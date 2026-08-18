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
    page_title="Peer Evaluation",
    page_icon="🎀",
    layout="centered",
)

st.markdown(
    """
    <style>
      :root {
        --pink-50: #fff7fa;
        --pink-100: #ffe9f1;
        --pink-200: #ffd4e3;
        --pink-400: #f58aae;
        --pink-500: #ee6f9c;
        --pink-600: #df5c8c;
        --ink: #3d3340;
        --muted: #837984;
        --line: #f1d9e2;
      }
      .stApp {
        background: linear-gradient(180deg, #fff9fb 0%, #ffffff 40%);
        color: var(--ink);
      }
      .block-container {
        max-width: 760px;
        padding-top: 4.4rem;
        padding-bottom: 4rem;
      }
      .student-hero { margin: 0 0 1.25rem 0; }
      .student-kicker {
        color: var(--pink-600);
        font-weight: 700;
        font-size: .78rem;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: .35rem;
      }
      .student-title {
        font-size: clamp(2rem, 6vw, 3rem);
        line-height: 1.05;
        font-weight: 800;
        letter-spacing: -.04em;
        color: #332d35;
        margin: 0 0 .55rem 0;
      }
      .student-subtitle {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.65;
        margin: 0;
      }
      .week-card {
        background: linear-gradient(135deg, #fff0f5, #fff8fb);
        border: 1px solid var(--pink-200);
        border-radius: 18px;
        padding: 1rem 1.15rem;
        margin: 1rem 0 1.35rem 0;
        color: #6e4d5d;
        box-shadow: 0 8px 24px rgba(205, 92, 137, .06);
      }
      .week-card strong { color: #b94772; }
      div[data-testid="stForm"] {
        background: rgba(255,255,255,.92);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1.35rem 1.35rem .75rem;
        box-shadow: 0 12px 36px rgba(120, 66, 88, .06);
      }
      div[data-baseweb="input"] > div,
      div[data-baseweb="textarea"] > div {
        border-radius: 14px !important;
        border-color: var(--line) !important;
        background: #fffafb !important;
      }
      div[data-baseweb="input"] > div:focus-within,
      div[data-baseweb="textarea"] > div:focus-within {
        border-color: var(--pink-400) !important;
        box-shadow: 0 0 0 1px var(--pink-400) !important;
      }
      /* Pink primary buttons */
      button[kind="primary"],
      button[kind="primaryFormSubmit"],
      div[data-testid="stFormSubmitButton"] button,
      button[data-testid="stBaseButton-primary"],
      button[data-testid="stBaseButton-primaryFormSubmit"] {
        background: linear-gradient(135deg, #ee6f9c, #df5c8c) !important;
        background-color: #ee6f9c !important;
        border: none !important;
        color: white !important;
        border-radius: 14px !important;
        min-height: 3rem !important;
        font-weight: 700 !important;
        box-shadow: 0 8px 20px rgba(223, 92, 140, .22) !important;
      }
      /* Pink primary button hover */
      button[kind="primary"]:hover,
      button[kind="primaryFormSubmit"]:hover,
      div[data-testid="stFormSubmitButton"] button:hover,
      button[data-testid="stBaseButton-primary"]:hover,
      button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
        background: linear-gradient(135deg, #f58aae, #ee6f9c) !important;
        background-color: #ee6f9c !important;
        border: none !important;
        color: white !important;
        transform: translateY(-1px);
        box-shadow: 0 10px 24px rgba(223, 92, 140, .28) !important;
      }
      div[data-testid="stMetric"] {
        background: #fffafb;
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 12px;
      }
      .peer-card {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 1.15rem 1.15rem .5rem;
        margin: 14px 0 20px 0;
        box-shadow: 0 10px 28px rgba(120, 66, 88, .05);
      }
      .small-note {opacity: .72; font-size: .92rem;}
      .instruction-card {
        background: #fff6f9;
        border-left: 4px solid var(--pink-400);
        border-radius: 14px;
        padding: .9rem 1rem;
        margin: 1rem 0 1.25rem;
        color: #6f5964;
        line-height: 1.6;
      }
      .success-card {
        text-align: center;
        background: linear-gradient(145deg, #fff4f8, #ffffff);
        border: 1px solid var(--pink-200);
        border-radius: 24px;
        padding: 2rem 1.4rem;
        margin: 1.25rem 0;
        box-shadow: 0 16px 36px rgba(205, 92, 137, .09);
      }
      .success-icon {
        width: 54px;
        height: 54px;
        margin: 0 auto .85rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f8cddd;
        color: #a63f67;
        font-size: 1.55rem;
        font-weight: 900;
      }
      .success-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #493943;
        margin-bottom: .35rem;
      }
      .success-copy {
        color: var(--muted);
        font-size: .96rem;
      }
      div[data-testid="stAlert"] { border-radius: 16px; }
      @media (max-width: 640px) {
        .block-container { padding-top: 3.4rem; }
        .student-title { font-size: 2.15rem; }
        div[data-testid="stForm"] { padding: 1rem 1rem .55rem; }
        .peer-card { padding: 1rem 1rem .4rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# Student roster sheet headers
ROSTER_HEADERS = ["Group", "Student ID", "Name", "Department"]

# Headers for the weekly evaluation sheets
# Example: sheet name = 2026-08-17 (Monday of the corresponding week)
WEEKLY_HEADERS = [
    "Student ID",
    "Evaluator Name",
    "Group",
    "Teammate ID",
    "Teammate Name",
    "Score",
    "Comment",
    "Attendance",
]

# Legacy headers are accepted for backward compatibility.
LEGACY_WEEKLY_HEADERS = [
    "\ud559\ubc88",
    "\uc774\ub984",
    "\uc870",
    "\uc870\uc6d0 \ud559\ubc88",
    "\uc870\uc6d0",
    "\uc810\uc218",
    "comment",
]
ROSTER_HEADER_ALIASES = {
    "Group": ["Group", "\uc870"],
    "Student ID": ["Student ID", "\ud559\ubc88"],
    "Name": ["Name", "\uc774\ub984"],
    "Department": ["Department", "\ud559\uacfc"],
}

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
        suffix = "  ← Current week" if current_week and sheet_name == current_week else ""
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
    """Create the current week's tab and migrate legacy headers if needed."""
    ws = get_or_create_worksheet(week_sheet, rows=1000, cols=len(WEEKLY_HEADERS) + 2)
    first_row = ws.row_values(1)

    if not first_row:
        ws.append_row(WEEKLY_HEADERS, value_input_option="RAW")
        return ws

    if first_row[: len(WEEKLY_HEADERS)] == WEEKLY_HEADERS:
        return ws

    if first_row[: len(LEGACY_WEEKLY_HEADERS)] == LEGACY_WEEKLY_HEADERS:
        ws.update("A1:H1", [WEEKLY_HEADERS], value_input_option="RAW")
        return ws

    raise RuntimeError(
        f"The header of the '{week_sheet}' sheet does not match the expected format. "
        f"Please set the first row to {WEEKLY_HEADERS}."
    )

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

    header = [str(x).strip() for x in values[0]]
    rows = values[1:]
    raw = pd.DataFrame(rows, columns=header)

    mapped = pd.DataFrame()
    for english_col, aliases in ROSTER_HEADER_ALIASES.items():
        source_col = next((alias for alias in aliases if alias in raw.columns), None)
        mapped[english_col] = raw[source_col] if source_col else ""

    for col in ROSTER_HEADERS:
        mapped[col] = mapped[col].astype(str).str.strip()

    mapped = mapped[
        (mapped["Student ID"] != "")
        & (mapped["Name"] != "")
        & (mapped["Group"] != "")
    ]
    return mapped.reset_index(drop=True)

def read_week_evaluations(week_sheet: str) -> pd.DataFrame:
    if not worksheet_exists(week_sheet):
        return pd.DataFrame(columns=WEEKLY_HEADERS)

    ws = open_spreadsheet().worksheet(week_sheet)
    values = ws.get_all_values()
    if not values:
        return pd.DataFrame(columns=WEEKLY_HEADERS)

    header = values[0]

    if header[: len(LEGACY_WEEKLY_HEADERS)] == LEGACY_WEEKLY_HEADERS:
        ws.update("A1:H1", [WEEKLY_HEADERS], value_input_option="RAW")
        header = WEEKLY_HEADERS

    if header[: len(WEEKLY_HEADERS)] != WEEKLY_HEADERS:
        raise RuntimeError(
            f"The header of the '{week_sheet}' sheet does not match the expected format. "
            f"Please set the first row to {WEEKLY_HEADERS}."
        )

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
    raw = pd.read_excel(uploaded_file, sheet_name=sheet, dtype=str)
    raw.columns = [str(c).strip() for c in raw.columns]

    df = pd.DataFrame()
    missing = []

    for english_col, aliases in ROSTER_HEADER_ALIASES.items():
        source_col = next((alias for alias in aliases if alias in raw.columns), None)
        if source_col is None:
            if english_col == "Department":
                df[english_col] = ""
            else:
                missing.append(english_col)
        else:
            df[english_col] = raw[source_col]

    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    for col in ROSTER_HEADERS:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str).str.strip()

    df = df[
        (df["Group"] != "")
        & (df["Student ID"] != "")
        & (df["Name"] != "")
    ]

    df["Student ID"] = df["Student ID"].str.replace(r"\.0$", "", regex=True)
    df["Group"] = df["Group"].str.replace(r"\.0$", "", regex=True)

    if df.empty:
        raise ValueError("No valid student rows were found.")

    if df["Student ID"].duplicated().any():
        dup = df.loc[df["Student ID"].duplicated(keep=False), "Student ID"].tolist()
        raise ValueError("Duplicate Student IDs found: " + ", ".join(sorted(set(dup))))

    small_groups = df.groupby("Group").size()
    small_groups = small_groups[small_groups < 2]
    if not small_groups.empty:
        raise ValueError(
            "The following groups contain only one student: "
            + ", ".join(map(str, small_groups.index))
        )

    return df.sort_values(["Group", "Name", "Student ID"]).reset_index(drop=True)

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
    return str(evaluator_id) in set(df["Student ID"].astype(str).str.strip())


