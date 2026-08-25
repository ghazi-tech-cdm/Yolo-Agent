import streamlit as st
from ultralytics import YOLO
from PIL import Image, ImageDraw
import numpy as np
import pandas as pd
import os
import json
import hashlib
import urllib.parse
import urllib.request
from pathlib import Path

# Optional face-recognition dependency.
# Install with: pip install face_recognition
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Celebrity Vision Agent",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path("celebrity_data")
DATA_DIR.mkdir(exist_ok=True)
REGISTRY_FILE = DATA_DIR / "registry.json"


# =========================================================
# FUTURISTIC UI
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(0,229,255,.10), transparent 27%),
        radial-gradient(circle at 88% 17%, rgba(124,58,237,.12), transparent 30%),
        linear-gradient(135deg,#050914 0%,#080d1a 48%,#04070e 100%);
    color:#e8f1ff;
    font-family:'Inter',sans-serif;
}

.stApp:before {
    content:"";
    position:fixed;
    inset:0;
    pointer-events:none;
    opacity:.20;
    background-image:
        linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),
        linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);
    background-size:42px 42px;
    mask-image:linear-gradient(to bottom,black,transparent 85%);
}

.block-container { max-width:1450px; padding-top:2rem; padding-bottom:3rem; }

[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#070c17 0%,#050811 100%);
    border-right:1px solid rgba(90,220,255,.12);
}

.hero {
    padding:28px 30px;
    border:1px solid rgba(75,211,255,.20);
    border-radius:24px;
    background:linear-gradient(135deg,rgba(8,22,38,.92),rgba(10,13,28,.86));
    box-shadow:0 0 45px rgba(0,212,255,.07),inset 0 1px 0 rgba(255,255,255,.04);
    margin-bottom:24px;
}

.eyebrow {
    color:#54ddff;
    font-family:'Space Grotesk',sans-serif;
    font-size:12px;
    font-weight:700;
    letter-spacing:2.5px;
    text-transform:uppercase;
    margin-bottom:8px;
}

.hero h1 {
    font-family:'Space Grotesk',sans-serif;
    font-size:clamp(30px,4vw,52px);
    line-height:1.02;
    margin:0;
    color:#f3f8ff;
}

