import json
from collections import Counter
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

# YOLO is imported lazily so the dashboard can start even before the model is needed.
try:
    from ultralytics import YOLO
except Exception:
    YOLO = None


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="CID Intelligence Hub",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# STYLING
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

    .stApp {
        background:
            radial-gradient(circle at 12% 10%, rgba(0,229,255,.08), transparent 24%),
            radial-gradient(circle at 88% 12%, rgba(124,58,237,.09), transparent 24%),
            linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px),
            #070b12;
        background-size: auto, auto, 34px 34px, 34px 34px;
        color: #e8eef7;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, p, label, div, span {
        font-family: Inter, sans-serif;
    }

    .hero {
        border: 1px solid rgba(0,229,255,.18);
        background: linear-gradient(135deg, rgba(10,18,31,.95), rgba(10,14,25,.76));
        border-radius: 22px;
        padding: 28px 32px;
        margin-bottom: 20px;
        box-shadow: 0 0 45px rgba(0,229,255,.05), inset 0 1px rgba(255,255,255,.04);
    }

    .eyebrow {
        color: #00e5ff;
        font: 700 11px 'Space Mono', monospace;
        letter-spacing: 2px;
    }

    .hero h1 {
        font-size: 40px;
        margin: 8px 0;
        letter-spacing: -1.5px;
    }

    .hero p {
        color: #93a4ba;
        margin: 0;
        max-width: 850px;
        font-size: 14px;
    }

    .panel {
        border: 1px solid rgba(148,163,184,.13);
        background: rgba(10,15,24,.78);
        border-radius: 18px;
        padding: 18px;
        box-shadow: inset 0 1px rgba(255,255,255,.025);
    }

    .metric {
        background: rgba(15,23,36,.92);
        border: 1px solid rgba(148,163,184,.12);
        border-radius: 14px;
        padding: 15px;
        text-align: center;
        min-height: 86px;
    }

    .metric .value {
        font: 800 23px 'Space Mono', monospace;
        color: #eaf7ff;
    }

    .metric .label {
        color: #718198;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 5px;
    }

    .mono {
        font-family: 'Space Mono', monospace !important;
        color: #7dd3fc;
        font-size: 11px;
    }

    .tag {
        display: inline-block;
        padding: 4px 9px;
        border-radius: 999px;
        background: rgba(0,229,255,.08);
        border: 1px solid rgba(0,229,255,.16);
        color: #8be9ff;
        font-size: 11px;
        margin: 2px;
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

    .stButton button, .stDownloadButton button {
        border-radius: 10px;
    }

    .small-muted {
        color: #718198;
        font-size: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION DATA
# ============================================================
def new_state():
    return {
        "cases": [],
        "persons": [],
        "evidence": [],
        "clues": [],
        "timeline": [],
        "locations": [],
        "board": [],
        "next_case": 1,
        "next_person": 1,
        "next_evidence": 1,
        "next_clue": 1,
        "next_event": 1,
        "next_location": 1,
        "next_board": 1,
    }


if "db" not in st.session_state:
    st.session_state.db = new_state()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "selected_case_id" not in st.session_state:
    st.session_state.selected_case_id = None


db = st.session_state.db


# ============================================================
# HELPERS
# ============================================================
def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def make_id(prefix, number):
    return f"{prefix}-{number:03d}"


def get_case(case_id):
    return next((x for x in db["cases"] if x["id"] == case_id), None)


def selected_case():
    return get_case(st.session_state.selected_case_id)


def case_options():
    return {f'{c["id"]} — {c["title"]}': c["id"] for c in db["cases"]}


def case_counts(case_id):
    return {
        "persons": sum(x["case_id"] == case_id for x in db["persons"]),
        "evidence": sum(x["case_id"] == case_id for x in db["evidence"]),
        "clues": sum(x["case_id"] == case_id for x in db["clues"]),
        "timeline": sum(x["case_id"] == case_id for x in db["timeline"]),
        "locations": sum(x["case_id"] == case_id for x in db["locations"]),
    }


def ensure_case_selected():
    if not db["cases"]:
        return False
    if not get_case(st.session_state.selected_case_id):
        st.session_state.selected_case_id = db["cases"][0]["id"]
    return True


def add_case(title, category, priority, status, summary):
    case_id = make_id("CASE", db["next_case"])
    db["next_case"] += 1
    item = {
        "id": case_id,
        "title": title,
        "category": category,
        "priority": priority,
        "status": status,
        "summary": summary,
        "created": now_text(),
    }
    db["cases"].append(item)
    st.session_state.selected_case_id = case_id
    return case_id


def add_person(case_id, name, role, phone, notes):
    pid = make_id("PER", db["next_person"])
    db["next_person"] += 1
    db["persons"].append(
        {
            "id": pid,
            "case_id": case_id,
            "name": name,
            "role": role,
            "phone": phone,
            "notes": notes,
            "created": now_text(),
        }
    )
    return pid


def add_evidence(case_id, title, kind, source, description, linked_person=""):
    eid = make_id("EVD", db["next_evidence"])
    db["next_evidence"] += 1
    db["evidence"].append(
        {
            "id": eid,
            "case_id": case_id,
            "title": title,
            "kind": kind,
            "source": source,
            "description": description,
            "linked_person": linked_person,
            "created": now_text(),
        }
    )
    return eid


def add_clue(case_id, title, strength, status, description):
    cid = make_id("CLUE", db["next_clue"])
    db["next_clue"] += 1
    db["clues"].append(
        {
            "id": cid,
            "case_id": case_id,
            "title": title,
            "strength": strength,
            "status": status,
            "description": description,
            "created": now_text(),
        }
    )
    return cid


def add_event(case_id, title, date_text, location, description):
    eid = make_id("EVT", db["next_event"])
    db["next_event"] += 1
    db["timeline"].append(
        {
            "id": eid,
            "case_id": case_id,
            "title": title,
            "date": date_text,
            "location": location,
            "description": description,
        }
    )
    return eid


def add_location(case_id, name, address, category, notes):
    lid = make_id("LOC", db["next_location"])
    db["next_location"] += 1
    db["locations"].append(
        {
            "id": lid,
            "case_id": case_id,
            "name": name,
            "address": address,
            "category": category,
            "notes": notes,
        }
    )
    return lid


def add_board_item(case_id, item_type, item_id, note):
    bid = make_id("LINK", db["next_board"])
    db["next_board"] += 1
    db["board"].append(
        {
            "id": bid,
            "case_id": case_id,
            "item_type": item_type,
            "item_id": item_id,
            "note": note,
        }
    )
    return bid


def seed_demo():
    if db["cases"]:
        return

    cid = add_case(
        "Warehouse Night Incident",
        "Theft",
        "HIGH",
        "Active",
        "Night-time warehouse incident with CCTV evidence, a vehicle lead and multiple persons of interest.",
    )
    p1 = add_person(cid, "Ali R.", "Person of Interest", "+92 300 0000000", "Seen near warehouse access road.")
    p2 = add_person(cid, "Bilal K.", "Witness", "+92 301 0000000", "Reported unusual vehicle movement.")
    e1 = add_evidence(
        cid,
        "Warehouse CCTV",
        "Image",
        "Security Camera 04",
        "Frame showing a vehicle and two people near the loading gate.",
        p1,
    )
    e2 = add_evidence(
        cid,
        "Vehicle Observation",
        "Observation",
        "Witness statement",
        "Dark vehicle reportedly left the area around 02:15.",
        p2,
    )
    cl1 = add_clue(
        cid,
        "Vehicle movement",
        "Strong",
        "Open",
        "Witness account and CCTV appear to point to the same time window.",
    )
    add_event(cid, "Incident reported", "2026-08-20 02:05", "Warehouse Gate", "Alarm triggered.")
    add_event(cid, "Vehicle observed", "2026-08-20 02:15", "Access Road", "Witness saw a dark vehicle.")
    add_location(cid, "Warehouse Gate", "Sector Industrial Area", "Scene", "Primary incident location.")
    add_board_item(cid, "Evidence", e1, "Compare with vehicle observation.")
    add_board_item(cid, "Evidence", e2, "Check time consistency.")
    add_board_item(cid, "Clue", cl1, "Potential connection.")
    st.session_state.selected_case_id = cid


def get_person_name(person_id):
    if not person_id:
        return "—"
    person = next((x for x in db["persons"] if x["id"] == person_id), None)
    return person["name"] if person else person_id


# ============================================================
# LOGIN
# ============================================================
if not st.session_state.logged_in:
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">CID / CONTROLLED INVESTIGATION ENVIRONMENT</div>
            <h1>🕵️ CID Intelligence Hub</h1>
            <p>Case management, linked evidence, persons, clues, timeline analysis and optional YOLO image intelligence.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    a, b, c = st.columns([1, 1.2, 1])
    with b:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Secure Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("ENTER CONTROL ROOM", type="primary", width="stretch"):
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                seed_demo()
                st.rerun()
            else:
                st.error("Invalid credentials.")
        st.caption("Demo login: admin / admin123")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🕵️ CID CONTROL")
    st.caption("Connected Investigation Workspace")
    st.divider()

    pages = [
        "Dashboard",
        "Case Files",
        "Persons",
        "Evidence",
        "Clues",
        "Investigation Board",
        "Timeline",
        "Locations",
        "Image Intelligence",
        "Analytics",
        "Report",
    ]

    page = st.radio("MODULES", pages, index=pages.index(st.session_state.page))
    st.session_state.page = page

    st.divider()

    if db["cases"]:
        labels = list(case_options().keys())
        current_label = next(
            (k for k, v in case_options().items() if v == st.session_state.selected_case_id),
            labels[0],
        )
        chosen = st.selectbox("ACTIVE CASE", labels, index=labels.index(current_label))
        st.session_state.selected_case_id = case_options()[chosen]
    else:
        st.info("Create a case first.")

    st.divider()
    st.markdown('<div class="mono">SYSTEM // ONLINE</div>', unsafe_allow_html=True)
    st.markdown('<div class="mono">MODE // CASE INTELLIGENCE</div>', unsafe_allow_html=True)

    if st.button("Reset Demo Data", width="stretch"):
        st.session_state.db = new_state()
        db = st.session_state.db
        seed_demo()
        st.rerun()

    if st.button("Logout", width="stretch"):
        st.session_state.logged_in = False
        st.rerun()


# ============================================================
# TOP BAR
# ============================================================
case = selected_case()

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">AI-ASSISTED CASE MANAGEMENT / LINKED DATA</div>
        <h1>CID Intelligence Hub</h1>
        <p>Everything is connected through the active case: persons ↔ evidence ↔ clues ↔ timeline ↔ locations ↔ investigation board.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if case:
    st.markdown(
        f"""
        <div class="panel">
            <span class="tag">{case["id"]}</span>
            <span class="tag">{case["status"]}</span>
            <span class="tag">{case["priority"]} PRIORITY</span>
            <strong style="font-size:18px">{case["title"]}</strong>
            <div class="small-muted" style="margin-top:8px">{case["summary"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.warning("No case exists. Create one from Case Files.")


# ============================================================
# DASHBOARD
# ============================================================
if page == "Dashboard":
    st.markdown("### LIVE CASE OVERVIEW")

    if not case:
        st.info("Create your first case from Case Files.")
    else:
        counts = case_counts(case["id"])
        cols = st.columns(6)
        metrics = [
            (len(db["cases"]), "Total cases"),
            (counts["persons"], "Persons"),
            (counts["evidence"], "Evidence"),
            (counts["clues"], "Clues"),
            (counts["timeline"], "Timeline events"),
            (counts["locations"], "Locations"),
        ]
        for col, value, label in zip(cols, *zip(*metrics)):
            with col:
                st.markdown(
                    f'<div class="metric"><div class="value">{value}</div><div class="label">{label}</div></div>',
                    unsafe_allow_html=True,
                )

        st.write("")
        left, right = st.columns([1.3, 1])

        with left:
            st.markdown("#### Case Activity")
            activities = []
            for x in db["evidence"]:
                if x["case_id"] == case["id"]:
                    activities.append(("Evidence", x["created"], x["title"]))
            for x in db["clues"]:
                if x["case_id"] == case["id"]:
                    activities.append(("Clue", x["created"], x["title"]))
            for x in db["persons"]:
                if x["case_id"] == case["id"]:
                    activities.append(("Person", x["created"], x["name"]))

            if activities:
                activities.sort(key=lambda x: x[1], reverse=True)
                st.dataframe(
                    pd.DataFrame(activities, columns=["Type", "Time", "Item"]),
                    width="stretch",
                    hide_index=True,
                )
            else:
                st.info("No activity yet.")

        with right:
            st.markdown("#### Connected Intelligence")
            st.markdown(
                f"""
                <div class="panel">
                    <div class="mono">CASE ID</div>
                    <h3>{case["id"]}</h3>
                    <div class="mono">CREATED</div>
                    <p>{case["created"]}</p>
                    <div class="mono">CATEGORY</div>
                    <p>{case["category"]}</p>
                    <div class="mono">LINKS</div>
                    <p>{counts["evidence"] + counts["clues"] + counts["persons"] + counts["timeline"] + counts["locations"]} connected records</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# CASE FILES
# ============================================================
elif page == "Case Files":
    st.markdown("### CASE FILES")

    with st.expander("➕ Create New Case", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            title = st.text_input("Case title", key="new_case_title")
            category = st.selectbox(
                "Category",
                ["Theft", "Missing Person", "Fraud", "Assault", "Cyber", "Other"],
                key="new_case_category",
            )
            priority = st.selectbox(
                "Priority", ["LOW", "MEDIUM", "HIGH", "CRITICAL"], key="new_case_priority"
            )
        with c2:
            status = st.selectbox(
                "Status", ["Active", "Under Review", "Closed"], key="new_case_status"
            )
            summary = st.text_area("Case summary", key="new_case_summary")

        if st.button("CREATE CASE", type="primary"):
            if title.strip():
                cid = add_case(title.strip(), category, priority, status, summary.strip())
                st.success(f"Created {cid}. All other modules now use this case automatically.")
                st.rerun()
            else:
                st.error("Case title is required.")

    st.write("")
    if db["cases"]:
        rows = [
            {
                "ID": c["id"],
                "Title": c["title"],
                "Category": c["category"],
                "Priority": c["priority"],
                "Status": c["status"],
                "Created": c["created"],
            }
            for c in db["cases"]
        ]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    else:
        st.info("No cases.")


# ============================================================
# PERSONS
# ============================================================
elif page == "Persons":
    st.markdown("### PERSONS / PERSONS OF INTEREST")

    if not case:
        st.warning("Create/select a case first.")
    else:
        with st.expander("➕ Add Person", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Name")
                role = st.selectbox(
                    "Role",
                    ["Person of Interest", "Witness", "Complainant", "Victim", "Other"],
                )
            with c2:
                phone = st.text_input("Contact")
                notes = st.text_area("Notes")

            if st.button("ADD PERSON", type="primary"):
                if name.strip():
                    add_person(case["id"], name.strip(), role, phone.strip(), notes.strip())
                    st.success("Person linked to the active case.")
                    st.rerun()
                else:
                    st.error("Name is required.")

        persons = [x for x in db["persons"] if x["case_id"] == case["id"]]
        if persons:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "ID": x["id"],
                            "Name": x["name"],
                            "Role": x["role"],
                            "Contact": x["phone"],
                            "Notes": x["notes"],
                        }
                        for x in persons
                    ]
                ),
                width="stretch",
                hide_index=True,
            )
        else:
            st.info("No persons linked to this case.")


# ============================================================
# EVIDENCE
# ============================================================
elif page == "Evidence":
    st.markdown("### EVIDENCE VAULT")

    if not case:
        st.warning("Create/select a case first.")
    else:
        persons = [x for x in db["persons"] if x["case_id"] == case["id"]]

        with st.expander("➕ Register Evidence", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Evidence title")
                kind = st.selectbox(
                    "Type",
                    ["Image", "Document", "Video", "Observation", "Statement", "Other"],
                )
                source = st.text_input("Source")
            with c2:
                description = st.text_area("Description")
                person_labels = ["— None —"] + [f'{p["id"]} — {p["name"]}' for p in persons]
                person_label = st.selectbox("Link to person", person_labels)

            if st.button("REGISTER EVIDENCE", type="primary"):
                if title.strip():
                    linked_person = "" if person_label == "— None —" else person_label.split(" — ")[0]
                    add_evidence(
                        case["id"],
                        title.strip(),
                        kind,
                        source.strip(),
                        description.strip(),
                        linked_person,
                    )
                    st.success("Evidence registered and linked to this case.")
                    st.rerun()
                else:
                    st.error("Evidence title is required.")

        evidence = [x for x in db["evidence"] if x["case_id"] == case["id"]]
        if evidence:
            rows = []
            for x in evidence:
                linked = get_person_name(x["linked_person"])
                rows.append(
                    {
                        "ID": x["id"],
                        "Title": x["title"],
                        "Type": x["kind"],
                        "Source": x["source"],
                        "Linked Person": linked,
                        "Created": x["created"],
                    }
                )
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        else:
            st.info("No evidence registered yet.")


# ============================================================
# CLUES
# ============================================================
elif page == "Clues":
    st.markdown("### CLUE TRACKER")

    if not case:
        st.warning("Create/select a case first.")
    else:
        with st.expander("➕ Add Clue", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Clue title")
                strength = st.selectbox("Strength", ["Weak", "Moderate", "Strong", "Critical"])
            with c2:
                status = st.selectbox("Status", ["Open", "Verified", "Disputed", "Closed"])
                description = st.text_area("Why is this clue important?")

            if st.button("ADD CLUE", type="primary"):
                if title.strip():
                    add_clue(
                        case["id"], title.strip(), strength, status, description.strip()
                    )
                    st.success("Clue connected to the case.")
                    st.rerun()
                else:
                    st.error("Clue title is required.")

        clues = [x for x in db["clues"] if x["case_id"] == case["id"]]
        if clues:
            for x in clues:
                with st.container(border=True):
                    a, b, c = st.columns([2.5, 1, 1])
                    with a:
                        st.markdown(f"**{x['title']}**")
                        st.caption(x["description"])
                    with b:
                        st.metric("Strength", x["strength"])
                    with c:
                        st.metric("Status", x["status"])
        else:
            st.info("No clues yet.")


# ============================================================
# INVESTIGATION BOARD
# ============================================================
elif page == "Investigation Board":
    st.markdown("### 🧩 INVESTIGATION BOARD")
    st.caption("This is the main connection layer. Add evidence/person/clue/event links to form an investigation graph.")

    if not case:
        st.warning("Create/select a case first.")
    else:
        all_items = []
        for x in db["persons"]:
            if x["case_id"] == case["id"]:
                all_items.append((f"Person | {x['id']} | {x['name']}", "Person", x["id"]))
        for x in db["evidence"]:
            if x["case_id"] == case["id"]:
                all_items.append((f"Evidence | {x['id']} | {x['title']}", "Evidence", x["id"]))
        for x in db["clues"]:
            if x["case_id"] == case["id"]:
                all_items.append((f"Clue | {x['id']} | {x['title']}", "Clue", x["id"]))
        for x in db["timeline"]:
            if x["case_id"] == case["id"]:
                all_items.append((f"Event | {x['id']} | {x['title']}", "Timeline", x["id"]))

        if all_items:
            with st.expander("➕ Create Connection", expanded=True):
                labels = [x[0] for x in all_items]
                label_to_item = {x[0]: x for x in all_items}
                source_label = st.selectbox("Select item", labels, key="board_source")
                note = st.text_input("Connection note", placeholder="e.g. same time window / same person / corroborates")
                if st.button("ADD TO BOARD", type="primary"):
                    _, item_type, item_id = label_to_item[source_label]
                    add_board_item(case["id"], item_type, item_id, note.strip())
                    st.success("Item added to investigation board.")
                    st.rerun()

        board = [x for x in db["board"] if x["case_id"] == case["id"]]
        if board:
            for x in board:
                with st.container(border=True):
                    st.markdown(
                        f"**{x['item_type']} · {x['item_id']}**  \n{x['note'] or 'No connection note.'}"
                    )
        else:
            st.info("Board is empty. Add linked items above.")

        st.markdown("#### Automatic Relationship View")
        persons = [x for x in db["persons"] if x["case_id"] == case["id"]]
        evidence = [x for x in db["evidence"] if x["case_id"] == case["id"]]
        clues = [x for x in db["clues"] if x["case_id"] == case["id"]]

        rel_rows = []
        for e in evidence:
            rel_rows.append(
                {
                    "Evidence": e["title"],
                    "Linked Person": get_person_name(e["linked_person"]),
                    "Case": case["id"],
                }
            )
        for c in clues:
            rel_rows.append(
                {
                    "Evidence": c["title"],
                    "Linked Person": "—",
                    "Case": case["id"],
                }
            )

        if rel_rows:
            st.dataframe(pd.DataFrame(rel_rows), width="stretch", hide_index=True)
        else:
            st.info("Add evidence and clues to populate relationships.")


# ============================================================
# TIMELINE
# ============================================================
elif page == "Timeline":
    st.markdown("### 🕐 CASE TIMELINE")

    if not case:
        st.warning("Create/select a case first.")
    else:
        with st.expander("➕ Add Timeline Event", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Event title")
                date_text = st.text_input(
                    "Date/time",
                    value=datetime.now().strftime("%Y-%m-%d %H:%M"),
                )
            with c2:
                location = st.text_input("Location")
                description = st.text_area("Event description")

            if st.button("ADD EVENT", type="primary"):
                if title.strip():
                    add_event(
                        case["id"],
                        title.strip(),
                        date_text.strip(),
                        location.strip(),
                        description.strip(),
                    )
                    st.success("Timeline event linked to the case.")
                    st.rerun()
                else:
                    st.error("Event title is required.")

        events = [x for x in db["timeline"] if x["case_id"] == case["id"]]
        if events:
            events = sorted(events, key=lambda x: x["date"])
            for x in events:
                with st.container(border=True):
                    st.markdown(f"**{x['date']} — {x['title']}**")
                    st.caption(f"📍 {x['location']}  |  {x['description']}")
        else:
            st.info("No timeline events yet.")


# ============================================================
# LOCATIONS
# ============================================================
elif page == "Locations":
    st.markdown("### 📍 LOCATIONS")

    if not case:
        st.warning("Create/select a case first.")
    else:
        with st.expander("➕ Add Location", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Location name")
                address = st.text_input("Address / area")
            with c2:
                category = st.selectbox(
                    "Location type", ["Scene", "Residence", "Workplace", "Meeting", "Other"]
                )
                notes = st.text_area("Notes")

            if st.button("ADD LOCATION", type="primary"):
                if name.strip():
                    add_location(
                        case["id"], name.strip(), address.strip(), category, notes.strip()
                    )
                    st.success("Location linked to the active case.")
                    st.rerun()
                else:
                    st.error("Location name is required.")

        locations = [x for x in db["locations"] if x["case_id"] == case["id"]]
        if locations:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "ID": x["id"],
                            "Name": x["name"],
                            "Address": x["address"],
                            "Type": x["category"],
                            "Notes": x["notes"],
                        }
                        for x in locations
                    ]
                ),
                width="stretch",
                hide_index=True,
            )
        else:
            st.info("No locations yet.")


# ============================================================
# IMAGE INTELLIGENCE / YOLO
# ============================================================
elif page == "Image Intelligence":
    st.markdown("### 🖼️ IMAGE INTELLIGENCE")
    st.caption("Optional YOLO object detection. This does NOT identify people by face or perform celebrity recognition.")

    if YOLO is None:
        st.error("Ultralytics could not be imported. Check requirements.txt.")
    else:
        confidence = st.slider(
            "Detection confidence",
            min_value=0.10,
            max_value=0.95,
            value=0.35,
            step=0.05,
        )

        uploaded = st.file_uploader(
            "Upload evidence image",
            type=["jpg", "jpeg", "png"],
        )

        if uploaded:
            image = Image.open(uploaded).convert("RGB")
            st.image(image, caption="Original evidence", width="stretch")

            if st.button("RUN YOLO ANALYSIS", type="primary"):
                try:
                    with st.spinner("Loading YOLO model and running inference..."):
                        @st.cache_resource
                        def load_yolo():
                            return YOLO("yolov8n.pt")

                        model = load_yolo()
                        result = model(
                            np.array(image),
                            conf=confidence,
                            verbose=False,
                        )[0]

                    plotted = result.plot()
                    detected_image = Image.fromarray(plotted[..., ::-1])

                    boxes = result.boxes
                    detected_count = len(boxes)
                    names = [
                        model.names[int(box.cls[0])]
                        for box in boxes
                    ]
                    confs = [
                        float(box.conf[0])
                        for box in boxes
                    ]

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Objects detected", detected_count)
                    c2.metric("Unique classes", len(set(names)))
                    c3.metric(
                        "Average confidence",
                        f"{(sum(confs) / len(confs) * 100) if confs else 0:.1f}%",
                    )

                    st.image(
                        detected_image,
                        caption="YOLO detection result",
                        width="stretch",
                    )

                    if detected_count:
                        counts = Counter(names)
                        rows = [
                            {
                                "Object": name,
                                "Count": qty,
                                "Max Confidence": f"{max(
                                    [confs[i] for i, n in enumerate(names) if n == name]
                                ) * 100:.1f}%",
                            }
                            for name, qty in counts.items()
                        ]
                        st.dataframe(
                            pd.DataFrame(rows),
                            width="stretch",
                            hide_index=True,
                        )

                        if case:
                            st.divider()
                            st.markdown("#### Connect YOLO Result to Active Case")
                            evidence_title = st.text_input(
                                "Evidence record title",
                                value=f"YOLO analysis — {uploaded.name}",
                            )
                            if st.button("SAVE YOLO RESULT AS EVIDENCE"):
                                object_text = ", ".join(
                                    f"{k} ({v})" for k, v in counts.items()
                                )
                                add_evidence(
                                    case["id"],
                                    evidence_title.strip() or f"YOLO analysis — {uploaded.name}",
                                    "AI Image Analysis",
                                    uploaded.name,
                                    f"Detected objects: {object_text}. Average confidence: {(sum(confs) / len(confs) * 100):.1f}%.",
                                )
                                st.success(
                                    "YOLO result saved as evidence and linked to the active case."
                                )
                                st.rerun()
                    else:
                        st.info("No objects detected at the selected confidence threshold.")

                except Exception as exc:
                    st.error(f"YOLO inference failed: {exc}")


