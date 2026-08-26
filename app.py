import streamlit as st
from ultralytics import YOLO
from PIL import Image, ImageDraw
import numpy as np
import pandas as pd
import cv2
import json
import os
import hashlib
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime

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
# CONFIG / CONSTANTS
# =========================================================
APP_PASSWORD = "project123"  # <-- yahan se password change kar sakte hain

DATA_DIR = Path("celebrity_data")
DATA_DIR.mkdir(exist_ok=True)
REGISTRY_FILE = DATA_DIR / "registry.json"
MODELS_DIR = Path("face_models")
MODELS_DIR.mkdir(exist_ok=True)

YUNET_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
SFACE_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"
YUNET_PATH = MODELS_DIR / "yunet.onnx"
SFACE_PATH = MODELS_DIR / "sface.onnx"


# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(0,229,255,.10), transparent 28%),
        radial-gradient(circle at 88% 15%, rgba(124,58,237,.13), transparent 30%),
        linear-gradient(135deg, #050914 0%, #080d1a 48%, #04070e 100%);
    color:#e8f1ff;
    font-family:'Inter',sans-serif;
}
.block-container { max-width:1450px; padding-top:2rem; padding-bottom:3rem; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070c17 0%, #050811 100%);
    border-right: 1px solid rgba(90,220,255,.12);
}
.hero {
    padding:30px;
    border:1px solid rgba(75,211,255,.20);
    border-radius:24px;
    background: linear-gradient(135deg, rgba(8,22,38,.94), rgba(10,13,28,.88));
    box-shadow: 0 0 45px rgba(0,212,255,.07), inset 0 1px 0 rgba(255,255,255,.04);
    margin-bottom:24px;
}
.eyebrow { color:#54ddff; font-family:'Space Grotesk'; font-size:12px; font-weight:700; letter-spacing:2.5px; text-transform:uppercase; }
.hero h1 { font-family:'Space Grotesk'; font-size:clamp(32px,5vw,52px); line-height:1.05; margin:8px 0; color:#f3f8ff; }
.hero p { color:#8fa8bf; max-width:850px; font-size:15px; }
.section-title { font-family:'Space Grotesk'; font-size:20px; font-weight:700; color:#eef7ff; margin:28px 0 12px; }
.metric-label { color:#7890a7; font-size:10px; font-weight:700; letter-spacing:1.4px; }
.metric-value { color:#f3f8ff; font-family:'Space Grotesk'; font-size:26px; font-weight:700; margin-top:6px; }
.match-card {
    padding:22px; border-radius:20px; border:1px solid rgba(66,245,163,.22);
    background: linear-gradient(135deg, rgba(16,48,42,.40), rgba(8,19,30,.75));
}
.match-status { color:#65f3aa; font-size:11px; font-weight:700; letter-spacing:1.5px; }
.match-name { font-family:'Space Grotesk'; font-size:30px; font-weight:700; margin-top:5px; }
.info-card { padding:18px; border-radius:16px; border:1px solid rgba(126,170,205,.13); background: rgba(8,16,29,.70); margin-top:12px; }
.stButton > button {
    border-radius:12px; border:1px solid rgba(72,211,255,.25);
    background: rgba(16,34,52,.85); color:#dff8ff; font-weight:700;
    width:100%;
}
[data-testid="stFileUploader"] {
    border:1px dashed rgba(73,214,255,.35); border-radius:18px;
    background: rgba(5,17,29,.55); padding:8px;
}
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)


# =========================================================
# PASSWORD GATE
# =========================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <div class="hero" style="max-width:480px; margin:80px auto;">
        <div class="eyebrow">RESTRICTED ACCESS</div>
        <h1 style="font-size:32px;">Visual Intelligence Agent</h1>
        <p>Enter the access password to continue.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        pwd = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Enter password")
        if st.button("ENTER"):
            if pwd == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    st.stop()


# =========================================================
# HELPERS
# =========================================================
def load_registry():
    if REGISTRY_FILE.exists():
        try:
            return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_registry(data):
    REGISTRY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def safe_name(name):
    cleaned = "".join(c for c in name.strip() if c.isalnum() or c in " _-")
    return cleaned.replace(" ", "_") or "Unknown"


def image_hash(image):
    return hashlib.sha256(np.asarray(image).tobytes()).hexdigest()[:16]


def download_if_missing(url, path):
    if not path.exists():
        with st.spinner(f"Downloading model: {path.name} ..."):
            urllib.request.urlretrieve(url, path)


@st.cache_resource
def load_yolo():
    return YOLO("yolov8n.pt")


@st.cache_resource
def load_face_detector():
    download_if_missing(YUNET_URL, YUNET_PATH)
    detector = cv2.FaceDetectorYN.create(str(YUNET_PATH), "", (320, 320), 0.7, 0.3, 5000)
    return detector


@st.cache_resource
def load_face_recognizer():
    download_if_missing(SFACE_URL, SFACE_PATH)
    return cv2.FaceRecognizerSF.create(str(SFACE_PATH), "")


def detect_faces(bgr_image):
    """Returns list of face rows (each: x,y,w,h,landmarks...,score) using YuNet."""
    detector = load_face_detector()
    h, w = bgr_image.shape[:2]
    detector.setInputSize((w, h))
    _, faces = detector.detect(bgr_image)
    if faces is None:
        return []
    return faces


def get_face_feature(bgr_image, face_row):
    recognizer = load_face_recognizer()
    aligned = recognizer.alignCrop(bgr_image, face_row)
    feature = recognizer.feature(aligned)
    return feature


def compare_features(feature1, feature2):
    recognizer = load_face_recognizer()
    return recognizer.match(feature1, feature2, cv2.FaceRecognizerSF_FR_COSINE)


def build_gallery_features(registry):
    """Compute face features for every saved reference photo. Returns (features, names)."""
    features, names = [], []
    for person_name, paths in registry.items():
        for path in paths:
            if not os.path.exists(path):
                continue
            bgr = cv2.imread(path)
            if bgr is None:
                continue
            faces = detect_faces(bgr)
            if len(faces) == 0:
                continue
            feature = get_face_feature(bgr, faces[0])
            features.append(feature)
            names.append(person_name)
    return features, names


def wikipedia_lookup(query):
    """Try direct summary lookup; fall back to search if the exact title fails."""
    def fetch_summary(title):
        try:
            encoded = urllib.parse.quote(title.replace(" ", "_"))
            url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + encoded
            req = urllib.request.Request(url, headers={"User-Agent": "VisualIntelligenceAgent/1.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode())
        except Exception:
            return None
        return None

    # 1. Direct attempt
    result = fetch_summary(query)
    if result and result.get("extract"):
        return result

    # 2. Search fallback
    try:
        search_url = (
            "https://en.wikipedia.org/w/api.php?action=opensearch&search="
            + urllib.parse.quote(query)
            + "&limit=1&namespace=0&format=json"
        )
        req = urllib.request.Request(search_url, headers={"User-Agent": "VisualIntelligenceAgent/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())
            titles = data[1] if len(data) > 1 else []
            if titles:
                return fetch_summary(titles[0])
    except Exception:
        return None

    return None


def draw_face_boxes(pil_image, faces, labels):
    output = pil_image.copy()
    draw = ImageDraw.Draw(output)
    for i, face in enumerate(faces):
        x, y, w, h = [int(v) for v in face[:4]]
        draw.rectangle((x, y, x + w, y + h), outline=(55, 225, 255), width=4)
        if i < len(labels):
            draw.text((x + 4, max(0, y - 20)), labels[i], fill=(235, 250, 255))
    return output


def log_history(module, summary):
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.insert(0, {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Module": module,
        "Result": summary
    })
    st.session_state.history = st.session_state.history[:30]


# =========================================================
# LOAD DATA / PAGE STATE
# =========================================================
registry = load_registry()

if "page" not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

PAGES = ["🏠 Dashboard", "👤 People", "👁 Objects", "🌍 Scene", "📚 Knowledge", "🕘 History"]


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## ◈ VISUAL AI")
    st.caption("Visual Intelligence Agent")
    st.divider()

    selected = st.radio("MODULES", PAGES, index=PAGES.index(st.session_state.page))
    if selected != st.session_state.page:
        st.session_state.page = selected
        st.rerun()

    st.divider()
    st.markdown("### SYSTEM")
    st.success("Vision pipeline online")
    st.caption(f"Known people: {len(registry)}")
    st.caption("YOLOv8n · YuNet · SFace")

    if st.button("🔒 Logout"):
        st.session_state.authenticated = False
        st.rerun()


# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class="hero">
<div class="eyebrow">AI / COMPUTER VISION / VISUAL INTELLIGENCE</div>
<h1>Visual Intelligence Agent</h1>
<p>One interface for people, objects, scenes and image knowledge —
built with YOLOv8 and OpenCV's YuNet + SFace face recognition.</p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# DASHBOARD (clickable cards)
# =========================================================
if st.session_state.page == "🏠 Dashboard":
    st.markdown('<div class="section-title">SELECT INTELLIGENCE MODULE</div>', unsafe_allow_html=True)

    modules = [
        ("👤", "PEOPLE", "Identify people using your own reference gallery.", "👤 People"),
        ("👁", "OBJECTS", "Detect and count objects using YOLO.", "👁 Objects"),
        ("🌍", "SCENE", "Analyze the visual contents of an image.", "🌍 Scene"),
        ("📚", "KNOWLEDGE", "Look up information about a person or subject.", "📚 Knowledge"),
        ("🕘", "HISTORY", "Review your previous scans this session.", "🕘 History"),
    ]

    cols = st.columns(3)
    for i, (icon, title, description, target_page) in enumerate(modules):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {icon} {title}")
                st.caption(description)
                if st.button("Open", key=f"open_{title}"):
                    st.session_state.page = target_page
                    st.rerun()

    st.markdown('<div class="section-title">SYSTEM TELEMETRY</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        ("REFERENCE PEOPLE", len(registry)),
        ("REFERENCE PHOTOS", sum(len(x) for x in registry.values())),
        ("VISION MODEL", "YOLOv8n"),
        ("SYSTEM STATUS", "ONLINE"),
    ]
    for col, (label, value) in zip([c1, c2, c3, c4], metrics):
        with col:
            st.markdown(f"""
            <div class="info-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# PEOPLE
# =========================================================
elif st.session_state.page == "👤 People":
    st.markdown('<div class="section-title">PEOPLE / REFERENCE GALLERY</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1.5])
    with left:
        person_name = st.text_input("Person name", placeholder="Albert Einstein / Shah Rukh Khan")
    with right:
        reference_files = st.file_uploader(
            "Reference photos — 1 to 3 clear photos",
            type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="reference"
        )

    if st.button("＋ CREATE / UPDATE PROFILE"):
        if not person_name.strip():
            st.error("Enter a person name.")
        elif not reference_files:
            st.error("Upload at least one reference photo.")
        elif len(reference_files) > 3:
            st.error("Maximum 3 photos per upload.")
        else:
            folder = DATA_DIR / safe_name(person_name)
            folder.mkdir(parents=True, exist_ok=True)
            saved = registry.get(person_name.strip(), [])
            for file in reference_files:
                image = Image.open(file).convert("RGB")
                path = folder / f"{image_hash(image)}.jpg"
                image.save(path, quality=95)
                if str(path) not in saved:
                    saved.append(str(path))
            registry[person_name.strip()] = saved
            save_registry(registry)
            st.success(f"{person_name} profile saved.")
            st.rerun()

    if registry:
        st.caption("Registered people: " + ", ".join(registry.keys()))

    st.markdown('<div class="section-title">IDENTIFY PERSON</div>', unsafe_allow_html=True)
    tolerance = st.slider("Match sensitivity (higher = stricter)", 0.20, 0.60, 0.363, 0.01)

    uploaded = st.file_uploader("Upload image to identify", type=["jpg", "jpeg", "png"], key="person_image")

    if uploaded is not None:
        image = Image.open(uploaded).convert("RGB")
        bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        with st.spinner("Scanning faces..."):
            faces = detect_faces(bgr)
            known_features, known_names = build_gallery_features(registry)

            labels = []
            summaries = []
            for face in faces:
                feature = get_face_feature(bgr, face)
                if not known_features:
                    labels.append("Unknown")
                    summaries.append(("Unknown", 0.0))
                    continue
                scores = [compare_features(feature, kf) for kf in known_features]
                best_idx = int(np.argmax(scores))
                best_score = float(scores[best_idx])
                if best_score >= tolerance:
                    name = known_names[best_idx]
                else:
                    name = "Unknown"
                labels.append(f"{name} {best_score*100:.0f}%")
                summaries.append((name, best_score))

            annotated = draw_face_boxes(image, faces, labels)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**SOURCE FRAME**")
            st.image(image, use_container_width=True)
        with col2:
            st.markdown("**RECOGNITION FRAME**")
            st.image(annotated, use_container_width=True)

        if len(faces) == 0:
            st.warning("No face detected in the image.")

        for name, score in summaries:
            if name == "Unknown":
                st.info("Unknown — no sufficiently close gallery match.")
                log_history("People", "Unknown face")
                continue

            st.markdown(f"""
            <div class="match-card">
                <div class="match-status">CLOSED-SET MATCH</div>
                <div class="match-name">{name}</div>
                <div style="color:#65f3aa; margin-top:5px;">Similarity score: {score*100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            log_history("People", f"Matched: {name} ({score*100:.1f}%)")

            info = wikipedia_lookup(name)
            if info:
                st.markdown(f"""
                <div class="info-card">
                <b>{info.get("title", name)}</b><br><br>
                {info.get("description", "")}<br><br>
                {info.get("extract", "")}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.caption("No Wikipedia information found for this name.")


# =========================================================
# OBJECTS
# =========================================================
elif st.session_state.page == "👁 Objects":
    st.markdown('<div class="section-title">OBJECT DETECTION</div>', unsafe_allow_html=True)
    confidence = st.slider("YOLO confidence", 0.10, 0.95, 0.25, 0.05)
    uploaded = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"], key="objects")

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        model = load_yolo()
        with st.spinner("Running YOLO inference..."):
            result = model(np.array(image), conf=confidence, verbose=False)[0]
        output = Image.fromarray(result.plot()[..., ::-1])

        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="Source", use_container_width=True)
        with col2:
            st.image(output, caption="Detection", use_container_width=True)

        rows = [{"Object": model.names[int(b.cls[0])], "Confidence": f"{float(b.conf[0])*100:.1f}%"} for b in result.boxes]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            log_history("Objects", f"{len(rows)} object(s) detected")
        else:
            st.info("No objects detected.")
            log_history("Objects", "No objects detected")


# =========================================================
# SCENE
# =========================================================
elif st.session_state.page == "🌍 Scene":
    st.markdown('<div class="section-title">SCENE ANALYSIS</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload a scene", type=["jpg", "jpeg", "png"], key="scene")

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        model = load_yolo()
        with st.spinner("Analyzing visual scene..."):
            result = model(np.array(image), conf=0.25, verbose=False)[0]

        names = [model.names[int(b.cls[0])] for b in result.boxes]
        counts = pd.Series(names).value_counts().to_dict() if names else {}

        st.image(image, caption="Scene Input", use_container_width=True)
        detected = ", ".join(f"{count} × {name}" for name, count in counts.items()) if counts else "No supported objects detected."

        st.markdown(f"""
        <div class="info-card">
        <b>VISUAL SCENE SUMMARY</b><br><br>
        Detected elements:<br>{detected}<br><br>
        <span style="color:#7189a0;">The scene module reports only observations supported by the current vision model.</span>
        </div>
        """, unsafe_allow_html=True)
        log_history("Scene", detected)


# =========================================================
# KNOWLEDGE
# =========================================================
elif st.session_state.page == "📚 Knowledge":
    st.markdown('<div class="section-title">KNOWLEDGE AGENT</div>', unsafe_allow_html=True)

    person = st.text_input("Person / subject", placeholder="Albert Einstein")
    question = st.text_input("Optional: add a keyword to refine the search", placeholder="e.g. physics, Nobel Prize")

    if st.button("ASK KNOWLEDGE AGENT"):
        if not person.strip():
            st.error("Enter a person or subject.")
        else:
            query = f"{person.strip()} {question.strip()}".strip()
            info = wikipedia_lookup(query if question.strip() else person.strip())

            if info:
                st.markdown(f"""
                <div class="match-card">
                    <div class="match-status">KNOWLEDGE LOOKUP</div>
                    <div class="match-name">{info.get("title", person)}</div>
                    <br><b>{info.get("description", "")}</b><br><br>
                    {info.get("extract", "")}
                </div>
                """, unsafe_allow_html=True)
                log_history("Knowledge", f"Looked up: {info.get('title', person)}")
            else:
                st.warning("No Wikipedia information found. Try a different spelling or a more common name.")
                log_history("Knowledge", f"No result for: {person}")


# =========================================================
# HISTORY
# =========================================================
elif st.session_state.page == "🕘 History":
    st.markdown('<div class="section-title">SCAN HISTORY (this session)</div>', unsafe_allow_html=True)

    history = st.session_state.get("history", [])
    if not history:
        st.info("No activity yet this session. Use People, Objects, Scene, or Knowledge to see history here.")
    else:
        st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()


# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div style="text-align:center; color:#526a80; font-size:11px; margin-top:35px;">
VISION CORE • PEOPLE • OBJECTS • SCENE • KNOWLEDGE
</div>
""", unsafe_allow_html=True)
