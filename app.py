```python
import json
from datetime import datetime
from collections import Counter

import streamlit as st
from PIL import Image

# Optional YOLO imports are loaded only when Image Intelligence is opened.
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CID Investigation Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
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
        background-size: auto, auto, 36px 36px, 36px 36px;
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
        position: relative;
        overflow: hidden;
    }

    .hero:after {
        content: '';
        position: absolute;
        right: -90px;
        top: -100px;
        width: 280px;
        height: 280px;
        border: 1px solid rgba(0,229,255,.15);
        border-radius: 50%;
        box-shadow:
            0 0 0 30px rgba(0,229,255,.025),
            0 0 0 60px rgba(0,229,255,.018);
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
        max-width: 850px;
        font-size: 15px;
    }

    .panel {
        border: 1px solid rgba(148,163,184,.13);
        background: rgba(10,15,24,.78);
        border-radius: 18px;
        padding: 18px;
        height: 100%;
        box-shadow: inset 0 1px rgba(255,255,255,.025);
        margin-bottom: 16px;
    }

    .panel-title {
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 12px;
        letter-spacing: .3px;
    }

    .mono {
        font-family: 'Space Mono', monospace;
        color: #7dd3fc;
        font-size: 12px;
    }

    .muted {
        color: #718198;
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

    [data-testid="stSidebar"] {
        background: #080d15;
        border-right: 1px solid rgba(148,163,184,.12);
    }

    [data-testid="stFileUploaderDropzone"] {
        background: rgba(8,15,25,.72);
        border: 1px dashed rgba(0,229,255,.35);
        border-radius: 16px;
    }

    .stButton button {
        border-radius: 10px;
    }

    div[data-testid="stMetric"] {
        background: rgba(15,23,36,.85);
        border: 1px solid rgba(148,163,184,.10);
        border-radius: 14px;
        padding: 10px;
    }

    .timeline-line {
        border-left: 2px solid rgba(0,229,255,.25);
        padding-left: 18px;
        margin-left: 7px;
    }

    .timeline-item {
        margin-bottom: 20px;
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
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "active_case" not in st.session_state:
    st.session_state.active_case = "CID-2026-001"

if "cases" not in st.session_state:
    st.session_state.cases = [
        {
            "id": "CID-2026-001",
            "title": "Warehouse Incident",
            "status": "ACTIVE",
            "priority": "HIGH",
            "location": "Industrial Area",
            "lead": "Investigation Unit A",
            "opened": "2026-08-24",
            "description": "Investigation regarding an incident reported at a commercial warehouse.",
        },
        {
            "id": "CID-2026-002",
            "title": "Missing Property Report",
            "status": "PENDING",
            "priority": "MEDIUM",
            "location": "Central District",
            "lead": "Investigation Unit B",
            "opened": "2026-08-21",
            "description": "Property disappearance case requiring statement and evidence review.",
        },
        {
            "id": "CID-2026-003",
            "title": "Vehicle Incident",
            "status": "REVIEW",
            "priority": "LOW",
            "location": "North Sector",
            "lead": "Investigation Unit C",
            "opened": "2026-08-19",
            "description": "Vehicle-related incident under preliminary review.",
        },
    ]

if "persons" not in st.session_state:
    st.session_state.persons = []

if "statements" not in st.session_state:
    st.session_state.statements = []

if "clues" not in st.session_state:
    st.session_state.clues = []

if "timeline" not in st.session_state:
    st.session_state.timeline = [
        {
            "date": "2026-08-24 09:15",
            "title": "Case opened",
            "detail": "Initial incident report registered.",
        },
        {
            "date": "2026-08-24 11:40",
            "title": "Scene review",
            "detail": "Initial observations recorded.",
        },
        {
            "date": "2026-08-25 14:20",
            "title": "Statement added",
            "detail": "Witness statement entered into case file.",
        },
    ]


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
                Secure case-management workspace for organizing investigations,
                persons, statements, clues, timelines and optional image intelligence.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 1.2, 1])

    with c2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown("### ◈ SECURE ACCESS")
        st.caption("Demo authentication — replace with your real authentication system before production use.")

        username = st.text_input("Officer ID", placeholder="Enter officer ID")
        password = st.text_input(
            "Access key",
            type="password",
            placeholder="Enter access key",
        )

        if st.button("AUTHENTICATE", use_container_width=True):
            if username == "admin" and password == "cid2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Authentication failed.")

        st.markdown(
            '<div class="mono" style="margin-top:15px">DEMO // admin / cid2026</div>',
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)


if not st.session_state.authenticated:
    login_screen()
    st.stop()


# =========================================================
# HELPERS
# =========================================================

def active_case():
    for case in st.session_state.cases:
        if case["id"] == st.session_state.active_case:
            return case

    return st.session_state.cases[0]


def metric_card(value, label):
    st.markdown(
        f"""
        <div class="metric">
            <div class="value">{value}</div>
            <div class="label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def add_timeline_event(title, detail):
    st.session_state.timeline.insert(
        0,
        {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": title,
            "detail": detail,
        },
    )


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

    case_options = [case["id"] for case in st.session_state.cases]

    selected_case = st.selectbox(
        "Case",
        case_options,
        index=case_options.index(st.session_state.active_case),
        label_visibility="collapsed",
    )

    if selected_case != st.session_state.active_case:
        st.session_state.active_case = selected_case
        st.rerun()

    case = active_case()

    st.markdown(
        f"""
        <div class="case-card">
            <div class="case-id">{case["id"]}</div>
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
        '<div class="mono">SESSION // ACTIVE</div>',
        unsafe_allow_html=True,
    )

    if st.button("LOCK SYSTEM", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()


# =========================================================
# HERO
# =========================================================

st.markdown(
    f"""
    <div class="hero">
        <div class="eyebrow">CID / CASE INTELLIGENCE PLATFORM</div>
        <h1>{navigation}</h1>
        <p>
            Active investigation:
            <strong>{case["id"]}</strong> — {case["title"]}.
            Centralized workspace for structured case intelligence.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# COMMAND CENTER
# =========================================================

if navigation == "Command Center":

    st.markdown("### OPERATIONAL OVERVIEW")

    active_cases = sum(
        1 for c in st.session_state.cases if c["status"] == "ACTIVE"
    )

    high_priority = sum(
        1 for c in st.session_state.cases if c["priority"] == "HIGH"
    )

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        metric_card(len(st.session_state.cases), "Total cases")

    with m2:
        metric_card(active_cases, "Active cases")

    with m3:
        metric_card(len(st.session_state.persons), "Persons logged")

    with m4:
        metric_card(len(st.session_state.clues), "Clues / evidence")

    st.write("")

    left, right = st.columns([1.6, 1])

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### CASE PORTFOLIO")

        for c in st.session_state.cases:
            st.markdown(
                f"""
                <div class="case-card">
                    <div class="case-id">{c["id"]}</div>
                    <div class="case-title">{c["title"]}</div>
                    <div class="muted">
                        {c["location"]} · Opened {c["opened"]}
                    </div>
                    <span class="tag">{c["status"]}</span>
                    <span class="tag">{c["priority"]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### SYSTEM STATUS")

        st.markdown(
            '<div class="status"><span class="dot"></span> DATABASE ONLINE</div>',
            unsafe_allow_html=True,
        )

        st.write("")
        st.markdown('<div class="mono">CASE ENGINE // READY</div>', unsafe_allow_html=True)
        st.markdown('<div class="mono">EVIDENCE INDEX // READY</div>', unsafe_allow_html=True)
        st.markdown('<div class="mono">TIMELINE ENGINE // READY</div>', unsafe_allow_html=True)
        st.markdown('<div class="mono">IMAGE AI // OPTIONAL</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### ACTIVE CASE")

        st.markdown(f"**{case['title']}**")
        st.caption(case["description"])
        st.write(f"**Location:** {case['location']}")
        st.write(f"**Lead:** {case['lead']}")

        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# CASE FILES
# =========================================================

elif navigation == "Case Files":

    st.markdown("### CASE MANAGEMENT")

    with st.expander("＋ CREATE NEW CASE", expanded=False):

        with st.form("new_case_form"):

            title = st.text_input("Case title")
            location = st.text_input("Location")
            priority = st.selectbox(
                "Priority",
                ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            )
            lead = st.text_input("Investigation lead")
            description = st.text_area("Case description")

            submitted = st.form_submit_button(
                "CREATE CASE",
                use_container_width=True,
            )

            if submitted:

                if not title.strip():
                    st.error("Case title is required.")
                else:

                    number = len(st.session_state.cases) + 1

                    new_case = {
                        "id": f"CID-2026-{number:03d}",
                        "title": title.strip(),
                        "status": "ACTIVE",
                        "priority": priority,
                        "location": location.strip() or "Unknown",
                        "lead": lead.strip() or "Unassigned",
                        "opened": datetime.now().strftime("%Y-%m-%d"),
                        "description": description.strip(),
                    }

                    st.session_state.cases.append(new_case)
                    st.session_state.active_case = new_case["id"]

                    add_timeline_event(
                        "Case created",
                        f"{new_case['id']} — {new_case['title']}",
                    )

                    st.success("Case created.")
                    st.rerun()

    st.write("")

    for c in st.session_state.cases:

        with st.container(border=True):

            a, b, d = st.columns([3, 1, 1])

            with a:
                st.markdown(f"#### {c['title']}")
                st.markdown(
                    f"`{c['id']}` · {c['location']} · {c['opened']}"
                )
                st.caption(c["description"])

            with b:
                st.metric("Priority", c["priority"])

            with d:
                if c["id"] == st.session_state.active_case:
                    st.success("ACTIVE")
                else:
                    if st.button(
                        "OPEN",
                        key=f"open_{c['id']}",
                        use_container_width=True,
                    ):
                        st.session_state.active_case = c["id"]
                        st.rerun()


# =========================================================
# PERSONS
# =========================================================

elif navigation == "Persons / Suspects":

    st.markdown("### PERSONS & SUBJECTS")

    with st.expander("＋ ADD PERSON", expanded=False):

        with st.form("person_form"):

            name = st.text_input("Name / identifier")
            role = st.selectbox(
                "Classification",
                [
                    "Person of interest",
                    "Witness",
                    "Complainant",
                    "Suspect",
                    "Victim",
                    "Other",
                ],
            )
            phone = st.text_input("Contact reference")
            notes = st.text_area("Notes")

            submitted = st.form_submit_button(
                "ADD PERSON",
                use_container_width=True,
            )

            if submitted:

                if not name.strip():
                    st.error("Name / identifier is required.")
                else:

                    st.session_state.persons.append(
                        {
                            "case": st.session_state.active_case,
                            "name": name.strip(),
                            "role": role,
                            "phone": phone.strip(),
                            "notes": notes.strip(),
                        }
                    )

                    add_timeline_event(
                        "Person added",
                        f"{name.strip()} added as {role}.",
                    )

                    st.success("Person added.")
                    st.rerun()

    people = [
        p
        for p in st.session_state.persons
        if p["case"] == st.session_state.active_case
    ]

    if not people:
        st.info("No persons have been logged for this case.")
    else:

        for p in people:

            st.markdown(
                f"""
                <div class="case-card">
                    <div class="case-id">{p["role"].upper()}</div>
                    <div class="case-title">{p["name"]}</div>
                    <div class="muted">
                        Contact: {p["phone"] or "Not provided"}
                    </div>
                    <p>{p["notes"] or "No notes recorded."}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# STATEMENTS
# =========================================================

elif navigation == "Statements":

    st.markdown("### STATEMENT REGISTER")

    with st.expander("＋ RECORD STATEMENT", expanded=False):

        with st.form("statement_form"):

            person = st.text_input("Statement source")
            statement_type = st.selectbox(
                "Type",
                ["Witness", "Complainant", "Subject", "Officer", "Other"],
            )
            statement = st.text_area(
                "Statement notes",
                height=180,
            )

            submitted = st.form_submit_button(
                "SAVE STATEMENT",
                use_container_width=True,
            )

            if submitted:

                if not person.strip() or not statement.strip():
                    st.error("Source and statement notes are required.")
                else:

                    st.session_state.statements.append(
                        {
                            "case": st.session_state.active_case,
                            "source": person.strip(),
                            "type": statement_type,
                            "statement": statement.strip(),
                            "date": datetime.now().strftime(
                                "%Y-%m-%d %H:%M"
                            ),
                        }
                    )

                    add_timeline_event(
                        "Statement recorded",
                        f"{person.strip()} — {statement_type}",
                    )

                    st.success("Statement recorded.")
                    st.rerun()

    statements = [
        s
        for s in st.session_state.statements
        if s["case"] == st.session_state.active_case
    ]

    if not statements:
        st.info("No statements recorded for this case.")
    else:

        for s in reversed(statements):

            with st.container(border=True):

                st.markdown(
                    f"**{s['source']}** · `{s['type']}`"
                )

                st.caption(s["date"])
                st.write(s["statement"])


# =========================================================
# CLUES / EVIDENCE
# =========================================================

elif navigation == "Clues & Evidence":

    st.markdown("### CLUE & EVIDENCE REGISTER")

    with st.expander("＋ ADD CLUE", expanded=False):

        with st.form("clue_form"):

            clue_title = st.text_input("Clue / evidence title")

            clue_type = st.selectbox(
                "Type",
                [
                    "Physical evidence",
                    "Digital evidence",
                    "Document",
                    "Observation",
                    "Lead",
                    "Other",
                ],
            )

            source = st.text_input("Source / location")
            relevance = st.select_slider(
                "Relevance",
                options=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                value="MEDIUM",
            )

            clue_notes = st.text_area("Details")

            submitted = st.form_submit_button(
                "REGISTER CLUE",
                use_container_width=True,
            )

            if submitted:

                if not clue_title.strip():
                    st.error("Clue title is required.")
                else:

                    st.session_state.clues.append(
                        {
                            "case": st.session_state.active_case,
                            "title": clue_title.strip(),
                            "type": clue_type,
                            "source": source.strip(),
                            "relevance": relevance,
                            "notes": clue_notes.strip(),
                            "date": datetime.now().strftime(
                                "%Y-%m-%d %H:%M"
                            ),
                        }
                    )

                    add_timeline_event(
                        "Evidence registered",
                        clue_title.strip(),
                    )

                    st.success("Clue registered.")
                    st.rerun()

    clues = [
        c
        for c in st.session_state.clues
        if c["case"] == st.session_state.active_case
    ]

    if not clues:
        st.info("No clues or evidence have been registered.")
    else:

        for c in reversed(clues):

            with st.container(border=True):

                a, b = st.columns([4, 1])

                with a:
                    st.markdown(f"### {c['title']}")
                    st.caption(
                        f"{c['type']} · Source: {c['source'] or 'Not specified'}"
                    )
                    st.write(c["notes"] or "No additional details.")

                with b:
                    st.metric("Relevance", c["relevance"])


# =========================================================
# INVESTIGATION BOARD
# =========================================================

elif navigation == "Investigation Board":

    st.markdown("### INVESTIGATION BOARD")

    st.caption(
        "Use this workspace to connect people, clues and investigation leads."
    )

    people = [
        p
        for p in st.session_state.persons
        if p["case"] == st.session_state.active_case
    ]

    clues = [
        c
        for c in st.session_state.clues
        if c["case"] == st.session_state.active_case
    ]

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
        st.markdown("### CLUES")

        if clues:
            for c in clues:
                st.markdown(
                    f'<span class="tag">{c["title"]}</span>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No clues.")
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### LEADS")

        leads = [
            c for c in clues
            if c["type"] == "Lead"
        ]

        if leads:
            for lead in leads:
                st.markdown(
                    f'<span class="tag">{lead["title"]}</span>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No investigation leads.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### RELATIONSHIP NOTES")

    with st.form("relationship_form"):

        source = st.text_input("Entity A")
        target = st.text_input("Entity B")
        relation = st.text_input(
            "Relationship / connection",
            placeholder="e.g. witness to incident",
        )

        submitted = st.form_submit_button(
            "ADD CONNECTION",
            use_container_width=True,
        )

        if submitted:

            if source.strip() and target.strip() and relation.strip():

                add_timeline_event(
                    "Investigation connection added",
                    f"{source} → {target}: {relation}",
                )

                st.success("Connection recorded.")
            else:
                st.error("All relationship fields are required.")


# =========================================================
# TIMELINE
# =========================================================

elif navigation == "Timeline":

    st.markdown("### CASE TIMELINE")

    with st.expander("＋ ADD TIMELINE EVENT", expanded=False):

        with st.form("timeline_form"):

            title = st.text_input("Event title")
            detail = st.text_area("Event detail")

            submitted = st.form_submit_button(
                "ADD EVENT",
                use_container_width=True,
            )

            if submitted:

                if not title.strip():
                    st.error("Event title is required.")
                else:

                    add_timeline_event(
                        title.strip(),
                        detail.strip(),
                    )

                    st.success("Timeline event added.")
                    st.rerun()

    st.markdown('<div class="timeline-line">', unsafe_allow_html=True)

    for event in st.session_state.timeline:

        st.markdown(
            f"""
            <div class="timeline-item">
                <div class="mono">{event["date"]}</div>
                <strong>{event["title"]}</strong>
                <div class="muted">{event["detail"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# LOCATIONS
# =========================================================

elif navigation == "Locations":

    st.markdown("### LOCATION INTELLIGENCE")

    st.info(
        "This module stores investigation locations. "
        "For production use, connect it to a proper GIS/database layer."
    )

    location_name = st.text_input(
        "Search / record location",
        value=case["location"],
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### ACTIVE CASE LOCATION")
        st.markdown(f"## {location_name}")
        st.caption("Primary location associated with the active case.")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### LOCATION DATA")
        st.markdown(
            '<div class="mono">GEO STATUS // MANUAL</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="mono">GIS CONNECTOR // NOT CONFIGURED</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# IMAGE INTELLIGENCE
# =========================================================

elif navigation == "Image Intelligence":

    st.markdown("### IMAGE INTELLIGENCE")

    st.warning(
        "YOLO is an object detector. It should not be treated as "
        "closed-set celebrity/person identity recognition."
    )

    if YOLO is None:

        st.error(
            "Ultralytics is not installed. Add `ultralytics` to requirements.txt."
        )

    else:

        confidence = st.slider(
            "Detection confidence",
            0.10,
            0.95,
            0.35,
            0.05,
        )

        uploaded_file = st.file_uploader(
            "Upload image",
            type=["jpg", "jpeg", "png"],
        )

        if uploaded_file is None:

            st.markdown(
                """
                <div class="panel" style="text-align:center;padding:55px">
                    <div class="eyebrow">IMAGE AI</div>
                    <h2>WAITING FOR IMAGE INPUT</h2>
                    <p class="muted">
                        Upload a JPG, JPEG or PNG image to start object detection.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            @st.cache_resource
            def load_yolo_model():
                return YOLO("yolov8n.pt")

            with st.spinner("Initializing YOLO model..."):
                model = load_yolo_model()

            image = Image.open(uploaded_file).convert("RGB")

            with st.spinner("Running object detection..."):
                results = model(
                    image,
                    conf=confidence,
                    verbose=False,
                )

            result = results[0]

            plotted = result.plot()

            # Ultralytics returns BGR array.
            plotted_rgb = plotted[:, :, ::-1]

            result_image = Image.fromarray(plotted_rgb)

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

            counts = Counter(classes)

            avg_conf = (
                sum(confidences) / count * 100
                if count
                else 0
            )

            m1, m2, m3, m4 = st.columns(4)

            with m1:
                metric_card(count, "Objects detected")

            with m2:
                metric_card(len(counts), "Unique classes")

            with m3:
                metric_card(
                    f"{avg_conf:.1f}%",
                    "Average confidence",
                )

            with m4:
                metric_card(
                    f"{image.width}×{image.height}",
                    "Input resolution",
                )

            st.write("")

            c1, c2 = st.columns(2)

            with c1:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                st.markdown("### ORIGINAL FRAME")
                st.image(
                    image,
                    use_container_width=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                st.markdown("### DETECTION FRAME")
                st.image(
                    result_image,
                    use_container_width=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("### DETECTION LOG")

            if not count:

                st.info(
                    "No objects detected at the selected confidence threshold."
                )

            else:

                summary_cols = st.columns(
                    min(4, max(1, len(counts)))
                )

                for i, (name, qty) in enumerate(counts.items()):

                    with summary_cols[
                        i % len(summary_cols)
                    ]:

                        metric_card(
                            qty,
                            name,
                        )

                rows = []

                for idx, box in enumerate(
                    boxes,
                    start=1,
                ):

                    class_id = int(box.cls[0])

                    rows.append(
                        {
                            "#": idx,
                            "Object": model.names[class_id],
                            "Confidence": (
                                f"{float(box.conf[0]) * 100:.1f}%"
                            ),
                        }
                    )

                st.dataframe(
                    rows,
                    use_container_width=True,
                    hide_index=True,
                )


# =========================================================
# ANALYTICS
# =========================================================

elif navigation == "Analytics":

    st.markdown("### INVESTIGATION ANALYTICS")

    status_counts = Counter(
        c["status"]
        for c in st.session_state.cases
    )

    priority_counts = Counter(
        c["priority"]
        for c in st.session_state.cases
    )

    c1, c2 = st.columns(2)

    with c1:

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### CASE STATUS")

        for status, amount in status_counts.items():

            st.write(
                f"**{status}** — {amount}"
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with c2:

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### PRIORITY DISTRIBUTION")

        for priority, amount in priority_counts.items():

            st.write(
                f"**{priority}** — {amount}"
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### CURRENT CASE ACTIVITY")

    activity_data = {
        "Persons": len(
            [
                p for p in st.session_state.persons
                if p["case"] == st.session_state.active_case
            ]
        ),
        "Statements": len(
            [
                s for s in st.session_state.statements
                if s["case"] == st.session_state.active_case
            ]
        ),
        "Clues": len(
            [
                c for c in st.session_state.clues
                if c["case"] == st.session_state.active_case
            ]
        ),
        "Timeline events": len(st.session_state.timeline),
    }

    st.bar_chart(activity_data)


# =========================================================
# REPORTS
# =========================================================

elif navigation == "Reports":

    st.markdown("### CASE REPORT GENERATOR")

    people = [
        p for p in st.session_state.persons
        if p["case"] == st.session_state.active_case
    ]

    statements = [
        s for s in st.session_state.statements
        if s["case"] == st.session_state.active_case
    ]

    clues = [
        c for c in st.session_state.clues
        if c["case"] == st.session_state.active_case
    ]

    report = {
        "generated_at": datetime.now().isoformat(),
        "case": case,
        "persons": people,
        "statements": statements,
        "clues": clues,
        "timeline": st.session_state.timeline,
    }

    st.markdown(
        '<div class="panel">',
        unsafe_allow_html=True,
    )

    st.markdown("### REPORT PREVIEW")

    st.write(f"**Case:** {case['id']}")
    st.write(f"**Title:** {case['title']}")
    st.write(f"**Status:** {case['status']}")
    st.write(f"**Priority:** {case['priority']}")
    st.write(f"**Location:** {case['location']}")
    st.write(f"**Lead:** {case['lead']}")

    st.markdown("---")

    st.write(f"Persons: **{len(people)}**")
    st.write(f"Statements: **{len(statements)}**")
    st.write(f"Clues: **{len(clues)}**")

    st.markdown("</div>", unsafe_allow_html=True)

    report_json = json.dumps(
        report,
        indent=4,
        ensure_ascii=False,
    )

    st.download_button(
        "DOWNLOAD JSON CASE REPORT",
        data=report_json,
        file_name=f"{case['id']}_report.json",
        mime="application/json",
        use_container_width=True,
    )

    with st.expander("VIEW RAW JSON"):

        st.code(
            report_json,
            language="json",
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
        CID INVESTIGATION INTELLIGENCE · CASE MANAGEMENT / OBJECT DETECTION
    </div>
    """,
    unsafe_allow_html=True,
)
```