.hero p { color:#8fa8bf; margin:13px 0 0; max-width:850px; font-size:15px; }

.status-pill {
    display:inline-flex;
    align-items:center;
    gap:8px;
    margin-top:20px;
    padding:7px 12px;
    border-radius:999px;
    border:1px solid rgba(66,245,163,.25);
    background:rgba(66,245,163,.07);
    color:#65f3aa;
    font-size:12px;
    font-weight:700;
}

.dot {
    width:7px;
    height:7px;
    border-radius:50%;
    background:#42f5a3;
    box-shadow:0 0 12px #42f5a3;
}

.section-title {
    font-family:'Space Grotesk',sans-serif;
    color:#eef7ff;
    font-size:19px;
    font-weight:700;
    margin:26px 0 12px;
}

.metric {
    min-height:118px;
    padding:20px;
    border-radius:18px;
    border:1px solid rgba(126,170,205,.15);
    background:rgba(10,18,32,.76);
}

.metric-label {
    color:#7890a7;
    font-size:11px;
    font-weight:700;
    letter-spacing:1.4px;
    text-transform:uppercase;
}

.metric-value {
    color:#f3f8ff;
    font-family:'Space Grotesk',sans-serif;
    font-size:28px;
    font-weight:700;
    margin-top:9px;
}

.metric-sub { color:#53dcff; font-size:11px; margin-top:5px; }

.panel {
    padding:18px;
    border-radius:18px;
    border:1px solid rgba(126,170,205,.14);
    background:rgba(7,13,25,.72);
}

.match-card {
    padding:22px;
    border-radius:20px;
    border:1px solid rgba(66,245,163,.20);
    background:linear-gradient(135deg,rgba(16,48,42,.40),rgba(8,19,30,.72));
    box-shadow:0 0 32px rgba(66,245,163,.06);
}

.match-name {
    font-family:'Space Grotesk',sans-serif;
    font-size:32px;
    font-weight:700;
    color:#f4fbff;
}

.match-score { color:#65f3aa; font-size:13px; font-weight:700; }

.info-card {
    padding:18px;
    border-radius:16px;
    border:1px solid rgba(126,170,205,.13);
    background:rgba(8,16,29,.70);
    margin-bottom:10px;
}

.stButton > button {
    border-radius:12px;
    border:1px solid rgba(72,211,255,.25);
    background:rgba(16,34,52,.8);
    color:#dff8ff;
    font-weight:700;
}

.stButton > button:hover {
    border-color:rgba(72,211,255,.65);
    color:white;
}

[data-testid="stFileUploader"] {
    border:1px dashed rgba(73,214,255,.35);
    border-radius:18px;
    background:rgba(5,17,29,.55);
    padding:8px;
}

footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================
def safe_name(name: str) -> str:
    cleaned = "".join(c for c in name.strip() if c.isalnum() or c in " _-")
    return cleaned.replace(" ", "_") or "Unknown"


def load_registry():
    if REGISTRY_FILE.exists():
        try:
            return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_registry(registry):
    REGISTRY_FILE.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def image_hash(image: Image.Image) -> str:
    return hashlib.sha256(np.asarray(image).tobytes()).hexdigest()[:16]


@st.cache_resource
def load_yolo():
    return YOLO("yolov8n.pt")


def build_gallery_encodings(registry):
    if not FACE_RECOGNITION_AVAILABLE:
        return [], []

    known_encodings = []
    known_names = []

    for celeb_name, paths in registry.items():
        for path in paths:
            if not os.path.exists(path):
                continue
            try:
                img = face_recognition.load_image_file(path)
                locations = face_recognition.face_locations(img, model="hog")
                encs = face_recognition.face_encodings(img, locations)
                if encs:
                    known_encodings.append(encs[0])
                    known_names.append(celeb_name)
            except Exception:
                continue

    return known_encodings, known_names


def wikipedia_summary(name):
    """Fetch a short Wikipedia summary without requiring an API key."""
    try:
        title = urllib.parse.quote(name.replace(" ", "_"))
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "CelebrityVisionAgent/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        return {
            "title": data.get("title", name),
            "description": data.get("description", ""),
            "extract": data.get("extract", ""),
            "url": data.get("content_urls", {})
                       .get("desktop", {})
                       .get("page", ""),
        }
    except Exception:
        return None


def draw_face_boxes(image, locations, labels=None):
    output = image.copy()
    draw = ImageDraw.Draw(output)

    for i, (top, right, bottom, left) in enumerate(locations):
        draw.rectangle((left, top, right, bottom), outline=(55, 225, 255), width=4)

        if labels and i < len(labels):
            label = labels[i]
            bbox = draw.textbbox((left, max(0, top - 24)), label)
            draw.rounded_rectangle(
                bbox,
                radius=5,
                fill=(5, 15, 25),
                outline=(55, 225, 255),
                width=1,
            )
            draw.text((left + 4, max(0, top - 22)), label, fill=(235, 250, 255))

    return output


# =========================================================
# SIDEBAR
# =========================================================
registry = load_registry()

with st.sidebar:
    st.markdown("## ◈ VISION CORE")
    st.caption("Celebrity + YOLO Recognition Agent")
    st.divider()

    mode = st.radio(
        "Agent mode",
        ["Celebrity Recognition", "YOLO Object Detection"],
        index=0,
    )

    st.markdown("### FACE MATCHING")
    face_tolerance = st.slider(
        "Match tolerance",
        min_value=0.30,
        max_value=0.70,
        value=0.50,
        step=0.05,
        help="Lower values are stricter. Start around 0.50 and tune with your reference photos.",
    )

    st.divider()
    st.markdown("### CELEBRITY GALLERY")

    if registry:
        for celeb, photos in registry.items():
            st.caption(f"● {celeb}  ·  {len(photos)} photo(s)")
    else:
        st.caption("No celebrity references added yet.")

    st.divider()
    if FACE_RECOGNITION_AVAILABLE:
        st.success("Face engine ready")
    else:
        st.warning("Install face_recognition to enable celebrity matching.")

    st.caption("YOLO model: YOLOv8n")


# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class="hero">
    <div class="eyebrow">AI / COMPUTER VISION / CELEBRITY INTELLIGENCE</div>
    <h1>Celebrity Vision Agent</h1>
    <p>
        Build a closed-set celebrity gallery from your own reference photos,
        then upload a new image to match faces against that gallery.
        YOLO remains available for general object detection.
    </p>
    <div class="status-pill"><span class="dot"></span> VISION PIPELINE READY</div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# GALLERY MANAGEMENT
# =========================================================
st.markdown('<div class="section-title">01 / CELEBRITY REFERENCE GALLERY</div>', unsafe_allow_html=True)

g1, g2 = st.columns([1, 1.5])

with g1:
    celeb_name = st.text_input(
        "Celebrity name",
        placeholder="e.g. Shah Rukh Khan",
    )

with g2:
    reference_files = st.file_uploader(
        "Add 1–3 clear reference photos",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="reference_upload",
    )

if st.button("＋ Add / Update Celebrity", use_container_width=True):
    if not celeb_name.strip():
        st.error("Enter a celebrity name first.")
    elif not reference_files:
        st.error("Upload at least one reference photo.")
    elif len(reference_files) > 3:
        st.error("Please add up to 3 reference photos per submission.")
    elif not FACE_RECOGNITION_AVAILABLE:
        st.error("Install `face_recognition` first, then restart Streamlit.")
    else:
        folder = DATA_DIR / safe_name(celeb_name)
        folder.mkdir(parents=True, exist_ok=True)

        saved = []
        for uploaded in reference_files:
            img = Image.open(uploaded).convert("RGB")
            temp_path = folder / f"{image_hash(img)}.jpg"
            img.save(temp_path, quality=95)
            saved.append(str(temp_path))

        current = registry.get(celeb_name.strip(), [])
        for path in saved:
            if path not in current:
                current.append(path)

        registry[celeb_name.strip()] = current
        save_registry(registry)
        st.success(f"{celeb_name.strip()} added to the reference gallery.")
        st.rerun()


if registry:
    gallery_cols = st.columns(min(4, max(1, len(registry))))
    for idx, (name, paths) in enumerate(registry.items()):
        with gallery_cols[idx % len(gallery_cols)]:
            st.markdown(
                f'<div class="info-card"><b>{name}</b><br>'
                f'<span style="color:#7189a0;font-size:12px;">'
                f'{len(paths)} reference photo(s)</span></div>',
                unsafe_allow_html=True,
            )


# =========================================================
# RECOGNITION MODE
# =========================================================
if mode == "Celebrity Recognition":
    st.markdown('<div class="section-title">02 / INPUT FRAME</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload a photo to identify faces",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key="recognition_upload",
    )

    if not FACE_RECOGNITION_AVAILABLE:
        st.info(
            "Celebrity recognition is disabled until the `face_recognition` package "
            "is installed. The gallery UI is ready."
        )

    if uploaded_file is not None and FACE_RECOGNITION_AVAILABLE:
        image = Image.open(uploaded_file).convert("RGB")
        rgb = np.array(image)

        with st.spinner("Scanning faces and matching against your closed-set gallery..."):
            locations = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, locations)
            known_encodings, known_names = build_gallery_encodings(registry)

            labels = []
            matches = []

            for encoding in encodings:
                if not known_encodings:
                    labels.append("Unknown")
                    matches.append(("Unknown", 0.0))
                    continue

                distances = face_recognition.face_distance(known_encodings, encoding)
                best_index = int(np.argmin(distances))
                best_distance = float(distances[best_index])

                if best_distance <= face_tolerance:
                    name = known_names[best_index]
                    # Approximate visual score; not a probability.
                    score = max(0.0, min(1.0, 1.0 - best_distance))
                    labels.append(f"{name}  {score*100:.0f}%")
                    matches.append((name, score))
                else:
                    labels.append("Unknown")
                    matches.append(("Unknown", 0.0))

            annotated = draw_face_boxes(image, locations, labels)

        m1, m2, m3, m4 = st.columns(4)

        recognized = [m for m in matches if m[0] != "Unknown"]

        with m1:
            st.markdown(
                f'<div class="metric"><div class="metric-label">Faces</div>'
                f'<div class="metric-value">{len(locations)}</div>'
                f'<div class="metric-sub">DETECTED FACES</div></div>',
                unsafe_allow_html=True,
            )

        with m2:
            st.markdown(
                f'<div class="metric"><div class="metric-label">Recognized</div>'
                f'<div class="metric-value">{len(recognized)}</div>'
                f'<div class="metric-sub">GALLERY MATCHES</div></div>',
                unsafe_allow_html=True,
            )

        with m3:
            unique_names = len(set(m[0] for m in recognized))
            st.markdown(
                f'<div class="metric"><div class="metric-label">Identities</div>'
                f'<div class="metric-value">{unique_names}</div>'
                f'<div class="metric-sub">UNIQUE CELEBRITIES</div></div>',
                unsafe_allow_html=True,
            )

        with m4:
            st.markdown(
                f'<div class="metric"><div class="metric-label">Gallery</div>'
                f'<div class="metric-value">{len(registry)}</div>'
                f'<div class="metric-sub">KNOWN IDENTITIES</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-title">03 / RECOGNITION OUTPUT</div>', unsafe_allow_html=True)

        left, right = st.columns(2)

        with left:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("**SOURCE FRAME**")
            st.image(image, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("**FACE MATCH FRAME**")
            st.image(annotated, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">04 / IDENTITY RESULTS</div>', unsafe_allow_html=True)

        if not matches:
            st.info("No face detected in the uploaded image.")
        else:
            for name, score in matches:
                if name == "Unknown":
                    st.markdown(
                        '<div class="info-card"><b>UNKNOWN</b><br>'
                        '<span style="color:#7189a0;">No sufficiently close match in your selected celebrity gallery.</span></div>',
                        unsafe_allow_html=True,
                    )
                    continue

                wiki = wikipedia_summary(name)

                st.markdown(
                    f'<div class="match-card">'
                    f'<div style="color:#65f3aa;font-size:11px;font-weight:700;letter-spacing:1.5px;">'
                    f'CLOSED-SET MATCH</div>'
                    f'<div class="match-name">{name}</div>'
                    f'<div class="match-score">REFERENCE DISTANCE MATCH • {score*100:.1f}% visual score</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                if wiki:
                    st.markdown(
                        f'<div class="info-card">'
                        f'<b>{wiki["title"]}</b><br>'
                        f'<span style="color:#8fa8bf;">{wiki["description"]}</span><br><br>'
                        f'<span style="color:#b4c6d8;">{wiki["extract"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if wiki["url"]:
                        st.markdown(f"[Open Wikipedia profile]({wiki['url']})")

        st.caption(
            "Important: the displayed match score is an approximate similarity score, "
            "not a calibrated probability. Test your gallery with representative images."
        )


# =========================================================
# YOLO MODE
# =========================================================
else:
    st.markdown('<div class="section-title">02 / OBJECT DETECTION INPUT</div>', unsafe_allow_html=True)

    yolo_conf = st.slider(
        "YOLO confidence threshold",
        0.10, 0.95, 0.25, 0.05,
        key="yolo_conf"
    )

    uploaded_file = st.file_uploader(
        "Upload an image for object detection",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key="yolo_upload",
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        model = load_yolo()

        with st.spinner("Running YOLO inference..."):
            result = model(np.array(image), conf=yolo_conf, verbose=False)[0]

        plotted = result.plot()
        result_image = Image.fromarray(plotted[..., ::-1])

        detections = []
        for box in result.boxes:
            class_id = int(box.cls[0])
            detections.append({
                "Object": model.names[class_id],
                "Confidence": float(box.conf[0]),
            })

        left, right = st.columns(2)
        with left:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("**SOURCE FRAME**")
            st.image(image, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("**YOLO DETECTION FRAME**")
            st.image(result_image, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">03 / OBJECT LOG</div>', unsafe_allow_html=True)

        if detections:
            df = pd.DataFrame(detections)
            df["Confidence"] = (df["Confidence"] * 100).round(1).astype(str) + "%"
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No objects crossed the selected confidence threshold.")


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    '<div style="text-align:center;color:#526a80;font-size:11px;margin-top:34px;">'
    'VISION CORE • CLOSED-SET CELEBRITY RECOGNITION • YOLO OBJECT DETECTION'
    '</div>',
    unsafe_allow_html=True,
)