# ============================================================
# ANALYTICS
# ============================================================
elif page == "Analytics":
    st.markdown("### 📊 INVESTIGATION ANALYTICS")

    if not db["cases"]:
        st.info("Create cases to see analytics.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Cases", len(db["cases"]))
        c2.metric("Evidence", len(db["evidence"]))
        c3.metric("Persons", len(db["persons"]))
        c4.metric("Clues", len(db["clues"]))

        st.write("")

        case_stats = []
        for c in db["cases"]:
            counts = case_counts(c["id"])
            case_stats.append(
                {
                    "Case": c["id"],
                    "Title": c["title"],
                    "Persons": counts["persons"],
                    "Evidence": counts["evidence"],
                    "Clues": counts["clues"],
                    "Timeline": counts["timeline"],
                    "Locations": counts["locations"],
                }
            )

        st.dataframe(
            pd.DataFrame(case_stats),
            width="stretch",
            hide_index=True,
        )

        st.markdown("#### Priority Distribution")
        priority_counts = Counter(c["priority"] for c in db["cases"])
        st.bar_chart(pd.DataFrame.from_dict(priority_counts, orient="index", columns=["Cases"]))


# ============================================================
# REPORT
# ============================================================
elif page == "Report":
    st.markdown("### 📄 CASE REPORT")

    if not case:
        st.warning("Create/select a case first.")
    else:
        counts = case_counts(case["id"])
        report = {
            "generated_at": now_text(),
            "case": case,
            "persons": [x for x in db["persons"] if x["case_id"] == case["id"]],
            "evidence": [x for x in db["evidence"] if x["case_id"] == case["id"]],
            "clues": [x for x in db["clues"] if x["case_id"] == case["id"]],
            "timeline": [x for x in db["timeline"] if x["case_id"] == case["id"]],
            "locations": [x for x in db["locations"] if x["case_id"] == case["id"]],
            "investigation_board": [x for x in db["board"] if x["case_id"] == case["id"]],
        }

        st.markdown(
            f"""
            <div class="panel">
                <h2>{case["title"]}</h2>
                <p>{case["summary"]}</p>
                <div class="mono">CASE // {case["id"]}</div>
                <div class="mono">STATUS // {case["status"]}</div>
                <div class="mono">PRIORITY // {case["priority"]}</div>
                <br>
                <div class="mono">PERSONS {counts["persons"]} · EVIDENCE {counts["evidence"]} · CLUES {counts["clues"]} · EVENTS {counts["timeline"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.json(report)

        st.download_button(
            "DOWNLOAD CASE REPORT (JSON)",
            data=json.dumps(report, indent=2, ensure_ascii=False),
            file_name=f"{case['id']}_report.json",
            mime="application/json",
            width="stretch",
        )


# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(
    "CID Intelligence Hub • Demo investigation management system • "
    "YOLO is used only for closed-set object detection; it does not identify people."
)
