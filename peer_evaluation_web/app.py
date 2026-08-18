from __future__ import annotations

import hmac
import io
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


st.set_page_config(
    page_title="팀 프로젝트 조원 평가",
    page_icon="📝",
    layout="centered",
)

st.markdown(
    """
    <style>
      .block-container {max-width: 860px; padding-top: 2rem; padding-bottom: 4rem;}
      div[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.25); border-radius: 12px; padding: 12px;}
      .peer-card {border: 1px solid rgba(128,128,128,.28); border-radius: 14px; padding: 18px 18px 8px 18px; margin: 12px 0 18px 0;}
      .small-note {opacity: .75; font-size: .92rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

ROSTER_HEADERS = ["조", "학번", "이름", "학과"]
EVAL_HEADERS = [
    "submission_id",
    "submitted_at",
    "evaluator_id",
    "evaluator_name",
    "group",
    "target_id",
    "target_name",
    "score",
    "comment",
]


def secret_ready() -> bool:
    try:
        _ = st.secrets["SPREADSHEET_ID"]
        _ = st.secrets["ADMIN_PASSWORD"]
        _ = st.secrets["gcp_service_account"]
        return True
    except Exception:
        return False


@st.cache_resource(show_spinner=False)
def open_spreadsheet():
    info = dict(st.secrets["gcp_service_account"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_info(info, scopes=scopes)
    client = gspread.authorize(credentials)
    return client.open_by_key(st.secrets["SPREADSHEET_ID"])


def get_or_create_worksheet(title: str, rows: int, cols: int):
    spreadsheet = open_spreadsheet()
    try:
        return spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)


def ensure_eval_sheet():
    ws = get_or_create_worksheet("evaluations", rows=1000, cols=len(EVAL_HEADERS) + 2)
    first_row = ws.row_values(1)
    if not first_row:
        ws.append_row(EVAL_HEADERS, value_input_option="RAW")
    elif first_row[: len(EVAL_HEADERS)] != EVAL_HEADERS:
        raise RuntimeError("evaluations 시트의 헤더가 프로그램 형식과 다릅니다.")
    return ws


def read_roster() -> pd.DataFrame:
    ws = get_or_create_worksheet("students", rows=200, cols=8)
    values = ws.get_all_values()
    if not values:
        return pd.DataFrame(columns=ROSTER_HEADERS)
    header = values[0]
    if not all(col in header for col in ["조", "학번", "이름"]):
        return pd.DataFrame(columns=ROSTER_HEADERS)
    rows = values[1:]
    df = pd.DataFrame(rows, columns=header)
    for col in ROSTER_HEADERS:
        if col not in df.columns:
            df[col] = ""
    df = df[ROSTER_HEADERS].copy()
    for col in ROSTER_HEADERS:
        df[col] = df[col].astype(str).str.strip()
    df = df[(df["학번"] != "") & (df["이름"] != "") & (df["조"] != "")]
    return df.reset_index(drop=True)


def read_evaluations() -> pd.DataFrame:
    ws = ensure_eval_sheet()
    records = ws.get_all_records(expected_headers=EVAL_HEADERS)
    if not records:
        return pd.DataFrame(columns=EVAL_HEADERS)
    df = pd.DataFrame(records)
    for col in EVAL_HEADERS:
        if col not in df.columns:
            df[col] = ""
    return df[EVAL_HEADERS]


def normalize_uploaded_roster(uploaded_file) -> pd.DataFrame:
    xls = pd.ExcelFile(uploaded_file)
    sheet = "students" if "students" in xls.sheet_names else xls.sheet_names[0]
    df = pd.read_excel(uploaded_file, sheet_name=sheet, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]

    required = ["조", "학번", "이름"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError("필수 열이 없습니다: " + ", ".join(missing))

    if "학과" not in df.columns:
        df["학과"] = ""

    df = df[ROSTER_HEADERS].copy()
    for col in ROSTER_HEADERS:
        df[col] = df[col].fillna("").astype(str).str.strip()
    df = df[(df["조"] != "") & (df["학번"] != "") & (df["이름"] != "")]

    # Excel에서 숫자 학번/조가 1234.0처럼 읽힌 경우만 정리
    df["학번"] = df["학번"].str.replace(r"\.0$", "", regex=True)
    df["조"] = df["조"].str.replace(r"\.0$", "", regex=True)

    if df.empty:
        raise ValueError("유효한 학생 행이 없습니다.")
    if df["학번"].duplicated().any():
        dup = df.loc[df["학번"].duplicated(keep=False), "학번"].tolist()
        raise ValueError("중복 학번이 있습니다: " + ", ".join(sorted(set(dup))))

    small_groups = df.groupby("조").size()
    small_groups = small_groups[small_groups < 2]
    if not small_groups.empty:
        raise ValueError("조원이 1명뿐인 조가 있습니다: " + ", ".join(map(str, small_groups.index)))

    return df.sort_values(["조", "이름", "학번"]).reset_index(drop=True)


def save_roster(df: pd.DataFrame) -> None:
    ws = get_or_create_worksheet("students", rows=max(200, len(df) + 20), cols=8)
    ws.clear()
    values = [ROSTER_HEADERS] + df[ROSTER_HEADERS].fillna("").astype(str).values.tolist()
    ws.append_rows(values, value_input_option="RAW")


def evaluator_has_submitted(evaluator_id: str, eval_df: pd.DataFrame | None = None) -> bool:
    if eval_df is None:
        eval_df = read_evaluations()
    if eval_df.empty:
        return False
    return evaluator_id in set(eval_df["evaluator_id"].astype(str))


def append_evaluation_rows(student: pd.Series, targets: pd.DataFrame, scores: dict, comments: dict) -> None:
    ws = ensure_eval_sheet()
    # 제출 직전 다시 확인하여 일반적인 중복 제출을 방지
    fresh = read_evaluations()
    if evaluator_has_submitted(str(student["학번"]), fresh):
        raise ValueError("이미 제출된 평가입니다.")

    submission_id = str(uuid.uuid4())
    submitted_at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    rows = []
    for _, target in targets.iterrows():
        target_id = str(target["학번"])
        rows.append(
            [
                submission_id,
                submitted_at,
                str(student["학번"]),
                str(student["이름"]),
                str(student["조"]),
                target_id,
                str(target["이름"]),
                int(scores[target_id]),
                str(comments.get(target_id, "")).strip(),
            ]
        )
    ws.append_rows(rows, value_input_option="RAW")


def make_result_excel(roster: pd.DataFrame, eval_df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    work = eval_df.copy()
    if not work.empty:
        work["score"] = pd.to_numeric(work["score"], errors="coerce")
        summary = (
            work.groupby(["target_id", "target_name", "group"], as_index=False)["score"]
            .agg(["count", "mean", "min", "max"])
            .reset_index()
            .rename(
                columns={
                    "target_id": "학번",
                    "target_name": "이름",
                    "group": "조",
                    "count": "평가수",
                    "mean": "평균",
                    "min": "최저",
                    "max": "최고",
                }
            )
        )
        summary["평균"] = summary["평균"].round(2)
        submitted = set(work["evaluator_id"].astype(str))
    else:
        summary = pd.DataFrame(columns=["학번", "이름", "조", "평가수", "평균", "최저", "최고"])
        submitted = set()

    missing = roster[~roster["학번"].astype(str).isin(submitted)].copy()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        summary.to_excel(writer, sheet_name="학생별 요약", index=False)
        work.to_excel(writer, sheet_name="원본 평가", index=False)
        missing.to_excel(writer, sheet_name="미제출자", index=False)
        roster.to_excel(writer, sheet_name="학생 명단", index=False)

        for sheet_name in ["학생별 요약", "원본 평가", "미제출자", "학생 명단"]:
            worksheet = writer.sheets[sheet_name]
            worksheet.freeze_panes(1, 0)
            worksheet.autofilter(0, 0, max(0, worksheet.dim_rowmax), max(0, worksheet.dim_colmax))
            worksheet.set_column(0, max(0, worksheet.dim_colmax), 16)

    return output.getvalue()


def student_page():
    st.title("팀 프로젝트 조원 평가")
    st.caption("평가 내용은 다른 학생에게 공개되지 않으며 담당자만 확인할 수 있습니다.")

    roster = read_roster()
    if roster.empty:
        st.info("아직 학생 명단이 등록되지 않았습니다. 담당자에게 문의해 주세요.")
        return

    if "student" not in st.session_state:
        st.session_state.student = None

    if st.session_state.student is None:
        with st.form("login_form"):
            student_id = st.text_input("학번", placeholder="예: 2023133001").strip()
            student_name = st.text_input("이름", placeholder="예: 홍길동").strip()
            login = st.form_submit_button("평가 시작", type="primary", use_container_width=True)

        if login:
            matched = roster[
                (roster["학번"].astype(str) == student_id)
                & (roster["이름"].astype(str) == student_name)
            ]
            if matched.empty:
                st.error("학번과 이름이 학생 명단과 일치하지 않습니다.")
            else:
                student = matched.iloc[0].to_dict()
                if evaluator_has_submitted(student_id):
                    st.warning("이미 조원 평가를 제출했습니다. 중복 제출은 할 수 없습니다.")
                else:
                    st.session_state.student = student
                    st.rerun()
        return

    student = pd.Series(st.session_state.student)
    student_id = str(student["학번"])

    # 다른 브라우저/탭에서 방금 제출했을 수도 있으므로 재확인
    if evaluator_has_submitted(student_id):
        st.success("조원 평가가 이미 제출되었습니다. 감사합니다.")
        if st.button("처음 화면으로"):
            st.session_state.student = None
            st.rerun()
        return

    targets = roster[
        (roster["조"].astype(str) == str(student["조"]))
        & (roster["학번"].astype(str) != student_id)
    ].copy()

    c1, c2, c3 = st.columns(3)
    c1.metric("평가자", str(student["이름"]))
    c2.metric("학번", student_id)
    c3.metric("조", f"{student['조']}조")

    st.info("각 조원의 프로젝트 기여도를 **1점(매우 낮음) ~ 5점(매우 높음)**으로 평가해 주세요. 코멘트는 선택 사항입니다.")

    scores = {}
    comments = {}
    for _, target in targets.iterrows():
        target_id = str(target["학번"])
        st.markdown('<div class="peer-card">', unsafe_allow_html=True)
        dept = f" · {target['학과']}" if str(target.get("학과", "")).strip() else ""
        st.subheader(f"{target['이름']}  ·  {target_id}{dept}")
        selected = st.feedback("stars", key=f"score_{student_id}_{target_id}")
        scores[target_id] = None if selected is None else selected + 1
        st.caption("★ 1점  ·  ★★★★★ 5점")
        comments[target_id] = st.text_area(
            "코멘트",
            key=f"comment_{student_id}_{target_id}",
            placeholder="프로젝트 참여, 역할 수행, 협업 등에 대해 자유롭게 작성해 주세요.",
            height=90,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    agree = st.checkbox("입력한 평가 내용을 확인했습니다.")
    if st.button("평가 제출", type="primary", use_container_width=True, disabled=not agree):
        missing_scores = [
            str(row["이름"])
            for _, row in targets.iterrows()
            if scores.get(str(row["학번"])) is None
        ]
        if missing_scores:
            st.error("점수를 선택하지 않은 조원이 있습니다: " + ", ".join(missing_scores))
        else:
            try:
                append_evaluation_rows(student, targets, scores, comments)
            except ValueError as exc:
                st.warning(str(exc))
            except Exception as exc:
                st.error("평가 저장 중 오류가 발생했습니다. 담당자에게 문의해 주세요.")
                st.exception(exc)
            else:
                st.session_state.student = None
                st.success("평가가 정상적으로 제출되었습니다. 감사합니다.")
                st.balloons()

    if st.button("평가자 정보 다시 입력"):
        st.session_state.student = None
        st.rerun()


def admin_login() -> bool:
    if st.session_state.get("admin_authenticated", False):
        return True

    password = st.text_input("관리자 비밀번호", type="password")
    if st.button("관리자 로그인", type="primary"):
        expected = str(st.secrets["ADMIN_PASSWORD"])
        if hmac.compare_digest(password, expected):
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    return False


def admin_page():
    st.title("관리자")
    if not admin_login():
        return

    if st.button("관리자 로그아웃"):
        st.session_state.admin_authenticated = False
        st.rerun()

    roster = read_roster()
    eval_df = read_evaluations()

    st.subheader("1. 학생 명단")
    if roster.empty:
        st.warning("학생 명단이 아직 없습니다. 아래에서 students.xlsx를 등록하세요.")
    else:
        group_counts = roster.groupby("조").size().sort_index()
        st.success(f"현재 {len(roster)}명 / {roster['조'].nunique()}개 조가 등록되어 있습니다.")
        st.dataframe(roster, hide_index=True, use_container_width=True)
        st.caption("조별 인원: " + " · ".join(f"{g}조 {n}명" for g, n in group_counts.items()))

    uploaded = st.file_uploader("학생 명단 Excel 업로드", type=["xlsx"], help="필수 열: 조, 학번, 이름 / 선택 열: 학과")
    if uploaded is not None:
        try:
            new_roster = normalize_uploaded_roster(uploaded)
        except Exception as exc:
            st.error(f"명단 파일을 읽을 수 없습니다: {exc}")
        else:
            st.write("업로드할 명단 미리보기")
            st.dataframe(new_roster, hide_index=True, use_container_width=True)
            if not eval_df.empty:
                st.error("이미 평가 데이터가 존재하므로 명단을 교체할 수 없습니다. 수업 중 명단 불일치를 방지하기 위한 보호 기능입니다.")
            elif st.button("이 명단을 Google Sheet에 저장", type="primary"):
                save_roster(new_roster)
                st.success("학생 명단을 저장했습니다.")
                st.rerun()

    st.divider()
    st.subheader("2. 제출 현황 및 결과")
    if roster.empty:
        st.info("학생 명단을 먼저 등록하세요.")
        return

    if eval_df.empty:
        submitted_ids = set()
    else:
        submitted_ids = set(eval_df["evaluator_id"].astype(str))

    total = len(roster)
    submitted_count = len(submitted_ids)
    missing = roster[~roster["학번"].astype(str).isin(submitted_ids)].copy()

    m1, m2, m3 = st.columns(3)
    m1.metric("전체 학생", total)
    m2.metric("제출 완료", submitted_count)
    m3.metric("미제출", len(missing))
    st.progress(submitted_count / total if total else 0)

    st.markdown("**미제출자**")
    if missing.empty:
        st.success("모든 학생이 제출했습니다.")
    else:
        st.dataframe(missing, hide_index=True, use_container_width=True)

    if not eval_df.empty:
        work = eval_df.copy()
        work["score"] = pd.to_numeric(work["score"], errors="coerce")
        summary = (
            work.groupby(["target_id", "target_name", "group"], as_index=False)
            .agg(
                평가수=("score", "count"),
                평균=("score", "mean"),
                최저=("score", "min"),
                최고=("score", "max"),
            )
            .rename(columns={"target_id": "학번", "target_name": "이름", "group": "조"})
        )
        summary["평균"] = summary["평균"].round(2)

        st.markdown("**학생별 평가 요약**")
        st.dataframe(summary.sort_values(["조", "이름"]), hide_index=True, use_container_width=True)

        st.markdown("**원본 평가**")
        st.dataframe(work, hide_index=True, use_container_width=True)

    excel_bytes = make_result_excel(roster, eval_df)
    st.download_button(
        "전체 결과 Excel 다운로드",
        data=excel_bytes,
        file_name=f"peer_evaluation_results_{datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    if st.button("Google Sheet에서 최신 데이터 다시 불러오기"):
        st.rerun()


if not secret_ready():
    st.title("팀 프로젝트 조원 평가")
    st.error("배포 설정이 아직 완료되지 않았습니다.")
    st.markdown(
        "관리자는 Streamlit Cloud의 **Secrets**에 `SPREADSHEET_ID`, `ADMIN_PASSWORD`, "
        "`[gcp_service_account]` 정보를 등록해야 합니다. 자세한 내용은 함께 제공된 `README_KO.md`를 확인하세요."
    )
    st.stop()

page = st.sidebar.radio("메뉴", ["학생 평가", "관리자"])

try:
    if page == "학생 평가":
        student_page()
    else:
        admin_page()
except gspread.exceptions.APIError as exc:
    st.error("Google Sheet 연결 중 API 오류가 발생했습니다. Google API 활성화 및 Sheet 공유 권한을 확인하세요.")
    st.exception(exc)
except Exception as exc:
    st.error("앱 설정 또는 데이터 연결에 문제가 있습니다.")
    st.exception(exc)
