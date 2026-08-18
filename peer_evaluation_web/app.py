from __future__ import annotations

import hmac
import io
import re
from datetime import datetime, timedelta
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

# 학생 명단 시트 헤더
ROSTER_HEADERS = ["조", "학번", "이름", "학과"]

# 매주 생성되는 평가 시트의 헤더
# 예: 시트 이름 = 2026-08-17 (해당 주 월요일)
WEEKLY_HEADERS = ["학번", "이름", "조", "조원 학번", "조원", "점수", "comment"]

WEEK_SHEET_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def current_week_context(now: datetime | None = None) -> tuple[str, str]:
    """Return (sheet_name, human_label) for the KST Monday-Sunday week."""
    if now is None:
        now = datetime.now(ZoneInfo("Asia/Seoul"))
    elif now.tzinfo is None:
        now = now.replace(tzinfo=ZoneInfo("Asia/Seoul"))
    else:
        now = now.astimezone(ZoneInfo("Asia/Seoul"))

    monday = (now - timedelta(days=now.weekday())).date()
    sunday = monday + timedelta(days=6)
    sheet_name = monday.isoformat()  # Google Sheet tab: 2026-08-17
    label = f"{monday.strftime('%Y.%m.%d')} ~ {sunday.strftime('%Y.%m.%d')}"
    return sheet_name, label


def week_display(sheet_name: str, current_week: str | None = None) -> str:
    try:
        monday = datetime.fromisoformat(sheet_name).date()
        sunday = monday + timedelta(days=6)
        suffix = "  ← 이번 주" if current_week and sheet_name == current_week else ""
        return f"{monday.strftime('%Y.%m.%d')} ~ {sunday.strftime('%Y.%m.%d')}{suffix}"
    except Exception:
        return sheet_name


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


def worksheet_exists(title: str) -> bool:
    try:
        open_spreadsheet().worksheet(title)
        return True
    except gspread.WorksheetNotFound:
        return False


def ensure_week_sheet(week_sheet: str):
    """Create the current week's tab and header if needed."""
    ws = get_or_create_worksheet(week_sheet, rows=1000, cols=len(WEEKLY_HEADERS) + 2)
    first_row = ws.row_values(1)
    if not first_row:
        ws.append_row(WEEKLY_HEADERS, value_input_option="RAW")
    elif first_row[: len(WEEKLY_HEADERS)] != WEEKLY_HEADERS:
        raise RuntimeError(
            f"'{week_sheet}' 시트의 헤더가 프로그램 형식과 다릅니다. "
            f"첫 행을 {WEEKLY_HEADERS} 로 맞춰 주세요."
        )
    return ws


def list_week_sheets() -> list[str]:
    """Return weekly tab names such as 2026-08-17."""
    return sorted(
        [ws.title for ws in open_spreadsheet().worksheets() if WEEK_SHEET_RE.match(ws.title)],
        reverse=True,
    )


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


def read_week_evaluations(week_sheet: str) -> pd.DataFrame:
    if not worksheet_exists(week_sheet):
        return pd.DataFrame(columns=WEEKLY_HEADERS)

    ws = open_spreadsheet().worksheet(week_sheet)
    values = ws.get_all_values()
    if not values:
        return pd.DataFrame(columns=WEEKLY_HEADERS)

    header = values[0]
    if header[: len(WEEKLY_HEADERS)] != WEEKLY_HEADERS:
        raise RuntimeError(f"'{week_sheet}' 시트의 헤더가 프로그램 형식과 다릅니다.")

    rows = values[1:]
    normalized_rows = []
    for row in rows:
        row = list(row) + [""] * (len(WEEKLY_HEADERS) - len(row))
        normalized_rows.append(row[: len(WEEKLY_HEADERS)])

    if not normalized_rows:
        return pd.DataFrame(columns=WEEKLY_HEADERS)

    return pd.DataFrame(normalized_rows, columns=WEEKLY_HEADERS)


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


def evaluator_has_submitted(evaluator_id: str, week_sheet: str | None = None) -> bool:
    if week_sheet is None:
        week_sheet, _ = current_week_context()
    df = read_week_evaluations(week_sheet)
    if df.empty:
        return False
    return str(evaluator_id) in set(df["학번"].astype(str).str.strip())


def append_evaluation_rows(
    student: pd.Series,
    targets: pd.DataFrame,
    scores: dict,
    comments: dict,
) -> None:
    week_sheet, _ = current_week_context()
    ws = ensure_week_sheet(week_sheet)

    # 제출 직전 재확인: 같은 주차에 한 번만 제출 가능
    if evaluator_has_submitted(str(student["학번"]), week_sheet):
        raise ValueError("이번 주 조원 평가는 이미 제출했습니다.")

    rows = []
    for idx, (_, target) in enumerate(targets.iterrows()):
        target_id = str(target["학번"])
        rows.append(
            [
                str(student["학번"]),
                str(student["이름"]) if idx == 0 else "",  # 이름은 첫 행에만 표시
                str(student["조"]),
                target_id,
                str(target["이름"]),
                int(scores[target_id]),
                str(comments.get(target_id, "")).strip(),
            ]
        )

    ws.append_rows(rows, value_input_option="RAW")


