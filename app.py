import streamlit as st
from ultralytics import YOLO
from PIL import Image, ImageDraw
import numpy as np
import pandas as pd
import json
import os
import hashlib
import urllib.parse
import urllib.request
from pathlib import Path

# =========================================================
# OPTIONAL FACE RECOGNITION
# =========================================================
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Visual Intelligence Agent",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# DATA
# =========================================================
DATA_DIR = Path("celebrity_data")
DATA_DIR.mkdir(exist_ok=True)

REGISTRY_FILE = DATA_DIR / "registry.json"


# =========================================================
# FUTURISTIC UI
# =========================================================
st.markdown("""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap'
);

.stApp {
    background:
        radial-gradient(
            circle at 12% 8%,
            rgba(0,229,255,.10),
            transparent 28%
        ),
        radial-gradient(
            circle at 88% 15%,
            rgba(124,58,237,.13),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #050914 0%,
            #080d1a 48%,
            #04070e 100%
        );

    color:#e8f1ff;
    font-family:'Inter',sans-serif;
}

.stApp:before {

    content:"";

    position:fixed;

    inset:0;

    pointer-events:none;

    opacity:.18;

    background-image:
        linear-gradient(
            rgba(255,255,255,.025) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(255,255,255,.025) 1px,
            transparent 1px
        );

    background-size:42px 42px;
}

.block-container {
    max-width:1450px;
    padding-top:2rem;
    padding-bottom:3rem;
}


[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #070c17 0%,
            #050811 100%
        );

    border-right:
        1px solid
        rgba(90,220,255,.12);
}


.hero {

    padding:30px;

    border:
        1px solid
        rgba(75,211,255,.20);

    border-radius:24px;

    background:
        linear-gradient(
            135deg,
            rgba(8,22,38,.94),
            rgba(10,13,28,.88)
        );

    box-shadow:
        0 0 45px
        rgba(0,212,255,.07),

        inset 0 1px 0
        rgba(255,255,255,.04);

    margin-bottom:24px;
}


.eyebrow {

    color:#54ddff;

    font-family:'Space Grotesk';

    font-size:12px;

    font-weight:700;

    letter-spacing:2.5px;

    text-transform:uppercase;
}


.hero h1 {

    font-family:'Space Grotesk';

    font-size:
        clamp(
            32px,
            5vw,
            58px
        );

    line-height:1.02;

    margin:8px 0;

    color:#f3f8ff;
}


.hero p {

    color:#8fa8bf;

    max-width:850px;

    font-size:15px;
}


.section-title {

    font-family:'Space Grotesk';

    font-size:20px;

    font-weight:700;

    color:#eef7ff;

    margin:
        28px 0 12px;
}


.module-card {

    min-height:180px;

    padding:22px;

    border:
        1px solid
        rgba(126,170,205,.15);

    border-radius:20px;

    background:
        rgba(8,16,29,.78);

    transition:
        .2s ease;
}


.module-card:hover {

    border-color:
        rgba(72,211,255,.40);

    transform:
        translateY(-2px);

    box-shadow:
        0 10px 35px
        rgba(0,210,255,.06);
}


.module-icon {

    font-size:30px;

    color:#53dcff;
}


.module-card h3 {

    font-family:'Space Grotesk';

    font-size:20px;

    margin:
        10px 0 7px;
}


.module-card p {

    color:#7f96aa;

    font-size:13px;

    line-height:1.6;
}


.metric {

    padding:18px;

    border:
        1px solid
        rgba(126,170,205,.14);

    border-radius:17px;

    background:
        rgba(10,18,32,.76);

    min-height:105px;
}


.metric-label {

    color:#7890a7;

    font-size:10px;

    font-weight:700;

    letter-spacing:1.4px;
}


.metric-value {

    color:#f3f8ff;

    font-family:'Space Grotesk';

    font-size:28px;

    font-weight:700;

    margin-top:8px;
}


.panel {

    padding:18px;

    border:
        1px solid
        rgba(126,170,205,.14);

    border-radius:18px;

    background:
        rgba(7,13,25,.72);
}


.match-card {

    padding:22px;

    border-radius:20px;

    border:
        1px solid
        rgba(66,245,163,.22);

    background:
        linear-gradient(
            135deg,
            rgba(16,48,42,.40),
            rgba(8,19,30,.75)
        );

    box-shadow:
        0 0 30px
        rgba(66,245,163,.05);
}


.match-status {

    color:#65f3aa;

    font-size:11px;

    font-weight:700;

    letter-spacing:1.5px;
}


.match-name {

    font-family:'Space Grotesk';

    font-size:32px;

    font-weight:700;

    margin-top:5px;
}


.info-card {

    padding:18px;

    border-radius:16px;

    border:
        1px solid
        rgba(126,170,205,.13);

    background:
        rgba(8,16,29,.70);

    margin-bottom:12px;
}


.stButton > button {

    border-radius:12px;

    border:
        1px solid
        rgba(72,211,255,.25);

    background:
        rgba(16,34,52,.85);

    color:#dff8ff;

    font-weight:700;
}


[data-testid="stFileUploader"] {

    border:
        1px dashed
        rgba(73,214,255,.35);

    border-radius:18px;

    background:
        rgba(5,17,29,.55);

    padding:8px;
}


footer {
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================
def load_registry():

    if REGISTRY_FILE.exists():

        try:
            return json.loads(
                REGISTRY_FILE.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:
            return {}

    return {}


def save_registry(data):

    REGISTRY_FILE.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def safe_name(name):

    cleaned = "".join(
        c
        for c in name.strip()
        if c.isalnum() or c in " _-"
    )

    return (
        cleaned.replace(" ", "_")
        or "Unknown"
    )


def image_hash(image):

    return hashlib.sha256(
        np.asarray(image).tobytes()
    ).hexdigest()[:16]


@st.cache_resource
def load_yolo():

    return YOLO("yolov8n.pt")


def build_gallery_encodings(registry):

    if not FACE_RECOGNITION_AVAILABLE:

        return [], []

    encodings = []
    names = []

    for person_name, paths in registry.items():

        for path in paths:

            if not os.path.exists(path):
                continue

            try:

                img = face_recognition.load_image_file(
                    path
                )

                locations = face_recognition.face_locations(
                    img,
                    model="hog"
                )

                faces = face_recognition.face_encodings(
                    img,
                    locations
                )

                if faces:

                    encodings.append(faces[0])
                    names.append(person_name)

            except Exception:
                continue

    return encodings, names


def wikipedia_lookup(name):

    try:

        title = urllib.parse.quote(
            name.replace(" ", "_")
        )

        url = (
            "https://en.wikipedia.org/"
            "api/rest_v1/page/summary/"
            + title
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                "VisualIntelligenceAgent/1.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=5
        ) as response:

            return json.loads(
                response.read().decode()
            )

    except Exception:

        return None


def draw_face_boxes(
    image,
    locations,
    labels
):

    output = image.copy()

    draw = ImageDraw.Draw(
        output
    )

    for i, (
        top,
        right,
        bottom,
        left
    ) in enumerate(locations):

        draw.rectangle(
            (
                left,
                top,
                right,
                bottom
            ),
            outline=(55,225,255),
            width=4
        )

        if i < len(labels):

            draw.text(
                (
                    left + 5,
                    max(0, top - 20)
                ),
                labels[i],
                fill=(235,250,255)
            )

    return output


# =========================================================
# LOAD DATA
# =========================================================
registry = load_registry()


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.markdown(
        "## ◈ VISUAL AI"
    )

    st.caption(
        "Visual Intelligence Agent"
    )

    st.divider()

    page = st.radio(
        "MODULES",
        [
            "🏠 Dashboard",
            "👤 People",
            "👁 Objects",
            "🌍 Scene",
            "📚 Knowledge",
            "🕘 History",
        ]
    )

    st.divider()

    st.markdown(
        "### SYSTEM"
    )

    st.success(
        "Vision pipeline online"
    )

    st.caption(
        f"Known people: {len(registry)}"
    )

    st.caption(
        "YOLOv8n"
    )

    if not FACE_RECOGNITION_AVAILABLE:

        st.warning(
            "Face engine unavailable"
        )


# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class="hero">

<div class="eyebrow">
AI / COMPUTER VISION / VISUAL INTELLIGENCE
</div>

<h1>
Visual Intelligence Agent
</h1>

<p>
One interface for people, objects, scenes and image knowledge.
Build your own reference gallery, inspect images with YOLO,
and retrieve knowledge about identified subjects.
</p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# DASHBOARD
# =========================================================
if page == "🏠 Dashboard":

    st.markdown(
        '<div class="section-title">'
        'SELECT INTELLIGENCE MODULE'
        '</div>',
        unsafe_allow_html=True
    )

    modules = [

        (
            "👤",
            "PEOPLE",
            "Identify people using your own reference gallery. "
            "Useful for celebrities, scientists and historical figures."
        ),

        (
            "👁",
            "OBJECTS",
            "Detect and count objects using YOLO."
        ),

        (
            "🌍",
            "SCENE",
            "Analyze the visual contents of an image."
        ),

        (
            "📚",
            "KNOWLEDGE",
            "Look up information about a person or subject."
        ),

        (
            "🕘",
            "HISTORY",
            "Review your previous scan interface."
        ),
    ]

    cols = st.columns(3)

    for i, (
        icon,
        title,
        description
    ) in enumerate(modules):

        with cols[i % 3]:

            st.markdown(
                f"""
                <div class="module-card">

                    <div class="module-icon">
                        {icon}
                    </div>

                    <h3>
                        {title}
                    </h3>

                    <p>
                        {description}
                    </p>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        '<div class="section-title">'
        'SYSTEM TELEMETRY'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        (
            "REFERENCE PEOPLE",
            len(registry)
        ),
        (
            "REFERENCE PHOTOS",
            sum(
                len(x)
                for x in registry.values()
            )
        ),
        (
            "VISION MODEL",
            "YOLOv8n"
        ),
        (
            "SYSTEM STATUS",
            "ONLINE"
        )
    ]

    for col, (
        label,
        value
    ) in zip(
        [c1,c2,c3,c4],
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


# =========================================================
# PEOPLE
# =========================================================
elif page == "👤 People":

    st.markdown(
        '<div class="section-title">'
        'PEOPLE / REFERENCE GALLERY'
        '</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns(
        [1, 1.5]
    )

    with left:

        person_name = st.text_input(
            "Person name",
            placeholder=
            "Albert Einstein / Shah Rukh Khan"
        )

    with right:

        reference_files = st.file_uploader(
            "Reference photos — 1 to 3 clear photos",
            type=[
                "jpg",
                "jpeg",
                "png"
            ],
            accept_multiple_files=True,
            key="reference"
        )

    if st.button(
        "＋ CREATE / UPDATE PROFILE",
        use_container_width=True
    ):

        if not FACE_RECOGNITION_AVAILABLE:

            st.error(
                "face_recognition is not installed."
            )

        elif not person_name.strip():

            st.error(
                "Enter a person name."
            )

        elif not reference_files:

            st.error(
                "Upload at least one reference photo."
            )

        elif len(reference_files) > 3:

            st.error(
                "Maximum 3 photos per upload."
            )

        else:

            folder = (
                DATA_DIR /
                safe_name(person_name)
            )

            folder.mkdir(
                parents=True,
                exist_ok=True
            )

            saved = registry.get(
                person_name.strip(),
                []
            )

            for file in reference_files:

                image = Image.open(
                    file
                ).convert("RGB")

                path = (
                    folder /
                    f"{image_hash(image)}.jpg"
                )

                image.save(
                    path,
                    quality=95
                )

                if str(path) not in saved:

                    saved.append(
                        str(path)
                    )

            registry[
                person_name.strip()
            ] = saved

            save_registry(
                registry
            )

            st.success(
                f"{person_name} profile saved."
            )

            st.rerun()


    st.markdown(
        '<div class="section-title">'
        'IDENTIFY PERSON'
        '</div>',
        unsafe_allow_html=True
    )

    tolerance = st.slider(
        "Match tolerance",
        0.30,
        0.70,
        0.50,
        0.05
    )

    uploaded = st.file_uploader(
        "Upload image to identify",
        type=[
            "jpg",
            "jpeg",
            "png"
        ],
        key="person_image"
    )

    if (
        uploaded is not None
        and FACE_RECOGNITION_AVAILABLE
    ):

        image = Image.open(
            uploaded
        ).convert("RGB")

        array = np.array(
            image
        )

        with st.spinner(
            "Scanning faces..."
        ):

            locations = (
                face_recognition.face_locations(
                    array,
                    model="hog"
                )
            )

            encodings = (
                face_recognition.face_encodings(
                    array,
                    locations
                )
            )

            known_encodings, known_names = (
                build_gallery_encodings(
                    registry
                )
            )

            results = []
            labels = []

            for encoding in encodings:

                if not known_encodings:

                    results.append(
                        ("Unknown", 0)
                    )

                    labels.append(
                        "Unknown"
                    )

                    continue

                distances = (
                    face_recognition.face_distance(
                        known_encodings,
                        encoding
                    )
                )

                best_index = int(
                    np.argmin(
                        distances
                    )
                )

                distance = float(
                    distances[
                        best_index
                    ]
                )

                score = max(
                    0,
                    min(
                        1,
                        1 - distance
                    )
                )

                if distance <= tolerance:

                    name = (
                        known_names[
                            best_index
                        ]
                    )

                else:

                    name = "Unknown"

                results.append(
                    (
                        name,
                        score
                    )
                )

                labels.append(
                    f"{name} {score*100:.0f}%"
                )

            annotated = (
                draw_face_boxes(
                    image,
                    locations,
                    labels
                )
            )

        left, right = st.columns(2)

        with left:

            st.markdown(
                '<div class="panel">',
                unsafe_allow_html=True
            )

            st.markdown(
                "**SOURCE FRAME**"
            )

            st.image(
                image,
                use_container_width=True
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

        with right:

            st.markdown(
                '<div class="panel">',
                unsafe_allow_html=True
            )

            st.markdown(
                "**RECOGNITION FRAME**"
            )

            st.image(
                annotated,
                use_container_width=True
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

        for name, score in results:

            if name == "Unknown":

                st.info(
                    "Unknown — no sufficiently "
                    "close gallery match."
                )

                continue

            st.markdown(
                f"""
                <div class="match-card">

                    <div class="match-status">
                        CLOSED-SET MATCH
                    </div>

                    <div class="match-name">
                        {name}
                    </div>

                    <div style="
                        color:#65f3aa;
                        margin-top:5px;
                    ">
                        Visual similarity:
                        {score*100:.1f}%
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            information = (
                wikipedia_lookup(
                    name
                )
            )

            if information:

                st.markdown(
                    f"""
                    <div class="info-card">

                    <b>
                    {information.get("title", name)}
                    </b>

                    <br><br>

                    {information.get(
                        "description",
                        ""
                    )}

                    <br><br>

                    {information.get(
                        "extract",
                        ""
                    )}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


# =========================================================
# OBJECTS
# =========================================================
elif page == "👁 Objects":

    st.markdown(
        '<div class="section-title">'
        'OBJECT DETECTION'
        '</div>',
        unsafe_allow_html=True
    )

    confidence = st.slider(
        "YOLO confidence",
        0.10,
        0.95,
        0.25,
        0.05
    )

    uploaded = st.file_uploader(
        "Upload image",
        type=[
            "jpg",
            "jpeg",
            "png"
        ],
        key="objects"
    )

    if uploaded:

        image = Image.open(
            uploaded
        ).convert("RGB")

        model = load_yolo()

        with st.spinner(
            "Running YOLO inference..."
        ):

            result = model(
                np.array(image),
                conf=confidence,
                verbose=False
            )[0]

        output = Image.fromarray(
            result.plot()[..., ::-1]
        )

        left, right = st.columns(2)

        with left:

            st.image(
                image,
                caption="Source",
                use_container_width=True
            )

        with right:

            st.image(
                output,
                caption="Detection",
                use_container_width=True
            )

        rows = []

        for box in result.boxes:

            class_id = int(
                box.cls[0]
            )

            rows.append(
                {
                    "Object":
                    model.names[
                        class_id
                    ],

                    "Confidence":
                    f"{float(box.conf[0])*100:.1f}%"
                }
            )

        if rows:

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No objects detected."
            )


# =========================================================
# SCENE
# =========================================================
elif page == "🌍 Scene":

    st.markdown(
        '<div class="section-title">'
        'SCENE ANALYSIS'
        '</div>',
        unsafe_allow_html=True
    )

    uploaded = st.file_uploader(
        "Upload a scene",
        type=[
            "jpg",
            "jpeg",
            "png"
        ],
        key="scene"
    )

    if uploaded:

        image = Image.open(
            uploaded
        ).convert("RGB")

        model = load_yolo()

        with st.spinner(
            "Analyzing visual scene..."
        ):

            result = model(
                np.array(image),
                conf=0.25,
                verbose=False
            )[0]

        names = []

        for box in result.boxes:

            names.append(
                model.names[
                    int(box.cls[0])
                ]
            )

        counts = (
            pd.Series(names)
            .value_counts()
            .to_dict()
            if names
            else {}
        )

        st.image(
            image,
            caption="Scene Input",
            use_container_width=True
        )

        detected = (
            ", ".join(
                f"{count} × {name}"
                for name, count
                in counts.items()
            )
            if counts
            else
            "No supported objects detected."
        )

        st.markdown(
            f"""
            <div class="info-card">

            <b>
            VISUAL SCENE SUMMARY
            </b>

            <br><br>

            Detected elements:

            <br>

            {detected}

            <br><br>

            <span style="color:#7189a0;">
            The scene module reports only observations
            supported by the current vision model.
            </span>

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# KNOWLEDGE
# =========================================================
elif page == "📚 Knowledge":

    st.markdown(
        '<div class="section-title">'
        'KNOWLEDGE AGENT'
        '</div>',
        unsafe_allow_html=True
    )

    person = st.text_input(
        "Person / subject",
        placeholder="Albert Einstein"
    )

    question = st.text_area(
        "Ask a question",
        placeholder=
        "What is this person famous for?"
    )

    if st.button(
        "ASK KNOWLEDGE AGENT",
        use_container_width=True
    ):

        if not person.strip():

            st.error(
                "Enter a person or subject."
            )

        else:

            information = (
                wikipedia_lookup(
                    person
                )
            )

            if information:

                st.markdown(
                    f"""
                    <div class="match-card">

                    <div class="match-status">
                        KNOWLEDGE LOOKUP
                    </div>

                    <div class="match-name">
                        {information.get(
                            "title",
                            person
                        )}
                    </div>

                    <br>

                    <b>
                    {information.get(
                        "description",
                        ""
                    )}
                    </b>

                    <br><br>

                    {information.get(
                        "extract",
                        ""
                    )}

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.warning(
                    "No Wikipedia information found."
                )


# =========================================================
# HISTORY
# =========================================================
elif page == "🕘 History":

    st.markdown(
        '<div class="section-title">'
        'SCAN HISTORY'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "History module is ready for scan persistence. "
        "The next upgrade can store date, image, module, "
        "detected person and confidence."
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
        margin-top:35px;
    ">
        VISION CORE • PEOPLE • OBJECTS • SCENE • KNOWLEDGE
    </div>
    """,
    unsafe_allow_html=True
)