def append_evaluation_rows(
    student: pd.Series,
    targets: pd.DataFrame,
    scores: dict,
    comments: dict,
    attendance: dict,
) -> None:
    week_sheet, _ = current_week_context()
    ws = ensure_week_sheet(week_sheet)

    if evaluator_has_submitted(str(student["Student ID"]), week_sheet):
        raise ValueError("You have already submitted this week's peer evaluation.")

    rows = []
    for idx, (_, target) in enumerate(targets.iterrows()):
        target_id = str(target["Student ID"])
        rows.append(
            [
                str(student["Student ID"]),
                str(student["Name"]) if idx == 0 else "",
                str(student["Group"]),
                target_id,
                str(target["Name"]),
                int(scores[target_id]),
                str(comments.get(target_id, "")).strip(),
                str(attendance.get(target_id, "")),
            ]
        )

    ws.append_rows(rows, value_input_option="RAW")

def make_result_excel(roster: pd.DataFrame, week_df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    work = week_df.copy()

    if not work.empty:
        work["Score"] = pd.to_numeric(work["Score"], errors="coerce")
        summary = (
            work.groupby(["Teammate ID", "Teammate Name", "Group"], as_index=False)
            .agg(
                Evaluations=("Score", "count"),
                Average=("Score", "mean"),
                Minimum=("Score", "min"),
                Maximum=("Score", "max"),
            )
            .rename(columns={"Teammate ID": "Student ID", "Teammate Name": "Name"})
        )
        summary["Average"] = summary["Average"].round(2)
        submitted = set(work["Student ID"].astype(str))
    else:
        summary = pd.DataFrame(
            columns=["Student ID", "Name", "Group", "Evaluations", "Average", "Minimum", "Maximum"]
        )
        submitted = set()

    missing = roster[~roster["Student ID"].astype(str).isin(submitted)].copy()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        summary.to_excel(writer, sheet_name="Student Summary", index=False)
        work.to_excel(writer, sheet_name="Raw Evaluations", index=False)
        missing.to_excel(writer, sheet_name="Missing Submissions", index=False)
        roster.to_excel(writer, sheet_name="Student Roster", index=False)

        for sheet_name in ["Student Summary", "Raw Evaluations", "Missing Submissions", "Student Roster"]:
            worksheet = writer.sheets[sheet_name]
            worksheet.freeze_panes(1, 0)
            worksheet.autofilter(0, 0, max(0, worksheet.dim_rowmax), max(0, worksheet.dim_colmax))
            worksheet.set_column(0, max(0, worksheet.dim_colmax), 16)

    return output.getvalue()

def make_all_weeks_excel(roster: pd.DataFrame, week_names: list[str]) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        roster.to_excel(writer, sheet_name="Student Roster", index=False)
        writer.sheets["Student Roster"].freeze_panes(1, 0)
        writer.sheets["Student Roster"].set_column(0, max(0, writer.sheets["Student Roster"].dim_colmax), 16)

        for week_name in sorted(week_names):
            df = read_week_evaluations(week_name)
            # Excel worksheet names are limited to 31 characters, so YYYY-MM-DD is used as-is.
            df.to_excel(writer, sheet_name=week_name, index=False)
            ws = writer.sheets[week_name]
            ws.freeze_panes(1, 0)
            ws.set_column(0, max(0, ws.dim_colmax), 16)

    return output.getvalue()


def student_page():
    week_sheet, week_label = current_week_context()

    st.markdown(
        """
        <div class="student-hero">
          <div class="student-kicker">TEAM PROJECT</div>
          <div class="student-title">Peer Evaluation</div>
          <p class="student-subtitle">
            Please evaluate each teammate's contribution to the project.<br>
            Your responses will not be shared with other students and will only be reviewed by the course TAs.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""<div class="week-card">🎀 <strong>Evaluation period</strong> &nbsp; {week_label}<br>
        <span style="font-size:.9rem; opacity:.78;">A new evaluation week starts automatically every Monday at 00:00 KST.</span></div>""",
        unsafe_allow_html=True,
    )

    roster = read_roster()
    if roster.empty:
        st.info("The student roster has not been registered yet. Please contact the course TAs.")
        return

    if "student" not in st.session_state:
        st.session_state.student = None

    if st.session_state.student is None:
        with st.form("login_form"):
            student_id = st.text_input("Student ID", placeholder="e.g. 2023133001").strip()
            student_name = st.text_input("Name", placeholder="e.g. Jane Doe").strip()
            login = st.form_submit_button("Start Evaluation", type="primary", use_container_width=True)

        if login:
            matched = roster[
                (roster["Student ID"].astype(str) == student_id)
                & (roster["Name"].astype(str) == student_name)
            ]

            if matched.empty:
                st.error("The Student ID and Name do not match the registered roster.")
            else:
                student = matched.iloc[0].to_dict()
                if evaluator_has_submitted(student_id, week_sheet):
                    st.warning(
                        "You have already submitted this week's peer evaluation. "
                        "You can submit again starting next Monday."
                    )
                else:
                    st.session_state.student = student
                    st.rerun()
        return

    student = pd.Series(st.session_state.student)
    student_id = str(student["Student ID"])

    if evaluator_has_submitted(student_id, week_sheet):
        st.success("This week's peer evaluation has already been submitted. Thank you.")
        if st.button("Return to Start"):
            st.session_state.student = None
            st.rerun()
        return

    targets = roster[
        (roster["Group"].astype(str) == str(student["Group"]))
        & (roster["Student ID"].astype(str) != student_id)
    ].copy()

    c1, c2, c3 = st.columns(3)
    c1.metric("Evaluator", str(student["Name"]))
    c2.metric("Student ID", student_id)
    c3.metric("Group", str(student["Group"]))

    st.markdown(
        '<div class="instruction-card">'
        'For each teammate, select their <strong>attendance status</strong> and rate their project contribution '
        'from <strong>1 (Very Low) to 5 (Very High)</strong>. Comments are optional.'
        '</div>',
        unsafe_allow_html=True,
    )

    scores = {}
    comments = {}
    attendance = {}

    for _, target in targets.iterrows():
        target_id = str(target["Student ID"])
        st.markdown('<div class="peer-card">', unsafe_allow_html=True)

        dept = f" · {target['Department']}" if str(target.get("Department", "")).strip() else ""
        st.subheader(f"{target['Name']}  ·  {target_id}{dept}")

        attendance[target_id] = st.radio(
            "Attendance",
            ["Present", "Absent"],
            index=None,
            horizontal=True,
            key=f"attendance_{student_id}_{target_id}",
        )

        selected = st.feedback("stars", key=f"score_{student_id}_{target_id}")
        scores[target_id] = None if selected is None else selected + 1
        st.caption("★ 1 point  ·  ★★★★★ 5 points")

        comments[target_id] = st.text_area(
            "Comment",
            key=f"comment_{student_id}_{target_id}",
            placeholder="Optional: comment on participation, assigned work, collaboration, communication, etc.",
            height=90,
        )

        st.markdown("</div>", unsafe_allow_html=True)

    agree = st.checkbox("I have reviewed the evaluation entries above.")

    if st.button("Submit Evaluation", type="primary", use_container_width=True, disabled=not agree):
        missing_attendance = [
            str(row["Name"])
            for _, row in targets.iterrows()
            if attendance.get(str(row["Student ID"])) is None
        ]

        missing_scores = [
            str(row["Name"])
            for _, row in targets.iterrows()
            if scores.get(str(row["Student ID"])) is None
        ]

        if missing_attendance:
            st.error("Attendance has not been selected for: " + ", ".join(missing_attendance))
        elif missing_scores:
            st.error("A score has not been selected for: " + ", ".join(missing_scores))
        else:
            try:
                append_evaluation_rows(student, targets, scores, comments, attendance)
            except ValueError as exc:
                st.warning(str(exc))
            except Exception as exc:
                st.error("An error occurred while saving the evaluation. Please contact the course TAs.")
                st.exception(exc)
            else:
                st.session_state.student = None
                st.toast("Evaluation submitted 🎀")
                st.markdown(
                    """
                    <div class="success-card">
                      <div class="success-icon">✓</div>
                      <div class="success-title">Evaluation Complete</div>
                      <div class="success-copy">Thank you for your response. You can submit a new evaluation next week.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if st.button("Change Evaluator Information"):
        st.session_state.student = None
        st.rerun()


def admin_login() -> bool:
    if st.session_state.get("admin_authenticated", False):
        return True

    password = st.text_input("Admin Password", type="password")
    if st.button("Admin Login", type="primary"):
        expected = str(st.secrets["ADMIN_PASSWORD"])
        if hmac.compare_digest(password, expected):
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False


def admin_page():
    st.title("Admin")

    if not admin_login():
        return

    if st.button("Log Out"):
        st.session_state.admin_authenticated = False
        st.rerun()

    roster = read_roster()

    st.subheader("1. Student Roster")

    if roster.empty:
        st.warning("No student roster is registered yet. Upload students.xlsx below.")
    else:
        group_counts = roster.groupby("Group").size().sort_index()
        st.success(
            f"{len(roster)} students across {roster['Group'].nunique()} groups are currently registered."
        )
        st.dataframe(roster, hide_index=True, use_container_width=True)
        st.caption(
            "Students per group: "
            + " · ".join(f"Group {g}: {n}" for g, n in group_counts.items())
        )

    uploaded = st.file_uploader(
        "Upload Student Roster Excel",
        type=["xlsx"],
        help=(
            "Required columns: Group, Student ID, Name / Optional column: Department. "
            "Legacy headers are also accepted."
        ),
    )

    if uploaded is not None:
        try:
            new_roster = normalize_uploaded_roster(uploaded)
        except Exception as exc:
            st.error(f"Could not read the roster file: {exc}")
        else:
            st.write("Roster Preview")
            st.dataframe(new_roster, hide_index=True, use_container_width=True)

            existing_weeks = list_week_sheets()
            if existing_weeks:
                st.error(
                    "The roster cannot be replaced because evaluation data already exists. "
                    "This protection prevents roster mismatches during the course."
                )
            elif st.button("Save This Roster to Google Sheets", type="primary"):
                save_roster(new_roster)
                st.success("The student roster has been saved.")
                st.rerun()

    st.divider()
    st.subheader("2. Weekly Submission Status and Results")

    if roster.empty:
        st.info("Please register the student roster first.")
        return

    current_week, current_week_label = current_week_context()
    available_weeks = list_week_sheets()

    if current_week not in available_weeks:
        available_weeks.append(current_week)

    available_weeks = sorted(available_weeks, reverse=True)

    selected_week = st.selectbox(
        "Evaluation Week",
        available_weeks,
        index=available_weeks.index(current_week),
        format_func=lambda w: week_display(w, current_week),
    )

    if selected_week == current_week:
        st.caption(
            f"Current evaluation period: {current_week_label} · "
            "A new date sheet starts automatically every Monday at 00:00 KST."
        )

    period_df = read_week_evaluations(selected_week)
    submitted_ids = set(period_df["Student ID"].astype(str)) if not period_df.empty else set()

    total = len(roster)
    submitted_count = len(submitted_ids)
    missing = roster[~roster["Student ID"].astype(str).isin(submitted_ids)].copy()

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Students", total)
    m2.metric("Submitted", submitted_count)
    m3.metric("Missing", len(missing))
    st.progress(submitted_count / total if total else 0)

    st.markdown("**Missing Submissions**")
    if missing.empty:
        st.success("All students have submitted.")
    else:
        st.dataframe(missing, hide_index=True, use_container_width=True)

    if not period_df.empty:
        work = period_df.copy()
        work["Score"] = pd.to_numeric(work["Score"], errors="coerce")

        summary = (
            work.groupby(["Teammate ID", "Teammate Name", "Group"], as_index=False)
            .agg(
                Evaluations=("Score", "count"),
                Average=("Score", "mean"),
                Minimum=("Score", "min"),
                Maximum=("Score", "max"),
            )
            .rename(columns={"Teammate ID": "Student ID", "Teammate Name": "Name"})
        )
        summary["Average"] = summary["Average"].round(2)

        st.markdown("**Student Evaluation Summary**")
        st.dataframe(
            summary.sort_values(["Group", "Name"]),
            hide_index=True,
            use_container_width=True,
        )

        st.markdown("**Raw Evaluations**")
        st.dataframe(work, hide_index=True, use_container_width=True)

    excel_bytes = make_result_excel(roster, period_df)
    st.download_button(
        "Download Selected Week as Excel",
        data=excel_bytes,
        file_name=(
            f"peer_evaluation_{selected_week}_"
            f"{datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d_%H%M')}.xlsx"
        ),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    real_weeks = list_week_sheets()
    if real_weeks:
        history_bytes = make_all_weeks_excel(roster, real_weeks)
        st.download_button(
            "Download All Weeks as Excel",
            data=history_bytes,
            file_name=(
                "peer_evaluation_all_weeks_"
                f"{datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d_%H%M')}.xlsx"
            ),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    if worksheet_exists("evaluations"):
        st.info(
            "The legacy 'evaluations' sheet is no longer used. "
            "If it contains only test data, you may delete it directly in Google Sheets."
        )

    if st.button("Reload Latest Data from Google Sheets"):
        st.rerun()


if not secret_ready():
    st.title("Peer Evaluation")
    st.error("Deployment setup has not been completed yet.")
    st.markdown(
        "The administrator must configure `SPREADSHEET_ID`, `ADMIN_PASSWORD`, and "
        "`[gcp_service_account]` in Streamlit Cloud **Secrets**."
    )
    st.stop()

page = st.sidebar.radio("Menu", ["Peer Evaluation", "Admin"])

try:
    if page == "Peer Evaluation":
        student_page()
    else:
        admin_page()
except gspread.exceptions.APIError as exc:
    st.error("A Google Sheets API error occurred. Check that the required Google APIs are enabled and that the spreadsheet is shared with the service account.")
    st.exception(exc)
except Exception as exc:
    st.error("There is a problem with the app configuration or data connection.")
    st.exception(exc)
