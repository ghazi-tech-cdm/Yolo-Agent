import json
import sqlite3
from datetime import datetime
from pathlib import Path
from collections import Counter

import streamlit as st
from PIL import Image

# =========================================================
# OPTIONAL YOLO IMPORT
# =========================================================

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="CID Investigation Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = Path("cid_investigation.db")


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            priority TEXT NOT NULL DEFAULT 'MEDIUM',
            location TEXT,
            lead TEXT,
            description TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            contact TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            person_id INTEGER,
            source_name TEXT NOT NULL,
            statement_type TEXT NOT NULL,
            statement TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE,
            FOREIGN KEY(person_id) REFERENCES persons(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            address TEXT,
            latitude REAL,
            longitude REAL,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            person_id INTEGER,
            location_id INTEGER,
            title TEXT NOT NULL,
            evidence_type TEXT NOT NULL,
            relevance TEXT NOT NULL DEFAULT 'MEDIUM',
            source TEXT,
            description TEXT,
            file_name TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE,
            FOREIGN KEY(person_id) REFERENCES persons(id) ON DELETE SET NULL,
            FOREIGN KEY(location_id) REFERENCES locations(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            person_id INTEGER,
            evidence_id INTEGER,
            relationship_type TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE,
            FOREIGN KEY(person_id) REFERENCES persons(id) ON DELETE SET NULL,
            FOREIGN KEY(evidence_id) REFERENCES evidence(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            detail TEXT,
            event_time TEXT NOT NULL,
            event_type TEXT DEFAULT 'GENERAL',
            FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE
        );
        """
    )

    conn.commit()
    conn.close()


init_db()


# =========================================================
# DATABASE HELPERS
# =========================================================

def execute(query, params=(), fetch=False, many=False):
    conn = get_db()

    try:
        cur = conn.cursor()

        if many:
            cur.executemany(query, params)
        else:
            cur.execute(query, params)

        if fetch:
            result = cur.fetchall()
        else:
            result = cur.lastrowid

        conn.commit()
        return result

    finally:
        conn.close()


def query_one(query, params=()):
    rows = execute(query, params, fetch=True)
    return rows[0] if rows else None


def query_all(query, params=()):
    return execute(query, params, fetch=True)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add_timeline(case_id, title, detail="", event_type="GENERAL"):
    execute(
        """
        INSERT INTO timeline
        (case_id, title, detail, event_time, event_type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            case_id,
            title,
            detail,
            now(),
            event_type,
        ),
    )


# =========================================================
# DEFAULT CASE
# =========================================================

def ensure_default_case():

    existing = query_one(
        "SELECT * FROM cases ORDER BY id LIMIT 1"
    )

    if existing:
        return

    case_id = execute(
        """
        INSERT INTO cases
        (case_number, title, status, priority, location, lead, description, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "CID-2026-001",
            "Warehouse Incident",
            "ACTIVE",
            "HIGH",
            "Industrial Area",
            "Investigation Unit A",
            "Initial investigation case.",
            now(),
        ),
    )

    add_timeline(
        case_id,
        "Case opened",
        "Initial case created in CID Investigation Intelligence.",
        "CASE",
    )


ensure_default_case()


# =========================================================
# SESSION STATE
# =========================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "active_case_id" not in st.session_state:

    first_case = query_one(
        "SELECT id FROM cases ORDER BY id LIMIT 1"
    )

    st.session_state.active_case_id = (
        first_case["id"] if first_case else None
    )


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

    .stApp {
        background:
            radial-gradient(circle at 15% 15%, rgba(0,229,255,.07), transparent 25%),
            radial-gradient(circle at 85% 20%, rgba(124,58,237,.08), transparent 25%),
            linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px),
            #070b12;

        background-size:
            auto,
            auto,
            36px 36px,
            36px 36px;

        color: #e8eef7;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
    }

    h1, h2, h3, h4, p, label, div {
        font-family: Inter, sans-serif;
    }

    .hero {
        border: 1px solid rgba(0,229,255,.18);
        background: linear-gradient(
            135deg,
            rgba(10,18,31,.94),
            rgba(10,14,25,.78)
        );
        border-radius: 22px;
        padding: 28px 32px;
        margin-bottom: 22px;
        box-shadow:
            0 0 45px rgba(0,229,255,.05),
            inset 0 1px rgba(255,255,255,.04);
    }

    .eyebrow {
        color: #00e5ff;
        font: 700 12px 'Space Mono', monospace;
        letter-spacing: 2px;
    }

    .hero h1 {
        font-size: 38px;
        margin: 8px 0;
        letter-spacing: -1.5px;
    }

    .hero p {
        color: #93a4ba;
        margin: 0;
        max-width: 900px;
        font-size: 15px;
    }

    .panel {
        border: 1px solid rgba(148,163,184,.13);
        background: rgba(10,15,24,.78);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 16px;
    }

    .panel-title {
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 12px;
    }

    .mono {
        font-family: 'Space Mono', monospace;
        color: #7dd3fc;
        font-size: 12px;
    }

    .metric {
        background: rgba(15,23,36,.92);
        border: 1px solid rgba(148,163,184,.12);
        border-radius: 14px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
    }

    .metric .value {
        font: 800 24px 'Space Mono', monospace;
        color: #eaf7ff;
    }

    .metric .label {
        color: #718198;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }

    .case-card {
        border: 1px solid rgba(0,229,255,.12);
        background: rgba(10,17,29,.82);
        border-radius: 16px;
        padding: 17px;
        margin-bottom: 12px;
    }

    .case-id {
        color: #00e5ff;
        font: 700 11px 'Space Mono', monospace;
        letter-spacing: 1px;
    }

    .case-title {
        font-size: 17px;
        font-weight: 700;
        margin: 5px 0;
    }

    .tag {
        display: inline-block;
        border: 1px solid rgba(125,211,252,.20);
        border-radius: 999px;
        padding: 4px 9px;
        color: #bae6fd;
        font: 11px 'Space Mono', monospace;
        margin-right: 5px;
        margin-top: 5px;
    }

    .status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: #a7f3d0;
        font-size: 12px;
        font-family: 'Space Mono', monospace;
    }

    .dot {
        width: 8px;
        height: 8px;
        background: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 12px #22c55e;
    }

    .timeline-line {
        border-left: 2px solid rgba(0,229,255,.25);
        padding-left: 18px;
        margin-left: 7px;
    }

    .timeline-item {
        margin-bottom: 22px;
        position: relative;
    }

    .timeline-item:before {
        content: '';
        position: absolute;
        left: -25px;
        top: 4px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #00e5ff;
        box-shadow: 0 0 12px rgba(0,229,255,.65);
    }

    [data-testid="stSidebar"] {
        background: #080d15;
        border-right: 1px solid rgba(148,163,184,.12);
    }

    [data-testid="stFileUploaderDropzone"] {
        background: rgba(8,15,25,.72);
        border: 1px dashed rgba(0,229,255,.35);
        border-radius: 16px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# LOGIN
# =========================================================

def login_screen():

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">CID / SECURE INVESTIGATION ENVIRONMENT</div>
            <h1>Investigation Intelligence</h1>
            <p>
                Connected case-management and investigation intelligence platform.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 1.2, 1])

    with center:

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown("### ◈ SECURE ACCESS")

        username = st.text_input(
            "Officer ID",
            placeholder="Enter officer ID",
        )

        password = st.text_input(
            "Access key",
            type="password",
            placeholder="Enter access key",
        )

        if st.button(
            "AUTHENTICATE",
            width="stretch",
        ):

            if username == "admin" and password == "cid2026":

                st.session_state.authenticated = True
                st.rerun()

            else:

                st.error("Authentication failed.")

        st.markdown(
            '<div class="mono">DEMO // admin / cid2026</div>',
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)


if not st.session_state.authenticated:

    login_screen()
    st.stop()


# =========================================================
# ACTIVE CASE
# =========================================================

case = query_one(
    "SELECT * FROM cases WHERE id = ?",
    (st.session_state.active_case_id,),
)

if case is None:

    case = query_one(
        "SELECT * FROM cases ORDER BY id LIMIT 1"
    )

    st.session_state.active_case_id = case["id"]


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ◈ CID COMMAND")

    st.markdown(
        '<div class="status"><span class="dot"></span> SYSTEM ONLINE</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    navigation = st.radio(
        "NAVIGATION",
        [
            "Command Center",
            "Case Files",
            "Persons / Suspects",
            "Statements",
            "Clues & Evidence",
            "Investigation Board",
            "Timeline",
            "Locations",
            "Image Intelligence",
            "Analytics",
            "Reports",
        ],
    )

    st.divider()

    st.markdown("**ACTIVE CASE**")

    cases = query_all(
        """
        SELECT id, case_number, title
        FROM cases
        ORDER BY id DESC
        """
    )

    case_map = {
        f"{c['case_number']} — {c['title']}": c["id"]
        for c in cases
    }

    labels = list(case_map.keys())

    current_label = next(
        (
            label
            for label, cid in case_map.items()
            if cid == st.session_state.active_case_id
        ),
        labels[0],
    )

    selected_label = st.selectbox(
        "Case",
        labels,
        index=labels.index(current_label),
        label_visibility="collapsed",
    )

    selected_id = case_map[selected_label]

    if selected_id != st.session_state.active_case_id:

        st.session_state.active_case_id = selected_id
        st.rerun()

    case = query_one(
        "SELECT * FROM cases WHERE id = ?",
        (st.session_state.active_case_id,),
    )

    st.markdown(
        f"""
        <div class="case-card">
            <div class="case-id">{case["case_number"]}</div>
            <div class="case-title">{case["title"]}</div>
            <span class="tag">{case["status"]}</span>
            <span class="tag">{case["priority"]}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        '<div class="mono">USER // CID ADMIN</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="mono">DATABASE // SQLITE</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "LOCK SYSTEM",
        width="stretch",
    ):

        st.session_state.authenticated = False
        st.rerun()


# =========================================================
# HERO
# =========================================================

st.markdown(
    f"""
    <div class="hero">
        <div class="eyebrow">CID / CONNECTED CASE INTELLIGENCE</div>
        <h1>{navigation}</h1>
        <p>
            Active case:
            <strong>{case["case_number"]}</strong>
            — {case["title"]}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# COMMAND CENTER
# =========================================================

if navigation == "Command Center":

    person_count = query_one(
        "SELECT COUNT(*) AS n FROM persons WHERE case_id = ?",
        (case["id"],)
    )["n"]

    statement_count = query_one(
        "SELECT COUNT(*) AS n FROM statements WHERE case_id = ?",
        (case["id"],)
    )["n"]

    evidence_count = query_one(
        "SELECT COUNT(*) AS n FROM evidence WHERE case_id = ?",
        (case["id"],)
    )["n"]

    location_count = query_one(
        "SELECT COUNT(*) AS n FROM locations WHERE case_id = ?",
        (case["id"],)
    )["n"]

    timeline_count = query_one(
        "SELECT COUNT(*) AS n FROM timeline WHERE case_id = ?",
        (case["id"],)
    )["n"]

    st.markdown("### OPERATIONAL OVERVIEW")

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        metric_card = lambda value, label: st.markdown(
            f"""
            <div class="metric">
                <div class="value">{value}</div>
                <div class="label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        metric_card(person_count, "Persons")

    with m2:
        metric_card(statement_count, "Statements")

    with m3:
        metric_card(evidence_count, "Evidence")

    with m4:
        metric_card(location_count, "Locations")

    with m5:
        metric_card(timeline_count, "Timeline events")

    st.write("")

    left, right = st.columns([1.5, 1])

    with left:

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown("### ACTIVE CASE")

        st.markdown(
            f"#### {case['title']}"
        )

        st.caption(case["description"])

        st.write(
            f"**Case:** `{case['case_number']}`"
        )

        st.write(
            f"**Location:** {case['location'] or 'Not specified'}"
        )

        st.write(
            f"**Lead:** {case['lead'] or 'Unassigned'}"
        )

        st.write(
            f"**Priority:** {case['priority']}"
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown("### LIVE CASE STATUS")

        st.markdown(
            f'<div class="mono">STATUS // {case["status"]}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="mono">PRIORITY // {case["priority"]}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="mono">PERSONS // {person_count}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="mono">EVIDENCE // {evidence_count}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="mono">EVENTS // {timeline_count}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# CASE FILES
# =========================================================

elif navigation == "Case Files":

    st.markdown("### CASE MANAGEMENT")

    with st.expander(
        "＋ CREATE NEW CASE",
        expanded=False,
    ):

        with st.form("new_case"):

            title = st.text_input("Case title")
            location = st.text_input("Primary location")

            priority = st.selectbox(
                "Priority",
                [
                    "LOW",
                    "MEDIUM",
                    "HIGH",
                    "CRITICAL",
                ],
            )

            lead = st.text_input("Investigation lead")

            description = st.text_area(
                "Case description"
            )

            submitted = st.form_submit_button(
                "CREATE CASE",
                width="stretch",
            )

            if submitted:

                if not title.strip():

                    st.error("Case title is required.")

                else:

                    last = query_one(
                        """
                        SELECT case_number
                        FROM cases
                        ORDER BY id DESC
                        LIMIT 1
                        """
                    )

                    number = 1

                    if last:

                        try:
                            number = (
                                int(
                                    last["case_number"].split("-")[-1]
                                ) + 1
                            )
                        except Exception:
                            number = 1

                    case_number = f"CID-2026-{number:03d}"

                    new_id = execute(
                        """
                        INSERT INTO cases
                        (
                            case_number,
                            title,
                            status,
                            priority,
                            location,
                            lead,
                            description,
                            created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            case_number,
                            title.strip(),
                            "ACTIVE",
                            priority,
                            location.strip(),
                            lead.strip(),
                            description.strip(),
                            now(),
                        ),
                    )

                    add_timeline(
                        new_id,
                        "Case created",
                        f"{case_number} — {title.strip()}",
                        "CASE",
                    )

                    st.session_state.active_case_id = new_id

                    st.success(
                        f"Case {case_number} created."
                    )

                    st.rerun()

    st.write("")

    all_cases = query_all(
        """
        SELECT *
        FROM cases
        ORDER BY id DESC
        """
    )

    for c in all_cases:

        with st.container(border=True):

            a, b, d = st.columns([3, 1, 1])

            with a:

                st.markdown(
                    f"#### {c['title']}"
                )

                st.markdown(
                    f"`{c['case_number']}` · "
                    f"{c['location'] or 'No location'} · "
                    f"{c['created_at']}"
                )

                st.caption(
                    c["description"] or "No description."
                )

            with b:

                st.metric(
                    "Priority",
                    c["priority"]
                )

            with d:

                if c["id"] == case["id"]:

                    st.success("ACTIVE")

                else:

                    if st.button(
                        "OPEN",
                        key=f"open_case_{c['id']}",
                        width="stretch",
                    ):

                        st.session_state.active_case_id = c["id"]
                        st.rerun()


# =========================================================
# PERSONS
# =========================================================

elif navigation == "Persons / Suspects":

    st.markdown("### PERSONS & SUBJECTS")

    with st.expander(
        "＋ ADD PERSON",
        expanded=False,
    ):

        with st.form("person_form"):

            name = st.text_input(
                "Name / identifier"
            )

            role = st.selectbox(
                "Classification",
                [
                    "Person of interest",
                    "Witness",
                    "Complainant",
                    "Suspect",
                    "Victim",
                    "Officer",
                    "Other",
                ],
            )

            contact = st.text_input(
                "Contact reference"
            )

            notes = st.text_area(
                "Notes"
            )

            submitted = st.form_submit_button(
                "ADD PERSON",
                width="stretch",
            )

            if submitted:

                if not name.strip():

                    st.error(
                        "Name / identifier is required."
                    )

                else:

                    person_id = execute(
                        """
                        INSERT INTO persons
                        (
                            case_id,
                            name,
                            role,
                            contact,
                            notes,
                            created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            case["id"],
                            name.strip(),
                            role,
                            contact.strip(),
                            notes.strip(),
                            now(),
                        ),
                    )

                    add_timeline(
                        case["id"],
                        "Person added",
                        f"{name.strip()} — {role}",
                        "PERSON",
                    )

                    st.success(
                        f"{name.strip()} added to the active case."
                    )

                    st.rerun()

    people = query_all(
        """
        SELECT *
        FROM persons
        WHERE case_id = ?
        ORDER BY id DESC
        """,
        (case["id"],)
    )

    if not people:

        st.info(
            "No persons are connected to this case yet."
        )

    else:

        for p in people:

            with st.container(border=True):

                a, b = st.columns([4, 1])

                with a:

                    st.markdown(
                        f"### {p['name']}"
                    )

                    st.markdown(
                        f"`{p['role']}`"
                    )

                    st.caption(
                        f"Contact: {p['contact'] or 'Not provided'}"
                    )

                    st.write(
                        p["notes"] or "No notes."
                    )

                with b:

                    statement_count = query_one(
                        """
                        SELECT COUNT(*) AS n
                        FROM statements
                        WHERE person_id = ?
                        """,
                        (p["id"],)
                    )["n"]

                    evidence_count = query_one(
                        """
                        SELECT COUNT(*) AS n
                        FROM evidence
                        WHERE person_id = ?
                        """,
                        (p["id"],)
                    )["n"]

                    st.metric(
                        "Statements",
                        statement_count
                    )

                    st.metric(
                        "Evidence links",
                        evidence_count
                    )


# =========================================================
# STATEMENTS
# =========================================================

elif navigation == "Statements":

    st.markdown("### CONNECTED STATEMENT REGISTER")

    people = query_all(
        """
        SELECT id, name, role
        FROM persons
        WHERE case_id = ?
        ORDER BY name
        """,
        (case["id"],)
    )

    person_options = {
        "Unlinked / external source": None
    }

    for p in people:
        person_options[
            f"{p['name']} — {p['role']}"
        ] = p["id"]

    with st.expander(
        "＋ RECORD STATEMENT",
        expanded=False,
    ):

        with st.form("statement_form"):

            selected_person = st.selectbox(
                "Related person",
                list(person_options.keys()),
            )

            source_name = st.text_input(
                "Source name / identifier"
            )

            statement_type = st.selectbox(
                "Statement type",
                [
                    "Witness",
                    "Complainant",
                    "Subject",
                    "Officer",
                    "Other",
                ],
            )

            statement = st.text_area(
                "Statement",
                height=180,
            )

            submitted = st.form_submit_button(
                "SAVE STATEMENT",
                width="stretch",
            )

            if submitted:

                if not source_name.strip():

                    st.error(
                        "Source name is required."
                    )

                elif not statement.strip():

                    st.error(
                        "Statement text is required."
                    )

                else:

                    person_id = person_options[
                        selected_person
                    ]

                    execute(
                        """
                        INSERT INTO statements
                        (
                            case_id,
                            person_id,
                            source_name,
                            statement_type,
                            statement,
                            created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            case["id"],
                            person_id,
                            source_name.strip(),
                            statement_type,
                            statement.strip(),
                            now(),
                        ),
                    )

                    add_timeline(
                        case["id"],
                        "Statement recorded",
                        f"{source_name.strip()} — {statement_type}",
                        "STATEMENT",
                    )

                    st.success(
                        "Statement connected to the case."
                    )

                    st.rerun()

    statements = query_all(
        """
        SELECT
            s.*,
            p.name AS person_name
        FROM statements s
        LEFT JOIN persons p
            ON s.person_id = p.id
        WHERE s.case_id = ?
        ORDER BY s.id DESC
        """,
        (case["id"],)
    )

    if not statements:

        st.info(
            "No statements recorded for this case."
        )

    else:

        for s in statements:

            with st.container(border=True):

                st.markdown(
                    f"### {s['source_name']}"
                )

                relation = (
                    s["person_name"]
                    if s["person_name"]
                    else "External / unlinked source"
                )

                st.caption(
                    f"{s['statement_type']} · "
                    f"Related person: {relation} · "
                    f"{s['created_at']}"
                )

                st.write(
                    s["statement"]
                )


# =========================================================
# LOCATIONS
# =========================================================

elif navigation == "Locations":

    st.markdown("### CONNECTED LOCATIONS")

    with st.expander(
        "＋ ADD LOCATION",
        expanded=False,
    ):

        with st.form("location_form"):

            name = st.text_input(
                "Location name"
            )

            address = st.text_input(
                "Address / description"
            )

            c1, c2 = st.columns(2)

            with c1:

                latitude = st.number_input(
                    "Latitude",
                    value=0.0,
                    format="%.6f",
                )

            with c2:

                longitude = st.number_input(
                    "Longitude",
                    value=0.0,
                    format="%.6f",
                )

            notes = st.text_area(
                "Location notes"
            )

            submitted = st.form_submit_button(
                "ADD LOCATION",
                width="stretch",
            )

            if submitted:

                if not name.strip():

                    st.error(
                        "Location name is required."
                    )

                else:

                    location_id = execute(
                        """
                        INSERT INTO locations
                        (
                            case_id,
                            name,
                            address,
                            latitude,
                            longitude,
                            notes,
                            created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            case["id"],
                            name.strip(),
                            address.strip(),
                            latitude if latitude != 0 else None,
                            longitude if longitude != 0 else None,
                            notes.strip(),
                            now(),
                        ),
                    )

                    add_timeline(
                        case["id"],
                        "Location added",
                        name.strip(),
                        "LOCATION",
                    )

                    st.success(
                        "Location connected to case."
                    )

                    st.rerun()

    locations = query_all(
        """
        SELECT *
        FROM locations
        WHERE case_id = ?
        ORDER BY id DESC
        """,
        (case["id"],)
    )

    if not locations:

        st.info(
            "No locations registered."
        )

    else:

        for loc in locations:

            with st.container(border=True):

                st.markdown(
                    f"### {loc['name']}"
                )

                st.caption(
                    loc["address"] or "No address recorded."
                )

                if loc["latitude"] is not None:

                    st.write(
                        f"Coordinates: "
                        f"{loc['latitude']}, "
                        f"{loc['longitude']}"
                    )

                st.write(
                    loc["notes"] or "No notes."
                )


# =========================================================
# EVIDENCE
# =========================================================

elif navigation == "Clues & Evidence":

    st.markdown("### CONNECTED EVIDENCE REGISTER")

    people = query_all(
        """
        SELECT id, name, role
        FROM persons
        WHERE case_id = ?
        ORDER BY name
        """,
        (case["id"],)
    )

    locations = query_all(
        """
        SELECT id, name
        FROM locations
        WHERE case_id = ?
        ORDER BY name
        """,
        (case["id"],)
    )

    person_options = {
        "No person linked": None
    }

    for p in people:

        person_options[
            f"{p['name']} — {p['role']}"
        ] = p["id"]

    location_options = {
        "No location linked": None
    }

    for loc in locations:

        location_options[
            loc["name"]
        ] = loc["id"]

    with st.expander(
        "＋ REGISTER EVIDENCE",
        expanded=False,
    ):

        with st.form("evidence_form"):

            title = st.text_input(
                "Evidence / clue title"
            )

            evidence_type = st.selectbox(
                "Evidence type",
                [
                    "Physical evidence",
                    "Digital evidence",
                    "CCTV / image",
                    "Document",
                    "Observation",
                    "Lead",
                    "Other",
                ],
            )

            relevance = st.selectbox(
                "Relevance",
                [
                    "LOW",
                    "MEDIUM",
                    "HIGH",
                    "CRITICAL",
                ],
            )

            source = st.text_input(
                "Source"
            )

            person_choice = st.selectbox(
                "Related person",
                list(person_options.keys()),
            )

            location_choice = st.selectbox(
                "Related location",
                list(location_options.keys()),
            )

            description = st.text_area(
                "Evidence details"
            )

            file_name = st.text_input(
                "File name / reference"
            )

            submitted = st.form_submit_button(
                "REGISTER EVIDENCE",
                width="stretch",
            )

            if submitted:

                if not title.strip():

                    st.error(
                        "Evidence title is required."
                    )

                else:

                    evidence_id = execute(
                        """
                        INSERT INTO evidence
                        (
                            case_id,
                            person_id,
                            location_id,
                            title,
                            evidence_type,
                            relevance,
                            source,
                            description,
                            file_name,
                            created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            case["id"],
                            person_options[person_choice],
                            location_options[location_choice],
                            title.strip(),
                            evidence_type,
                            relevance,
                            source.strip(),
                            description.strip(),
                            file_name.strip(),
                            now(),
                        ),
                    )

                    related = []

                    if person_options[person_choice]:
                        related.append(
                            f"person={person_choice}"
                        )

                    if location_options[location_choice]:
                        related.append(
                            f"location={location_choice}"
                        )

                    relation_text = (
                        ", ".join(related)
                        if related
                        else "no linked entities"
                    )

                    add_timeline(
                        case["id"],
                        "Evidence registered",
                        f"{title.strip()} ({relation_text})",
                        "EVIDENCE",
                    )

                    st.success(
                        "Evidence registered and linked."
                    )

                    st.rerun()

    evidence = query_all(
        """
        SELECT
            e.*,
            p.name AS person_name,
            l.name AS location_name
        FROM evidence e
        LEFT JOIN persons p
            ON e.person_id = p.id
        LEFT JOIN locations l
            ON e.location_id = l.id
        WHERE e.case_id = ?
        ORDER BY e.id DESC
        """,
        (case["id"],)
    )

    if not evidence:

        st.info(
            "No evidence has been registered."
        )

    else:

        for e in evidence:

            with st.container(border=True):

                a, b = st.columns([4, 1])

                with a:

                    st.markdown(
                        f"### {e['title']}"
                    )

                    st.caption(
                        f"{e['evidence_type']} · "
                        f"{e['created_at']}"
                    )

                    st.write(
                        f"**Person:** "
                        f"{e['person_name'] or 'Not linked'}"
                    )

                    st.write(
                        f"**Location:** "
                        f"{e['location_name'] or 'Not linked'}"
                    )

                    st.write(
                        f"**Source:** "
                        f"{e['source'] or 'Not specified'}"
                    )

                    st.write(
                        e["description"]
                        or "No description."
                    )

                    if e["file_name"]:

                        st.caption(
                            f"Reference: {e['file_name']}"
                        )

                with b:

                    st.metric(
                        "Relevance",
                        e["relevance"]
                    )


# =========================================================
# INVESTIGATION BOARD
# =========================================================

elif navigation == "Investigation Board":

    st.markdown("### INVESTIGATION RELATIONSHIP BOARD")

    people = query_all(
        """
        SELECT *
        FROM persons
        WHERE case_id = ?
        ORDER BY name
        """,
        (case["id"],)
    )

    evidence = query_all(
        """
        SELECT
            e.*,
            p.name AS person_name,
            l.name AS location_name
        FROM evidence e
        LEFT JOIN persons p
            ON e.person_id = p.id
        LEFT JOIN locations l
            ON e.location_id = l.id
        WHERE e.case_id = ?
        ORDER BY e.id DESC
        """,
        (case["id"],)
    )

    locations = query_all(
        """
        SELECT *
        FROM locations
        WHERE case_id = ?
        ORDER BY name
        """,
        (case["id"],)
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown("### PERSONS")

        if people:

            for p in people:

                st.markdown(
                    f'<span class="tag">{p["name"]}</span>',
                    unsafe_allow_html=True,
                )

        else:

            st.caption("No persons.")

        st.markdown("</div>", unsafe_allow_html=True)

    with c2:

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown("### EVIDENCE")

        if evidence:

            for e in evidence:

                st.markdown(
                    f'<span class="tag">{e["title"]}</span>',
                    unsafe_allow_html=True,
                )

        else:

            st.caption("No evidence.")

        st.markdown("</div>", unsafe_allow_html=True)

    with c3:

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown("### LOCATIONS")

        if locations:

            for loc in locations:

                st.markdown(
                    f'<span class="tag">{loc["name"]}</span>',
                    unsafe_allow_html=True,
                )

        else:

            st.caption("No locations.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### AUTOMATIC CONNECTIONS")

    if not evidence:

        st.info(
            "Add evidence linked to persons or locations "
            "to populate the relationship board."
        )

    else:

        for e in evidence:

            person = e["person_name"]
            location = e["location_name"]

            st.markdown(
                f"""
                <div class="case-card">
                    <div class="case-id">
                        EVIDENCE #{e["id"]}
                    </div>

                    <div class="case-title">
                        {e["title"]}
                    </div>

                    <div class="mono">
                        CASE → {case["case_number"]}
                    </div>

                    <div class="mono">
                        PERSON → {person or "NONE"}
                    </div>

                    <div class="mono">
                        LOCATION → {location or "NONE"}
                    </div>

                    <div class="mono">
                        TYPE → {e["evidence_type"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### CREATE PERSON ↔ EVIDENCE RELATION")

    if people and evidence:

        person_map = {
            f"{p['name']} — {p['role']}": p["id"]
            for p in people
        }

        evidence_map = {
            f"{e['title']} — #{e['id']}": e["id"]
            for e in evidence
        }

        with st.form("relationship_form"):

            person_label = st.selectbox(
                "Person",
                list(person_map.keys()),
            )

            evidence_label = st.selectbox(
                "Evidence",
                list(evidence_map.keys()),
            )

            relation = st.selectbox(
                "Relationship",
                [
                    "Associated with",
                    "Mentioned in",
                    "Observed with",
                    "Linked to",
                    "Source of",
                    "Other",
                ],
            )

            notes = st.text_area(
                "Relationship notes"
            )

            submitted = st.form_submit_button(
                "CREATE RELATION",
                width="stretch",
            )

            if submitted:

                execute(
                    """
                    INSERT INTO relationships
                    (
                        case_id,
                        person_id,
                        evidence_id,
                        relationship_type,
                        notes,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        case["id"],
                        person_map[person_label],
                        evidence_map[evidence_label],
                        relation,
                        notes.strip(),
                        now(),
                    ),
                )

                add_timeline(
                    case["id"],
                    "Relationship created",
                    f"{person_label} ↔ {evidence_label}",
                    "RELATIONSHIP",
                )

                st.success(
                    "Relationship saved."
                )

                st.rerun()

    relations = query_all(
        """
        SELECT
            r.*,
            p.name AS person_name,
            e.title AS evidence_title
        FROM relationships r
        LEFT JOIN persons p
            ON r.person_id = p.id
        LEFT JOIN evidence e
            ON r.evidence_id = e.id
        WHERE r.case_id = ?
        ORDER BY r.id DESC
        """,
        (case["id"],)
    )

    if relations:

        st.markdown("### SAVED RELATIONSHIPS")

        for r in relations:

            st.markdown(
                f"""
                <div class="case-card">
                    <strong>{r["person_name"] or "Unknown"}</strong>
                    →
                    <strong>{r["evidence_title"] or "Unknown evidence"}</strong>
                    <div class="muted">
                        {r["relationship_type"]}
                        ·
                        {r["notes"] or "No notes"}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# TIMELINE
# =========================================================

elif navigation == "Timeline":

    st.markdown("### CASE TIMELINE")

    with st.expander(
        "＋ ADD MANUAL EVENT",
        expanded=False,
    ):

        with st.form("manual_event"):

            title = st.text_input(
                "Event title"
            )

            detail = st.text_area(
                "Event detail"
            )

            event_type = st.selectbox(
                "Event type",
                [
                    "GENERAL",
                    "CASE",
                    "PERSON",
                    "STATEMENT",
                    "EVIDENCE",
                    "LOCATION",
                    "RELATIONSHIP",
                    "OTHER",
                ],
            )

            submitted = st.form_submit_button(
                "ADD EVENT",
                width="stretch",
            )

            if submitted:

                if not title.strip():

                    st.error(
                        "Event title is required."
                    )

                else:

                    add_timeline(
                        case["id"],
                        title.strip(),
                        detail.strip(),
                        event_type,
                    )

                    st.success(
                        "Timeline event added."
                    )

                    st.rerun()

    events = query_all(
        """
        SELECT *
        FROM timeline
        WHERE case_id = ?
        ORDER BY event_time DESC, id DESC
        """,
        (case["id"],)
    )

    if not events:

        st.info(
            "No timeline events."
        )

    else:

        st.markdown(
            '<div class="timeline-line">',
            unsafe_allow_html=True,
        )

        for event in events:

            st.markdown(
                f"""
                <div class="timeline-item">

                    <div class="mono">
                        {event["event_time"]}
                    </div>

                    <strong>
                        {event["title"]}
                    </strong>

                    <div class="muted">
                        {event["event_type"]}
                    </div>

                    <div>
                        {event["detail"] or ""}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


# =========================================================
# IMAGE INTELLIGENCE
# =========================================================

elif navigation == "Image Intelligence":

    st.markdown("### IMAGE INTELLIGENCE")

    st.warning(
        "YOLO performs object detection. A detected 'person' "
        "is not automatically identified as a specific individual."
    )

    if YOLO is None:

        st.error(
            "Ultralytics is not installed. "
            "Check requirements.txt."
        )

    else:

        confidence = st.slider(
            "Detection confidence",
            0.10,
            0.95,
            0.35,
            0.05,
        )

        uploaded = st.file_uploader(
            "Upload investigation image",
            type=[
                "jpg",
                "jpeg",
                "png",
            ],
        )

        if uploaded is None:

            st.markdown(
                """
                <div class="panel" style="text-align:center;padding:50px">
                    <div class="eyebrow">
                        IMAGE AI
                    </div>

                    <h2>
                        WAITING FOR IMAGE
                    </h2>

                    <p class="muted">
                        Upload an image to run object detection.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            @st.cache_resource
            def load_yolo():

                return YOLO("yolov8n.pt")

            with st.spinner(
                "Loading YOLO model..."
            ):

                model = load_yolo()

            image = Image.open(
                uploaded
            ).convert("RGB")

            with st.spinner(
                "Running image intelligence..."
            ):

                results = model(
                    image,
                    conf=confidence,
                    verbose=False,
                )

            result = results[0]

            plotted = result.plot()

            plotted_rgb = plotted[:, :, ::-1]

            result_image = Image.fromarray(
                plotted_rgb
            )

            boxes = result.boxes

            count = len(boxes)

            classes = [
                model.names[int(box.cls[0])]
                for box in boxes
            ]

            confidences = [
                float(box.conf[0])
                for box in boxes
            ]

            counts = Counter(
                classes
            )

            average_confidence = (
                sum(confidences) / count * 100
                if count
                else 0
            )

            m1, m2, m3 = st.columns(3)

            with m1:

                st.metric(
                    "Objects",
                    count,
                )

            with m2:

                st.metric(
                    "Classes",
                    len(counts),
                )

            with m3:

                st.metric(
                    "Average confidence",
                    f"{average_confidence:.1f}%",
                )

            c1, c2 = st.columns(2)

            with c1:

                st.markdown(
                    '<div class="panel">',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    "### ORIGINAL"
                )

                st.image(
                    image,
                    width="stretch",
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True,
                )

            with c2:

                st.markdown(
                    '<div class="panel">',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    "### DETECTION"
                )

                st.image(
                    result_image,
                    width="stretch",
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True,
                )

            if count:

                st.markdown(
                    "### DETECTED OBJECTS"
                )

                rows = []

                for index, box in enumerate(
                    boxes,
                    start=1,
                ):

                    class_id = int(
                        box.cls[0]
                    )

                    rows.append(
                        {
                            "#": index,
                            "Object": model.names[class_id],
                            "Confidence": (
                                f"{float(box.conf[0]) * 100:.1f}%"
                            ),
                        }
                    )

                st.dataframe(
                    rows,
                    width="stretch",
                    hide_index=True,
                )

                st.markdown(
                    "### SAVE AI RESULT AS EVIDENCE"
                )

                with st.form("save_ai_evidence"):

                    title = st.text_input(
                        "Evidence title",
                        value=(
                            f"AI image analysis — "
                            f"{uploaded.name}"
                        ),
                    )

                    relevance = st.selectbox(
                        "Relevance",
                        [
                            "LOW",
                            "MEDIUM",
                            "HIGH",
                            "CRITICAL",
                        ],
                        index=1,
                    )

                    description = st.text_area(
                        "Investigator notes",
                        value=(
                            f"YOLO detected "
                            f"{count} object(s). "
                            f"Classes: "
                            f"{', '.join(counts.keys())}."
                        ),
                    )

                    save = st.form_submit_button(
                        "SAVE TO CASE EVIDENCE",
                        width="stretch",
                    )

                    if save:

                        evidence_id = execute(
                            """
                            INSERT INTO evidence
                            (
                                case_id,
                                title,
                                evidence_type,
                                relevance,
                                source,
                                description,
                                file_name,
                                created_at
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                case["id"],
                                title.strip(),
                                "CCTV / image",
                                relevance,
                                "YOLO Image Intelligence",
                                description.strip(),
                                uploaded.name,
                                now(),
                            ),
                        )

                        add_timeline(
                            case["id"],
                            "AI image analysis saved",
                            (
                                f"{uploaded.name} — "
                                f"{count} detected objects"
                            ),
                            "EVIDENCE",
                        )

                        st.success(
                            f"AI result saved as Evidence #{evidence_id}."
                        )

            else:

                st.info(
                    "No objects detected at this confidence threshold."
                )


# =========================================================
# ANALYTICS
# =========================================================

elif navigation == "Analytics":

    st.markdown("### CASE ANALYTICS")

    person_count = query_one(
        "SELECT COUNT(*) AS n FROM persons WHERE case_id = ?",
        (case["id"],)
    )["n"]

    statement_count = query_one(
        "SELECT COUNT(*) AS n FROM statements WHERE case_id = ?",
        (case["id"],)
    )["n"]

    evidence_count = query_one(
        "SELECT COUNT(*) AS n FROM evidence WHERE case_id = ?",
        (case["id"],)
    )["n"]

    location_count = query_one(
        "SELECT COUNT(*) AS n FROM locations WHERE case_id = ?",
        (case["id"],)
    )["n"]

    relationship_count = query_one(
        "SELECT COUNT(*) AS n FROM relationships WHERE case_id = ?",
        (case["id"],)
    )["n"]

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.metric("Persons", person_count)

    with m2:
        st.metric("Statements", statement_count)

    with m3:
        st.metric("Evidence", evidence_count)

    with m4:
        st.metric("Locations", location_count)

    with m5:
        st.metric("Relationships", relationship_count)

    st.markdown("### ACTIVITY DISTRIBUTION")

    chart_data = {
        "Persons": person_count,
        "Statements": statement_count,
        "Evidence": evidence_count,
        "Locations": location_count,
        "Relationships": relationship_count,
    }

    st.bar_chart(
        chart_data
    )

    st.markdown("### EVIDENCE BY TYPE")

    evidence_types = query_all(
        """
        SELECT
            evidence_type,
            COUNT(*) AS total
        FROM evidence
        WHERE case_id = ?
        GROUP BY evidence_type
        ORDER BY total DESC
        """,
        (case["id"],)
    )

    if evidence_types:

        st.dataframe(
            [
                {
                    "Evidence Type": row["evidence_type"],
                    "Count": row["total"],
                }
                for row in evidence_types
            ],
            width="stretch",
            hide_index=True,
        )

    else:

        st.info(
            "No evidence analytics available yet."
        )


# =========================================================
# REPORTS
# =========================================================

elif navigation == "Reports":

    st.markdown("### AUTOMATIC CASE REPORT")

    people = query_all(
        """
        SELECT *
        FROM persons
        WHERE case_id = ?
        ORDER BY id
        """,
        (case["id"],)
    )

    statements = query_all(
        """
        SELECT
            s.*,
            p.name AS related_person
        FROM statements s
        LEFT JOIN persons p
            ON s.person_id = p.id
        WHERE s.case_id = ?
        ORDER BY s.id
        """,
        (case["id"],)
    )

    evidence = query_all(
        """
        SELECT
            e.*,
            p.name AS related_person,
            l.name AS related_location
        FROM evidence e
        LEFT JOIN persons p
            ON e.person_id = p.id
        LEFT JOIN locations l
            ON e.location_id = l.id
        WHERE e.case_id = ?
        ORDER BY e.id
        """,
        (case["id"],)
    )

    locations = query_all(
        """
        SELECT *
        FROM locations
        WHERE case_id = ?
        ORDER BY id
        """,
        (case["id"],)
    )

    relationships = query_all(
        """
        SELECT
            r.*,
            p.name AS person_name,
            e.title AS evidence_title
        FROM relationships r
        LEFT JOIN persons p
            ON r.person_id = p.id
        LEFT JOIN evidence e
            ON r.evidence_id = e.id
        WHERE r.case_id = ?
        ORDER BY r.id
        """,
        (case["id"],)
    )

    timeline = query_all(
        """
        SELECT *
        FROM timeline
        WHERE case_id = ?
        ORDER BY event_time
        """,
        (case["id"],)
    )

    report = {
        "generated_at": now(),

        "case": dict(case),

        "persons": [
            dict(p)
            for p in people
        ],

        "statements": [
            dict(s)
            for s in statements
        ],

        "evidence": [
            dict(e)
            for e in evidence
        ],

        "locations": [
            dict(l)
            for l in locations
        ],

        "relationships": [
            dict(r)
            for r in relationships
        ],

        "timeline": [
            dict(t)
            for t in timeline
        ],
    }

    st.markdown(
        '<div class="panel">',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        ### {case["case_number"]}

        **{case["title"]}**

        Status: `{case["status"]}`

        Priority: `{case["priority"]}`

        Location: `{case["location"] or "Not specified"}`

        Lead: `{case["lead"] or "Unassigned"}`
        """
    )

    st.markdown("</div>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("Persons", len(people))

    with m2:
        st.metric("Statements", len(statements))

    with m3:
        st.metric("Evidence", len(evidence))

    with m4:
        st.metric("Timeline", len(timeline))

    report_json = json.dumps(
        report,
        indent=4,
        ensure_ascii=False,
        default=str,
    )

    st.download_button(
        "DOWNLOAD COMPLETE CASE REPORT",
        data=report_json,
        file_name=f"{case['case_number']}_complete_report.json",
        mime="application/json",
        width="stretch",
    )

    with st.expander(
        "VIEW COMPLETE REPORT DATA"
    ):

        st.json(
            report
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#53657b;
        margin:45px 0 10px;
        font-family:'Space Mono',monospace;
        font-size:11px;
    ">
        CID INVESTIGATION INTELLIGENCE
        · CONNECTED CASE MANAGEMENT
        · SQLITE DATABASE
    </div>
    """,
    unsafe_allow_html=True,
)
