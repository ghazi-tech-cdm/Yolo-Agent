import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import pandas as pd
from datetime import datetime
from collections import Counter


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Detective",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "investigation_count" not in st.session_state:
    st.session_state.investigation_count = 0


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap'
    );

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(0, 220, 255, 0.10),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 15%,
                rgba(120, 70, 255, 0.10),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #040711 0%,
                #07101d 50%,
                #03060c 100%
            );

        color: #eaf6ff;
        font-family: 'Inter', sans-serif;
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        opacity: 0.13;

        background-image:
            linear-gradient(
                rgba(255,255,255,0.025) 1px,
                transparent 1px
            ),
            linear-gradient(
                90deg,
                rgba(255,255,255,0.025) 1px,
                transparent 1px
            );

        background-size: 40px 40px;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #060b15 0%,
                #030711 100%
            );

        border-right:
            1px solid
            rgba(75, 210, 255, 0.14);
    }

    .brand {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .brand-symbol {
        color: #4ddcff;
    }

    .sidebar-subtitle {
        color: #688198;
        font-size: 11px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: -4px;
    }

    .hero {
        padding: 30px;
        border-radius: 24px;

        background:
            linear-gradient(
                135deg,
                rgba(8, 23, 40, 0.95),
                rgba(8, 12, 27, 0.92)
            );

        border:
            1px solid
            rgba(71, 213, 255, 0.20);

        box-shadow:
            0 0 50px
            rgba(0, 210, 255, 0.06);

        margin-bottom: 25px;
    }

    .eyebrow {
        color: #52dcff;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2.5px;
        text-transform: uppercase;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(34px, 5vw, 58px);
        font-weight: 700;
        line-height: 1.02;
        margin: 8px 0 12px 0;
        color: #f1f8ff;
    }

    .hero-description {
        max-width: 850px;
        color: #8ca4b9;
        font-size: 15px;
        line-height: 1.65;
    }

    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        color: #f0f7ff;
        font-size: 21px;
        font-weight: 700;
        margin-top: 28px;
        margin-bottom: 14px;
    }

    .metric {
        min-height: 110px;
        padding: 20px;
        border-radius: 18px;

        background:
            rgba(8, 17, 31, 0.78);

        border:
            1px solid
            rgba(115, 160, 195, 0.15);
    }

    .metric-label {
        color: #6e879d;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.4px;
    }

    .metric-value {
        color: #f4faff;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 30px;
        font-weight: 700;
        margin-top: 9px;
    }

    .module-card {
        min-height: 165px;
        padding: 22px;
        border-radius: 20px;

        background:
            rgba(7, 16, 29, 0.78);

        border:
            1px solid
            rgba(115, 160, 195, 0.14);
    }

    .module-icon {
        font-size: 30px;
    }

    .module-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 19px;
        font-weight: 700;
        margin-top: 10px;
    }

    .module-text {
        color: #71899f;
        font-size: 13px;
        line-height: 1.6;
        margin-top: 6px;
    }

    .panel {
        padding: 18px;
        border-radius: 20px;

        background:
            rgba(7, 14, 26, 0.78);

        border:
            1px solid
            rgba(115, 160, 195, 0.14);
    }

    .panel-title {
        color: #9ab1c4;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.7px;
        margin-bottom: 12px;
    }

    .evidence-card {
        padding: 18px;
        margin-bottom: 12px;
        border-radius: 16px;

        background:
            linear-gradient(
                135deg,
                rgba(8, 27, 41, 0.92),
                rgba(7, 15, 27, 0.82)
            );

        border:
            1px solid
            rgba(63, 215, 255, 0.18);
    }

    .evidence-label {
        color: #52dcff;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.4px;
    }

    .evidence-name {
        color: #f0f8ff;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 22px;
        font-weight: 700;
        margin-top: 5px;
    }

    .evidence-confidence {
        color: #72e7a7;
        font-size: 13px;
        margin-top: 5px;
    }

    .analysis-card {
        padding: 24px;
        border-radius: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(13, 39, 48, 0.70),
                rgba(8, 17, 29, 0.88)
            );

        border:
            1px solid
            rgba(67, 229, 182, 0.20);

        box-shadow:
            0 0 35px
            rgba(67, 229, 182, 0.04);
    }

    .analysis-title {
        color: #67efbb;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.8px;
    }

    .analysis-text {
        color: #d9e8f3;
        font-size: 15px;
        line-height: 1.75;
        margin-top: 10px;
    }

    .status-online {
        display: inline-block;
        color: #67efbb;
        background: rgba(67, 239, 187, 0.08);
        border: 1px solid rgba(67, 239, 187, 0.18);
        border-radius: 30px;
        padding: 5px 10px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .empty-state {
        padding: 45px;
        text-align: center;
        border-radius: 20px;

        background:
            rgba(7, 15, 27, 0.65);

        border:
            1px dashed
            rgba(110, 160, 190, 0.18);
    }

    .empty-icon {
        font-size: 40px;
        margin-bottom: 10px;
    }

    .empty-title {
        font-family: 'Space Grotesk', sans-serif;
        color: #dceaf5;
        font-size: 19px;
        font-weight: 700;
    }

    .empty-text {
        color: #687f94;
        font-size: 13px;
        margin-top: 7px;
    }

    .stButton > button {
        min-height: 44px;
        border-radius: 12px;

        background:
            rgba(14, 34, 52, 0.90);

        border:
            1px solid
            rgba(70, 213, 255, 0.22);

        color: #e2f8ff;
        font-weight: 700;
    }

    .stButton > button:hover {
        border-color:
            rgba(70, 213, 255, 0.55);

        color: white;
    }

    [data-testid="stFileUploader"] {
        border:
            1px dashed
            rgba(70, 213, 255, 0.32);

        border-radius: 18px;

        background:
            rgba(5, 16, 29, 0.60);

        padding: 8px;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# YOLO MODEL
# =========================================================

@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")


# =========================================================
# HELPERS
# =========================================================

def get_position(x1, y1, x2, y2, width, height):
    """
    Convert bounding box coordinates into a simple
    human-readable position.
    """

    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    horizontal = "center"
    vertical = "middle"

    if center_x < width * 0.33:
        horizontal = "left"

    elif center_x > width * 0.66:
        horizontal = "right"

    if center_y < height * 0.33:
        vertical = "top"

    elif center_y > height * 0.66:
        vertical = "bottom"

    if vertical == "middle":
        return horizontal

    return f"{vertical}-{horizontal}"


def create_local_analysis(detections):
    """
    Generate a deterministic local analysis using
    only actual YOLO detections.
    """

    if not detections:
        return (
            "No supported objects were detected in the "
            "image at the selected confidence threshold."
        )

    counts = Counter(
        item["object"]
        for item in detections
    )

    total = len(detections)

    object_parts = []

    for name, count in counts.most_common():

        if count == 1:
            object_parts.append(
                f"1 {name}"
            )
        else:
            object_parts.append(
                f"{count} {name}s"
            )

    if len(object_parts) == 1:

        description = object_parts[0]

    elif len(object_parts) == 2:

        description = (
            f"{object_parts[0]} and "
            f"{object_parts[1]}"
        )

    else:

        description = (
            ", ".join(object_parts[:-1])
            + ", and "
            + object_parts[-1]
        )

    highest = max(
        detections,
        key=lambda item: item["confidence"]
    )

    highest_confidence = (
        highest["confidence"] * 100
    )

    return (
        f"The visual scan detected {description}. "
        f"A total of {total} detection(s) were found. "
        f"The highest-confidence detection is "
        f"{highest['object']} at "
        f"{highest_confidence:.1f}% confidence."
    )


def run_investigation(image, confidence):
    """
    Run YOLO and convert detections into a clean
    application-friendly structure.
    """

    model = load_model()

    image_array = np.array(image)

    result = model(
        image_array,
        conf=confidence,
        verbose=False
    )[0]

    detections = []

    image_height, image_width = image_array.shape[:2]

    for box in result.boxes:

        class_id = int(
            box.cls[0]
        )

        confidence_score = float(
            box.conf[0]
        )

        coordinates = (
            box.xyxy[0]
            .cpu()
            .numpy()
            .tolist()
        )

        x1, y1, x2, y2 = coordinates

        object_name = model.names[
            class_id
        ]

        position = get_position(
            x1,
            y1,
            x2,
            y2,
            image_width,
            image_height
        )

        detections.append(
            {
                "object": object_name,
                "confidence": confidence_score,
                "position": position,
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2),
            }
        )

    annotated_array = result.plot()

    annotated_image = Image.fromarray(
        annotated_array[..., ::-1]
    )

    return (
        annotated_image,
        detections
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">
            <span class="brand-symbol">◈</span>
            AI DETECTIVE
        </div>

        <div class="sidebar-subtitle">
            Visual Investigation System
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        '<span class="status-online">'
        '● SYSTEM ONLINE'
        '</span>',
        unsafe_allow_html=True
    )

    st.markdown("")

    page = st.radio(
        "NAVIGATION",
        [
            "🏠 Command Center",
            "🔎 Investigate",
            "🧠 AI Analysis",
            "🕘 History",
        ]
    )

    st.divider()

    st.markdown(
        "### VISION CORE"
    )

    st.caption(
        "Engine: YOLOv8n"
    )

    st.caption(
        "Mode: Image Investigation"
    )

    st.caption(
        "AI: Local Analysis"
    )


# =========================================================
# COMMAND CENTER
# =========================================================

if page == "🏠 Command Center":

    st.markdown(
        """
        <div class="hero">

            <div class="eyebrow">
                AI / COMPUTER VISION / INVESTIGATION
            </div>

            <div class="hero-title">
                AI Detective
            </div>

            <div class="hero-description">
                Visual Investigation & Intelligence Platform.
                Upload an image, detect visual evidence,
                inspect objects and generate an AI-style
                investigation summary without requiring
                an external API.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">'
        'COMMAND CENTER'
        '</div>',
        unsafe_allow_html=True
    )

    total_detections = sum(
        item.get("detections", 0)
        for item in st.session_state.history
    )

    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        (
            "INVESTIGATIONS",
            len(st.session_state.history)
        ),
        (
            "IMAGES ANALYZED",
            len(st.session_state.history)
        ),
        (
            "OBJECTS DETECTED",
            total_detections
        ),
        (
            "VISION ENGINE",
            "YOLOv8n"
        ),
    ]

    for col, (
        label,
        value
    ) in zip(
        [c1, c2, c3, c4],
        metrics
    ):

        with col:

            st.markdown(
                f"""
                <div class="metric">

                    <div class="metric-label">
                        {label}
                    </div>

                    <div class="metric-value">
                        {value}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        '<div class="section-title">'
        'INVESTIGATION MODULES'
        '</div>',
        unsafe_allow_html=True
    )

    modules = [
        (
            "🔎",
            "INVESTIGATE",
            "Upload an image and turn it into visual evidence using YOLO object detection."
        ),
        (
            "🧠",
            "AI ANALYSIS",
            "Generate a local investigation summary from the objects actually detected."
        ),
        (
            "🕘",
            "HISTORY",
            "Review investigations performed during the current session."
        ),
    ]

    cols = st.columns(3)

    for col, (
        icon,
        title,
        description
    ) in zip(
        cols,
        modules
    ):

        with col:

            st.markdown(
                f"""
                <div class="module-card">

                    <div class="module-icon">
                        {icon}
                    </div>

                    <div class="module-title">
                        {title}
                    </div>

                    <div class="module-text">
                        {description}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    if st.session_state.history:

        st.markdown(
            '<div class="section-title">'
            'LATEST INVESTIGATION'
            '</div>',
            unsafe_allow_html=True
        )

        latest = (
            st.session_state.history[-1]
        )

        st.markdown(
            f"""
            <div class="panel">

                <div class="panel-title">
                    RECENT CASE
                </div>

                <b>{latest["id"]}</b>
                &nbsp;&nbsp;
                {latest["time"]}

                <br><br>

                {latest["summary"]}

            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="empty-state">

                <div class="empty-icon">
                    ◈
                </div>

                <div class="empty-title">
                    No investigations yet
                </div>

                <div class="empty-text">
                    Open Investigate and upload your first image.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# INVESTIGATE
# =========================================================

elif page == "🔎 Investigate":

    st.markdown(
        '<div class="section-title">'
        'VISUAL INVESTIGATION'
        '</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns(
        [1.7, 1]
    )

    with left:

        uploaded_file = st.file_uploader(
            "UPLOAD VISUAL EVIDENCE",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp"
            ],
            help="Upload a clear image containing objects you want to investigate."
        )

    with right:

        confidence = st.slider(
            "DETECTION CONFIDENCE",
            min_value=0.10,
            max_value=0.95,
            value=0.25,
            step=0.05
        )

    if uploaded_file is None:

        st.markdown(
            """
            <div class="empty-state">

                <div class="empty-icon">
                    🔎
                </div>

                <div class="empty-title">
                    Awaiting visual evidence
                </div>

                <div class="empty-text">
                    Upload a JPG, JPEG, PNG or WEBP image
                    to begin an investigation.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        try:

            image = Image.open(
                uploaded_file
            ).convert("RGB")

            st.markdown(
                '<div class="section-title">'
                'EVIDENCE SCAN'
                '</div>',
                unsafe_allow_html=True
            )

            with st.spinner(
                "Scanning visual evidence..."
            ):

                (
                    annotated_image,
                    detections
                ) = run_investigation(
                    image,
                    confidence
                )

            summary = create_local_analysis(
                detections
            )

            timestamp = datetime.now().strftime(
                "%H:%M:%S"
            )

            st.session_state.investigation_count += 1

            investigation_id = (
                f"INV-"
                f"{st.session_state.investigation_count:04d}"
            )

            history_item = {
                "id": investigation_id,
                "time": timestamp,
                "filename": uploaded_file.name,
                "detections": len(detections),
                "summary": summary,
            }

            st.session_state.history.append(
                history_item
            )

            img_col, result_col = st.columns(
                2
            )

            with img_col:

                st.markdown(
                    """
                    <div class="panel">
                        <div class="panel-title">
                            SOURCE EVIDENCE
                        </div>
                    """,
                    unsafe_allow_html=True
                )

                st.image(
                    image,
                    use_container_width=True
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

            with result_col:

                st.markdown(
                    """
                    <div class="panel">
                        <div class="panel-title">
                            ANALYZED EVIDENCE
                        </div>
                    """,
                    unsafe_allow_html=True
                )

                st.image(
                    annotated_image,
                    use_container_width=True
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

            st.markdown(
                '<div class="section-title">'
                'EVIDENCE DETECTED'
                '</div>',
                unsafe_allow_html=True
            )

            if detections:

                evidence_cols = st.columns(
                    min(3, len(detections))
                )

                for index, detection in enumerate(
                    detections
                ):

                    with evidence_cols[
                        index % len(evidence_cols)
                    ]:

                        confidence_percent = (
                            detection["confidence"]
                            * 100
                        )

                        st.markdown(
                            f"""
                            <div class="evidence-card">

                                <div class="evidence-label">
                                    EVIDENCE #{index + 1:03d}
                                </div>

                                <div class="evidence-name">
                                    {detection["object"].upper()}
                                </div>

                                <div class="evidence-confidence">
                                    Confidence:
                                    {confidence_percent:.1f}%
                                </div>

                                <div style="
                                    color:#71899f;
                                    font-size:12px;
                                    margin-top:8px;
                                ">
                                    Position:
                                    {detection["position"]}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            else:

                st.info(
                    "No objects were detected. "
                    "Try lowering the confidence threshold."
                )

            st.markdown(
                '<div class="section-title">'
                'DETECTION TABLE'
                '</div>',
                unsafe_allow_html=True
            )

            if detections:

                table_data = []

                for detection in detections:

                    table_data.append(
                        {
                            "Object":
                            detection["object"],

                            "Confidence":
                            f"{detection['confidence'] * 100:.1f}%",

                            "Position":
                            detection["position"],
                        }
                    )

                df = pd.DataFrame(
                    table_data
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No detection records available."
                )

            st.markdown(
                '<div class="section-title">'
                'INVESTIGATION ANALYSIS'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div class="analysis-card">

                    <div class="analysis-title">
                        LOCAL AI ANALYSIS
                    </div>

                    <div class="analysis-text">
                        {summary}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        except Exception as error:

            st.error(
                "The image could not be analyzed."
            )

            st.caption(
                f"Technical detail: {error}"
            )


# =========================================================
# AI ANALYSIS
# =========================================================

elif page == "🧠 AI Analysis":

    st.markdown(
        '<div class="section-title">'
        'AI VISUAL ANALYSIS'
        '</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.history:

        st.markdown(
            """
            <div class="empty-state">

                <div class="empty-icon">
                    🧠
                </div>

                <div class="empty-title">
                    No analysis available
                </div>

                <div class="empty-text">
                    Run an investigation first.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        options = [
            item["id"]
            for item in st.session_state.history
        ]

        selected_id = st.selectbox(
            "SELECT INVESTIGATION",
            options
        )

        selected = next(
            item
            for item in st.session_state.history
            if item["id"] == selected_id
        )

        st.markdown(
            f"""
            <div class="analysis-card">

                <div class="analysis-title">
                    INVESTIGATION {selected["id"]}
                </div>

                <div style="
                    color:#6e879d;
                    font-size:12px;
                    margin-top:8px;
                ">
                    {selected["filename"]}
                    &nbsp; • &nbsp;
                    {selected["time"]}
                </div>

                <div class="analysis-text">
                    {selected["summary"]}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            'ANALYSIS NOTES'
            '</div>',
            unsafe_allow_html=True
        )

        st.info(
            "This analysis is generated from YOLO's "
            "actual detections. It does not invent "
            "objects or claim information that the "
            "vision model cannot verify."
        )


# =========================================================
# HISTORY
# =========================================================

elif page == "🕘 History":

    st.markdown(
        '<div class="section-title">'
        'INVESTIGATION HISTORY'
        '</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.history:

        st.markdown(
            """
            <div class="empty-state">

                <div class="empty-icon">
                    🕘
                </div>

                <div class="empty-title">
                    Investigation history is empty
                </div>

                <div class="empty-text">
                    Your investigations will appear here
                    during this session.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        history_rows = []

        for item in reversed(
            st.session_state.history
        ):

            history_rows.append(
                {
                    "Investigation":
                    item["id"],

                    "Time":
                    item["time"],

                    "File":
                    item["filename"],

                    "Detections":
                    item["detections"],
                }
            )

        st.dataframe(
            pd.DataFrame(
                history_rows
            ),
            use_container_width=True,
            hide_index=True
        )

        st.markdown(
            '<div class="section-title">'
            'INVESTIGATION REPORTS'
            '</div>',
            unsafe_allow_html=True
        )

        for item in reversed(
            st.session_state.history
        ):

            st.markdown(
                f"""
                <div class="panel"
                     style="margin-bottom:12px;">

                    <div class="panel-title">
                        {item["id"]} • {item["time"]}
                    </div>

                    <b>
                        {item["filename"]}
                    </b>

                    <br><br>

                    <span style="
                        color:#71899f;
                    ">
                        {item["detections"]}
                        detection(s)
                    </span>

                    <br><br>

                    {item["summary"]}

                </div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#526a80;
        font-size:11px;
        margin-top:40px;
        padding-top:20px;
    ">
        ◈ AI DETECTIVE
        &nbsp;•&nbsp;
        VISUAL INTELLIGENCE CORE
        &nbsp;•&nbsp;
        YOLO VISION ENGINE
    </div>
    """,
    unsafe_allow_html=True
)
