import json
from datetime import datetime
from collections import Counter

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CID AI Investigation System",
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
            radial-gradient(circle at 10% 10%, rgba(0,229,255,.08), transparent 24%),
            radial-gradient(circle at 90% 15%, rgba(124,58,237,.09), transparent 25%),
            linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px),
            #070b12;
        background-size: auto, auto, 38px 38px, 38px 38px;
        color: #e8eef7;
    }

    html, body, [class*="css"] {
        font-family: Inter, sans-serif;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: #080d15;
        border-right: 1px solid rgba(148,163,184,.12);
    }

    .hero {
        border: 1px solid rgba(0,229,255,.18);
        background:
            linear-gradient(135deg, rgba(10,18,31,.95), rgba(10,14,25,.80));
        border-radius: 22px;
        padding: 30px 34px;
        margin-bottom: 22px;
        box-shadow:
            0 0 50px rgba(0,229,255,.06),
            inset 0 1px rgba(255,255,255,.04);
    }

    .eyebrow {
        color: #00e5ff;
        font-family: 'Space Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
    }

    .hero h1 {
        font-size: 42px;
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
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: inset 0 1px rgba(255,255,255,.025);
    }

    .panel-title {
        font-weight: 800;
        font-size: 14px;
        letter-spacing: .5px;
        margin-bottom: 14px;
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
        padding: 16px;
        text-align: center;
        min-height: 88px;
    }

    .metric .value {
        font-family: 'Space Mono', monospace;
        font-weight: 800;
        font-size: 25px;
        color: #eaf7ff;
    }

    .metric .label {
        color: #718198;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 5px;
    }

    .finding {
        border-left: 3px solid #00e5ff;
        background: rgba(0,229,255,.045);
        padding: 12px 15px;
        border-radius: 8px;
        margin: 8px 0;
    }

    .finding-title {
        font-weight: 700;
        font-size: 13px;
    }

    .finding-text {
        color: #9fb0c4;
        font-size: 12px;
        margin-top: 4px;
    }

    .tag {
        display: inline-block;
        padding: 4px 8px;
        margin: 2px;
        border: 1px solid rgba(0,229,255,.2);
        border-radius: 999px;
        color: #7dd3fc;
        font-family: 'Space Mono', monospace;
        font-size: 10px;
    }

    .status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: #a7f3d0;
        font-family: 'Space Mono', monospace;
        font-size: 11px;
    }

    .dot {
        width: 8px;
        height: 8px;
        background: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 12px #22c55e;
    }

    .section-title {
        font-size: 18px;
        font-weight: 800;
        margin: 22px 0 12px;
    }

    .big-number {
        font-family: 'Space Mono', monospace;
        font-size: 34px;
        font-weight: 800;
    }

    div[data-testid="stFileUploaderDropzone"] {
        background: rgba(8,15,25,.72);
        border: 1px dashed rgba(0,229,255,.35);
        border-radius: 16px;
    }

    .stButton button {
        border-radius: 10px;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "case" not in st.session_state:
    st.session_state.case = None

if "yolo_model" not in st.session_state:
    st.session_state.yolo_model = None

if "yolo_error" not in st.session_state:
    st.session_state.yolo_error = None

if "detected_image" not in st.session_state:
    st.session_state.detected_image = None

if "detection_rows" not in st.session_state:
    st.session_state.detection_rows = []

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None


# ============================================================
# HELPERS
# ============================================================

def now_string():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def make_case_id():
    return "CID-" + datetime.now().strftime("%Y%m%d-%H%M%S")


def create_demo_case():
    timestamp = now_string()

    return {
        "case_id": "CID-DEMO-001",
        "title": "Warehouse Night Incident",
        "status": "ACTIVE",
        "priority": "HIGH",
        "location": "Sector 17 Industrial Warehouse",
        "created_at": timestamp,
        "investigator": "AI Investigation Unit",

        "evidence": [
            {
                "id": "EV-001",
                "type": "Image",
                "name": "warehouse_scene.jpg",
                "source": "CCTV Frame",
                "status": "ANALYZED",
            },
            {
                "id": "EV-002",
                "type": "Document",
                "name": "incident_report.pdf",
                "source": "Case File",
                "status": "LINKED",
            },
        ],

        "persons": [
            {
                "id": "PER-001",
                "name": "Person #1",
                "role": "Unknown",
                "status": "UNIDENTIFIED",
            },
            {
                "id": "PER-002",
                "name": "Person #2",
                "role": "Unknown",
                "status": "UNIDENTIFIED",
            },
        ],

        "objects": [
            {
                "id": "OBJ-001",
                "name": "Person",
                "source": "EV-001",
                "confidence": 0.91,
            },
            {
                "id": "OBJ-002",
                "name": "Person",
                "source": "EV-001",
                "confidence": 0.87,
            },
            {
                "id": "OBJ-003",
                "name": "Car",
                "source": "EV-001",
                "confidence": 0.84,
            },
            {
                "id": "OBJ-004",
                "name": "Backpack",
                "source": "EV-001",
                "confidence": 0.78,
            },
        ],

        "clues": [
            {
                "id": "CL-001",
                "title": "Multiple persons detected",
                "priority": "HIGH",
                "source": "EV-001",
            },
            {
                "id": "CL-002",
                "title": "Vehicle present near scene",
                "priority": "MEDIUM",
                "source": "EV-001",
            },
            {
                "id": "CL-003",
                "title": "Backpack detected",
                "priority": "MEDIUM",
                "source": "EV-001",
            },
        ],

        "findings": [
            {
                "id": "AI-001",
                "title": "Multiple individuals detected",
                "text": "Computer vision detected two person instances in the submitted evidence.",
                "severity": "HIGH",
            },
            {
                "id": "AI-002",
                "title": "Vehicle associated with scene",
                "text": "A vehicle was detected in the same visual frame as the identified persons.",
                "severity": "MEDIUM",
            },
            {
                "id": "AI-003",
                "title": "Portable object detected",
                "text": "A backpack-like object was detected and linked to the evidence frame.",
                "severity": "MEDIUM",
            },
        ],

        "timeline": [
            {
                "time": "22:14",
                "event": "CCTV frame captured",
                "source": "EV-001",
            },
            {
                "time": "22:16",
                "event": "Evidence imported into case",
                "source": "SYSTEM",
            },
            {
                "time": "22:17",
                "event": "YOLO visual analysis completed",
                "source": "AI ENGINE",
            },
            {
                "time": "22:18",
                "event": "AI findings generated",
                "source": "AI ENGINE",
            },
        ],
    }


def load_yolo():
    if st.session_state.yolo_model is not None:
        return st.session_state.yolo_model

    try:
        from ultralytics import YOLO

        with st.spinner("Loading YOLO vision engine..."):
            model = YOLO("yolov8n.pt")

        st.session_state.yolo_model = model
        st.session_state.yolo_error = None
        return model

    except Exception as exc:
        st.session_state.yolo_error = str(exc)
        return None


def generate_findings_from_detections(detection_rows):
    findings = []

    if not detection_rows:
        return [
            {
                "id": "AI-001",
                "title": "No objects detected",
                "text": "No object passed the current confidence threshold.",
                "severity": "LOW",
            }
        ]

    counts = Counter(row["Object"] for row in detection_rows)

    finding_number = 1

    for object_name, quantity in counts.items():
        severity = "MEDIUM"

        if object_name.lower() == "person":
            severity = "HIGH"

        if quantity >= 3:
            severity = "HIGH"

        findings.append(
            {
                "id": f"AI-{finding_number:03d}",
                "title": f"{quantity} × {object_name} detected",
                "text": (
                    f"YOLO detected {quantity} instance(s) of "
                    f"{object_name.lower()} in the submitted evidence."
                ),
                "severity": severity,
            }
        )

        finding_number += 1

    if "person" in {name.lower() for name in counts} and (
        "car" in {name.lower() for name in counts}
        or "truck" in {name.lower() for name in counts}
        or "motorcycle" in {name.lower() for name in counts}
    ):
        findings.append(
            {
                "id": f"AI-{finding_number:03d}",
                "title": "Person + vehicle co-occurrence",
                "text": (
                    "A person and vehicle were detected in the same evidence "
                    "frame. This relationship has been added as an investigative clue."
                ),
                "severity": "HIGH",
            }
        )

    return findings


def analyze_image(image, confidence):
    model = load_yolo()

    if model is None:
        return None, []

    with st.spinner("Running YOLO visual analysis..."):
        results = model(
            np.array(image),
            conf=confidence,
            verbose=False,
        )

    result = results[0]

    plotted = result.plot()

    plotted_rgb = plotted[..., ::-1]
    output_image = Image.fromarray(plotted_rgb)

    rows = []

    if result.boxes is not None:
        for index, box in enumerate(result.boxes, start=1):
            class_id = int(box.cls[0])
            object_name = model.names[class_id]
            confidence_value = float(box.conf[0])

            rows.append(
                {
                    "#": index,
                    "Object": object_name,
                    "Confidence": f"{confidence_value * 100:.1f}%",
                }
            )

    return output_image, rows


def ensure_case():
    if st.session_state.case is None:
        st.session_state.case = {
            "case_id": make_case_id(),
            "title": "New Investigation",
            "status": "ACTIVE",
            "priority": "MEDIUM",
            "location": "Not specified",
            "created_at": now_string(),
            "investigator": "CID AI Unit",
            "evidence": [],
            "persons": [],
            "objects": [],
            "clues": [],
            "findings": [],
            "timeline": [],
        }


def add_yolo_results_to_case(filename, detection_rows):
    ensure_case()

    case = st.session_state.case

    evidence_id = f"EV-{len(case['evidence']) + 1:03d}"

    case["evidence"].append(
        {
            "id": evidence_id,
            "type": "Image",
            "name": filename,
            "source": "Uploaded Evidence",
            "status": "ANALYZED",
        }
    )

    object_start = len(case["objects"]) + 1

    for offset, row in enumerate(detection_rows):
        confidence_text = row["Confidence"].replace("%", "")
        confidence_value = float(confidence_text) / 100

        case["objects"].append(
            {
                "id": f"OBJ-{object_start + offset:03d}",
                "name": row["Object"],
                "source": evidence_id,
                "confidence": confidence_value,
            }
        )

    new_findings = generate_findings_from_detections(detection_rows)

    for finding in new_findings:
        finding["id"] = f"AI-{len(case['findings']) + 1:03d}"
        case["findings"].append(finding)

    unique_objects = Counter(row["Object"] for row in detection_rows)

    for object_name, quantity in unique_objects.items():
        clue_id = f"CL-{len(case['clues']) + 1:03d}"

        priority = "HIGH" if object_name.lower() == "person" else "MEDIUM"

        case["clues"].append(
            {
                "id": clue_id,
                "title": f"{quantity} × {object_name} detected",
                "priority": priority,
                "source": evidence_id,
            }
        )

    case["timeline"].append(
        {
            "time": datetime.now().strftime("%H:%M"),
            "event": f"YOLO analyzed {filename}",
            "source": evidence_id,
        }
    )

    case["timeline"].append(
        {
            "time": datetime.now().strftime("%H:%M"),
            "event": f"{len(detection_rows)} detection(s) converted into investigation data",
            "source": "AI ENGINE",
        }
    )


def case_json():
    ensure_case()
    return json.dumps(st.session_state.case, indent=2, ensure_ascii=False)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🕵️ CID AI CONTROL")
    st.caption("Computer-Assisted Investigation Dashboard")
    st.divider()

    st.markdown(
        '<div class="status"><span class="dot"></span> SYSTEM ONLINE</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    page = st.radio(
        "NAVIGATION",
        [
            "Command Center",
            "Evidence Intelligence",
            "Investigation Graph",
            "Timeline",
            "Case Report",
        ],
    )

    st.divider()

    confidence = st.slider(
        "YOLO Confidence",
        min_value=0.10,
        max_value=0.95,
        value=0.35,
        step=0.05,
    )

    st.caption("Lower threshold = more detections.")

    st.divider()

    if st.button("⚡ LOAD DEMO CASE", width="stretch"):
        st.session_state.case = create_demo_case()
        st.session_state.detected_image = None
        st.session_state.detection_rows = []
        st.session_state.uploaded_filename = None
        st.rerun()

    if st.button("＋ NEW EMPTY CASE", width="stretch"):
        st.session_state.case = None
        st.session_state.detected_image = None
        st.session_state.detection_rows = []
        st.session_state.uploaded_filename = None
        st.rerun()

    st.divider()

    st.markdown(
        '<div class="mono">ENGINE // YOLOv8n</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="mono">MODE // OBJECT DETECTION</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="mono">PIPELINE // IMAGE → AI → CASE</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">CID / AI INVESTIGATION PLATFORM / LIVE SYSTEM</div>
        <h1>Command Investigation Intelligence</h1>
        <p>
            An interconnected investigation dashboard where evidence,
            computer vision, objects, clues, findings and timeline events
            automatically connect to the active case.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# COMMAND CENTER
# ============================================================

if page == "Command Center":

    if st.session_state.case is None:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">NO ACTIVE CASE</div>
                <div class="muted">
                    Start with <b>LOAD DEMO CASE</b> for an instant investigation
                    scenario, or create an empty case.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        a, b, c = st.columns(3)

        with a:
            st.metric("System", "ONLINE")

        with b:
            st.metric("AI Engine", "READY")

        with c:
            st.metric("Case", "NONE")

    else:
        case = st.session_state.case

        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-title">ACTIVE CASE</div>
                <div class="mono">{case['case_id']}</div>
                <h2 style="margin-bottom:4px;">{case['title']}</h2>
                <div class="muted">
                    {case['location']} · Priority: {case['priority']} ·
                    Investigator: {case['investigator']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### LIVE CASE OVERVIEW")

        metrics = [
            ("Evidence", len(case["evidence"])),
            ("Persons", len(case["persons"])),
            ("Objects", len(case["objects"])),
            ("Clues", len(case["clues"])),
            ("AI Findings", len(case["findings"])),
            ("Timeline Events", len(case["timeline"])),
        ]

        metric_cols = st.columns(6)

        for col, (label, value) in zip(metric_cols, metrics):
            with col:
                st.markdown(
                    f"""
                    <div class="metric">
                        <div class="value">{value}</div>
                        <div class="label">{label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.write("")

        left, right = st.columns([1.15, 1], gap="large")

        with left:
            st.markdown(
                '<div class="panel"><div class="panel-title">🧠 AI FINDINGS</div>',
                unsafe_allow_html=True,
            )

            if case["findings"]:
                for finding in case["findings"]:
                    st.markdown(
                        f"""
                        <div class="finding">
                            <div class="finding-title">
                                {finding['id']} · {finding['title']}
                            </div>
                            <div class="finding-text">
                                {finding['text']}
                            </div>
                            <div class="tag">{finding['severity']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No AI findings yet.")

            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown(
                '<div class="panel"><div class="panel-title">🔗 CASE CONNECTIONS</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="mono">
                CASE<br>
                ↓<br>
                {len(case['evidence'])} EVIDENCE ITEMS<br>
                ↓<br>
                {len(case['objects'])} DETECTED OBJECTS<br>
                ↓<br>
                {len(case['clues'])} CLUES<br>
                ↓<br>
                {len(case['findings'])} AI FINDINGS<br>
                ↓<br>
                {len(case['timeline'])} TIMELINE EVENTS
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### RECENT INVESTIGATION EVENTS")

        if case["timeline"]:
            timeline_df = pd.DataFrame(case["timeline"][-6:])
            st.dataframe(
                timeline_df,
                width="stretch",
                hide_index=True,
            )


# ============================================================
# EVIDENCE INTELLIGENCE
# ============================================================

elif page == "Evidence Intelligence":

    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">📸 AI EVIDENCE INTELLIGENCE</div>
            <div class="muted">
                Upload an evidence image. YOLO analyzes it and automatically
                inserts detections, clues, findings and timeline events into
                the active investigation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ensure_case()

    uploaded_file = st.file_uploader(
        "Upload evidence image",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file).convert("RGB")

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown(
                '<div class="panel"><div class="panel-title">ORIGINAL EVIDENCE</div>',
                unsafe_allow_html=True,
            )
            st.image(image, width="stretch")
            st.markdown("</div>", unsafe_allow_html=True)

        if st.button("🧠 RUN AI INVESTIGATION", type="primary", width="stretch"):

            output_image, rows = analyze_image(
                image,
                confidence,
            )

            if output_image is not None:

                st.session_state.detected_image = output_image
                st.session_state.detection_rows = rows
                st.session_state.uploaded_filename = uploaded_file.name

                add_yolo_results_to_case(
                    uploaded_file.name,
                    rows,
                )

                st.success(
                    f"AI investigation completed — {len(rows)} object(s) detected and linked to the case."
                )

        with col2:
            st.markdown(
                '<div class="panel"><div class="panel-title">YOLO DETECTION FRAME</div>',
                unsafe_allow_html=True,
            )

            if st.session_state.detected_image is not None:
                st.image(
                    st.session_state.detected_image,
                    width="stretch",
                )
            else:
                st.info("Run AI Investigation to analyze this evidence.")

            st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.yolo_error:
        st.error(
            "YOLO could not be loaded. "
            + st.session_state.yolo_error
        )

    if st.session_state.detection_rows:

        st.markdown("### DETECTION RESULTS")

        rows = st.session_state.detection_rows

        count = len(rows)
        classes = Counter(row["Object"] for row in rows)

        a, b, c = st.columns(3)

        with a:
            st.markdown(
                f"""
                <div class="metric">
                    <div class="value">{count}</div>
                    <div class="label">Objects Detected</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with b:
            st.markdown(
                f"""
                <div class="metric">
                    <div class="value">{len(classes)}</div>
                    <div class="label">Unique Classes</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c:
            confidence_values = [
                float(row["Confidence"].replace("%", ""))
                for row in rows
            ]

            avg = sum(confidence_values) / len(confidence_values)

            st.markdown(
                f"""
                <div class="metric">
                    <div class="value">{avg:.1f}%</div>
                    <div class="label">Average Confidence</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")

        st.dataframe(
            pd.DataFrame(rows),
            width="stretch",
            hide_index=True,
        )

        st.markdown("### AUTOMATICALLY GENERATED FINDINGS")

        for finding in st.session_state.case["findings"][-10:]:
            st.markdown(
                f"""
                <div class="finding">
                    <div class="finding-title">
                        {finding['id']} · {finding['title']}
                    </div>
                    <div class="finding-text">
                        {finding['text']}
                    </div>
                    <span class="tag">{finding['severity']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# INVESTIGATION GRAPH
# ============================================================

elif page == "Investigation Graph":

    ensure_case()

    case = st.session_state.case

    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">🕸️ INTERCONNECTED INVESTIGATION GRAPH</div>
            <div class="muted">
                This view shows how case entities connect to evidence,
                detections, clues and AI findings.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    graph_rows = []

    graph_rows.append(
        {
            "From": case["case_id"],
            "Relationship": "contains",
            "To": f"{len(case['evidence'])} evidence item(s)",
        }
    )

    for evidence in case["evidence"]:
        graph_rows.append(
            {
                "From": case["case_id"],
                "Relationship": "contains",
                "To": evidence["id"],
            }
        )

    for obj in case["objects"]:
        graph_rows.append(
            {
                "From": obj["source"],
                "Relationship": "detected",
                "To": f"{obj['id']} / {obj['name']}",
            }
        )

    for clue in case["clues"]:
        graph_rows.append(
            {
                "From": clue["source"],
                "Relationship": "produces clue",
                "To": f"{clue['id']} / {clue['title']}",
            }
        )

    for finding in case["findings"]:
        graph_rows.append(
            {
                "From": "AI ENGINE",
                "Relationship": "generates",
                "To": f"{finding['id']} / {finding['title']}",
            }
        )

    st.dataframe(
        pd.DataFrame(graph_rows),
        width="stretch",
        hide_index=True,
    )

    st.markdown("### VISUAL CASE MAP")

    center = st.columns([1, 2, 1])

    with center[1]:
        st.markdown(
            f"""
            <div class="panel" style="text-align:center;">
                <div class="mono">ACTIVE CASE</div>
                <div class="big-number">{case['case_id']}</div>
                <div class="muted">{case['title']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div style="
            text-align:center;
            font-family:'Space Mono',monospace;
            color:#00e5ff;
            font-size:24px;
        ">
            ↓
        </div>
        """,
        unsafe_allow_html=True,
    )

   evidence_cols = st.columns(min(4, max(1, len(case["evidence"]))))

    if case["evidence"]:
    evidence_cols = st.columns(
        min(4, max(1, len(case["evidence"])))
    )

    for i, evidence in enumerate(case["evidence"]):
        with evidence_cols[i % len(evidence_cols)]:
            st.markdown(
                f"""
                <div class="metric">
                    <div class="value">{evidence}</div>
                    <div class="label">Evidence</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### DETECTED ENTITIES")

    if case["objects"]:
        object_counts = Counter(
            obj["name"] for obj in case["objects"]
        )

        cols = st.columns(
            min(5, max(1, len(object_counts)))
        )

        for i, (name, quantity) in enumerate(object_counts.items()):
            with cols[i % len(cols)]:
                st.markdown(
                    f"""
                    <div class="metric">
                        <div class="value">{quantity}</div>
                        <div class="label">{name}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No detected objects yet.")


# ============================================================
# TIMELINE
# ============================================================

elif page == "Timeline":

    ensure_case()

    case = st.session_state.case

    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">🕐 INVESTIGATION TIMELINE</div>
            <div class="muted">
                Events are automatically added when evidence is analyzed.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not case["timeline"]:
        st.info("No timeline events yet.")
    else:
        for index, event in enumerate(case["timeline"], start=1):

            st.markdown(
                f"""
                <div class="finding">
                    <div class="mono">{event['time']} · EVENT {index:02d}</div>
                    <div class="finding-title">{event['event']}</div>
                    <div class="finding-text">
                        SOURCE: {event['source']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# CASE REPORT
# ============================================================

elif page == "Case Report":

    ensure_case()

    case = st.session_state.case

    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">📄 AI CASE REPORT</div>
            <div class="muted">
                Structured machine-readable investigation report.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### CASE SUMMARY")

    a, b, c, d = st.columns(4)

    with a:
        st.metric("Case ID", case["case_id"])

    with b:
        st.metric("Status", case["status"])

    with c:
        st.metric("Priority", case["priority"])

    with d:
        st.metric("Evidence", len(case["evidence"]))

    st.write("")

    st.markdown("### FINDINGS")

    if case["findings"]:
        for finding in case["findings"]:
            st.markdown(
                f"""
                <div class="finding">
                    <div class="finding-title">
                        {finding['id']} · {finding['title']}
                    </div>
                    <div class="finding-text">
                        {finding['text']}
                    </div>
                    <span class="tag">{finding['severity']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No findings available.")

    st.markdown("### EVIDENCE")

    if case["evidence"]:
        st.dataframe(
            pd.DataFrame(case["evidence"]),
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("No evidence.")

    st.markdown("### CLUES")

    if case["clues"]:
        st.dataframe(
            pd.DataFrame(case["clues"]),
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("No clues.")

    st.markdown("### RAW CASE JSON")

    st.code(
        case_json(),
        language="json",
    )

    st.download_button(
        "⬇️ DOWNLOAD CASE REPORT",
        data=case_json(),
        file_name=f"{case['case_id']}_report.json",
        mime="application/json",
        width="stretch",
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        margin-top:45px;
        color:#526277;
        font-family:'Space Mono',monospace;
        font-size:10px;
    ">
        CID AI INVESTIGATION SYSTEM · COMPUTER VISION ASSISTANCE ·
        YOLO OBJECT DETECTION · DEMONSTRATION PLATFORM
    </div>
    """,
    unsafe_allow_html=True,
)