def make_result_excel(roster: pd.DataFrame, week_df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    work = week_df.copy()

    if not work.empty:
        work["점수"] = pd.to_numeric(work["점수"], errors="coerce")
        summary = (
            work.groupby(["조원 학번", "조원", "조"], as_index=False)
            .agg(
                평가수=("점수", "count"),
                평균=("점수", "mean"),
                최저=("점수", "min"),
                최고=("점수", "max"),
            )
            .rename(columns={"조원 학번": "학번", "조원": "이름"})
        )
        summary["평균"] = summary["평균"].round(2)
        submitted = set(work["학번"].astype(str))
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


def make_all_weeks_excel(roster: pd.DataFrame, week_names: list[str]) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        roster.to_excel(writer, sheet_name="학생 명단", index=False)
        writer.sheets["학생 명단"].freeze_panes(1, 0)
        writer.sheets["학생 명단"].set_column(0, max(0, writer.sheets["학생 명단"].dim_colmax), 16)

        for week_name in sorted(week_names):
            df = read_week_evaluations(week_name)
            # Excel 탭명은 31자 제한이 있으므로 YYYY-MM-DD 그대로 사용
            df.to_excel(writer, sheet_name=week_name, index=False)
            ws = writer.sheets[week_name]
            ws.freeze_panes(1, 0)
            ws.set_column(0, max(0, ws.dim_colmax), 16)

    return output.getvalue()


def student_page():
    st.title("팀 프로젝트 조원 평가")
    week_sheet, week_label = current_week_context()
    st.caption("평가 내용은 다른 학생에게 공개되지 않으며 담당자만 확인할 수 있습니다.")
    st.info(f"📅 **이번 평가 기간:** {week_label} (월요일 00:00에 새 주차로 자동 전환)")

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
                if evaluator_has_submitted(student_id, week_sheet):
                    st.warning("이번 주 조원 평가를 이미 제출했습니다. 다음 주 월요일부터 다시 평가할 수 있습니다.")
                else:
                    st.session_state.student = student
                    st.rerun()
        return

    student = pd.Series(st.session_state.student)
    student_id = str(student["학번"])

    if evaluator_has_submitted(student_id, week_sheet):
        st.success("이번 주 조원 평가가 이미 제출되었습니다. 감사합니다.")
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
            existing_weeks = list_week_sheets()
            if existing_weeks:
                st.error("이미 평가 데이터가 존재하므로 명단을 교체할 수 없습니다. 수업 중 명단 불일치를 방지하기 위한 보호 기능입니다.")
            elif st.button("이 명단을 Google Sheet에 저장", type="primary"):
                save_roster(new_roster)
                st.success("학생 명단을 저장했습니다.")
                st.rerun()

    st.divider()
    st.subheader("2. 주차별 제출 현황 및 결과")
    if roster.empty:
        st.info("학생 명단을 먼저 등록하세요.")
        return

    current_week, current_week_label = current_week_context()
    available_weeks = list_week_sheets()
    if current_week not in available_weeks:
        available_weeks.append(current_week)
    available_weeks = sorted(available_weeks, reverse=True)

    selected_week = st.selectbox(
        "조회할 평가 주차",
        available_weeks,
        index=available_weeks.index(current_week),
        format_func=lambda w: week_display(w, current_week),
    )

    if selected_week == current_week:
        st.caption(f"현재 평가 기간: {current_week_label} · 매주 월요일 00:00(한국시간)에 새 날짜 시트가 자동으로 시작됩니다.")

    period_df = read_week_evaluations(selected_week)
    submitted_ids = set(period_df["학번"].astype(str)) if not period_df.empty else set()

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

    if not period_df.empty:
        work = period_df.copy()
        work["점수"] = pd.to_numeric(work["점수"], errors="coerce")
        summary = (
            work.groupby(["조원 학번", "조원", "조"], as_index=False)
            .agg(
                평가수=("점수", "count"),
                평균=("점수", "mean"),
                최저=("점수", "min"),
                최고=("점수", "max"),
            )
            .rename(columns={"조원 학번": "학번", "조원": "이름"})
        )
        summary["평균"] = summary["평균"].round(2)

        st.markdown("**학생별 평가 요약**")
        st.dataframe(summary.sort_values(["조", "이름"]), hide_index=True, use_container_width=True)

        st.markdown("**원본 평가**")
        st.dataframe(work, hide_index=True, use_container_width=True)

    excel_bytes = make_result_excel(roster, period_df)
    st.download_button(
        "선택 주차 결과 Excel 다운로드",
        data=excel_bytes,
        file_name=f"peer_evaluation_{selected_week}_{datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    real_weeks = list_week_sheets()
    if real_weeks:
        history_bytes = make_all_weeks_excel(roster, real_weeks)
        st.download_button(
            "전체 주차 결과 Excel 다운로드",
            data=history_bytes,
            file_name=f"peer_evaluation_all_weeks_{datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # 이전 버전의 evaluations 시트는 새 저장 방식에서는 사용하지 않음.
    if worksheet_exists("evaluations"):
        st.info("기존 'evaluations' 시트는 새 버전에서는 사용하지 않습니다. 테스트 데이터라면 Google Sheet에서 직접 삭제해도 됩니다.")

    if st.button("Google Sheet에서 최신 데이터 다시 불러오기"):
        st.rerun()


if not secret_ready():
    st.title("팀 프로젝트 조원 평가")
    st.error("배포 설정이 아직 완료되지 않았습니다.")
    st.markdown(
        "관리자는 Streamlit Cloud의 **Secrets**에 `SPREADSHEET_ID`, `ADMIN_PASSWORD`, "
        "`[gcp_service_account]` 정보를 등록해야 합니다."
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
