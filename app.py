"""
YOLO Vision — AI Object Detection Agent
=========================================
A simple, good-looking Streamlit app that runs YOLOv8 object detection
on user-uploaded images.

- Upload an image
- Adjust confidence threshold
- See detected objects with bounding boxes
- See a breakdown of detected classes
- Download the annotated result

Model: Ultralytics YOLOv8n (nano) — small, fast, downloads automatically
on first run (requires internet, available on Streamlit Cloud).
"""

import hashlib
import io
import time

import numpy as np
import streamlit as st
from PIL import Image

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="YOLO Vision — AI Object Detection",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# THEME
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Poppins:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(124,58,237,0.20) 0%, transparent 45%),
        radial-gradient(circle at 88% 15%, rgba(34,211,238,0.14) 0%, transparent 40%),
        linear-gradient(180deg, #06040f 0%, #0d0a1f 100%);
    color: #ece9ff;
}
#MainMenu, footer, header {visibility: hidden;}
.block-container { padding-top: 2rem; max-width: 1200px; }

.yolo-title {
    font-family: 'Orbitron', sans-serif;
    font-weight: 800;
    letter-spacing: 0.08em;
    background: linear-gradient(90deg, #a78bfa, #22d3ee, #a78bfa);
    background-size: 200% auto;
    -webkit-background-clip: text; background-clip: text; color: transparent;
    animation: shine 6s linear infinite;
    font-size: 2.4rem;
}
@keyframes shine { to { background-position: 200% center; } }
.yolo-subtitle { color: #a09bc4; font-weight: 300; margin-top: -0.4rem; }

.glass {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(167,139,250,0.25);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    backdrop-filter: blur(16px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.35);
    margin-bottom: 1rem;
}

.pill {
    display:inline-block; padding: 0.22rem 0.75rem; border-radius: 999px;
    font-size: 0.78rem; font-weight: 600; margin: 0.15rem 0.3rem 0.15rem 0;
    background: rgba(124,58,237,0.16); border: 1px solid rgba(167,139,250,0.4); color:#d8ccff;
}
.pill-cyan { background: rgba(34,211,238,0.14); border-color: rgba(34,211,238,0.4); color:#a8f0ff; }

.kpi { text-align:center; }
.kpi-value { font-family:'Orbitron', sans-serif; font-size:1.7rem; font-weight:700; }
.kpi-label { font-size:0.72rem; color:#a09bc4; letter-spacing:0.05em; text-transform:uppercase; }

div.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white; border: none; border-radius: 12px;
    padding: 0.55rem 1.3rem; font-weight: 600;
    box-shadow: 0 4px 20px rgba(124,58,237,0.4);
}
div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 26px rgba(124,58,237,0.6); color:white;}

section[data-testid="stSidebar"] { background: rgba(10,8,24,0.6); border-right: 1px solid rgba(167,139,250,0.15); }

.orb {
    width: 64px; height: 64px; border-radius: 50%; margin: 0 auto;
    background: radial-gradient(circle at 35% 30%, #c4b5fd, #7c3aed 45%, #312e81 100%);
    box-shadow: 0 0 40px 8px rgba(124,58,237,0.5);
    animation: pulse 2.4s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{transform:scale(1);} 50%{transform:scale(1.1);} }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# MODEL LOADING (cached — loaded once per session)
# ----------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def load_model(model_name: str):
    from ultralytics import YOLO
    return YOLO(model_name)  # auto-downloads on first run


MAX_DIM = 1280  # longer side is capped to this before inference — big speed win on large photos


def _resize_for_inference(image: Image.Image) -> Image.Image:
    """Downscale large images before running the model. Detection quality is
    essentially unchanged (YOLO already resizes internally to its input size),
    but a smaller array means faster preprocessing and less memory."""
    w, h = image.size
    longest = max(w, h)
    if longest <= MAX_DIM:
        return image
    scale = MAX_DIM / longest
    return image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)


@st.cache_data(show_spinner=False, max_entries=20)
def run_detection(image_bytes: bytes, confidence: float, iou: float, model_name: str):
    """
    Runs YOLO once for a given (image, confidence, iou, model) combination
    and caches the result. Re-running the app (e.g. moving an unrelated
    widget) or re-picking the same settings reuses the cached result
    instead of paying for inference again.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inference_image = _resize_for_inference(image)

    model = load_model(model_name)
    t0 = time.time()
    results = model.predict(np.array(inference_image), conf=confidence, iou=iou, verbose=False)
    elapsed = time.time() - t0

    result = results[0]
    annotated = result.plot()  # numpy array (BGR)
    annotated_img = Image.fromarray(annotated[..., ::-1])  # BGR -> RGB

    names = result.names
    counts = {}
    n_boxes = 0
    if result.boxes is not None:
        n_boxes = len(result.boxes)
        for cls_id in result.boxes.cls.tolist():
            cls_name = names[int(cls_id)]
            counts[cls_name] = counts.get(cls_name, 0) + 1

    buf = io.BytesIO()
    annotated_img.save(buf, format="PNG")

    return {
        "annotated_png": buf.getvalue(),
        "counts": counts,
        "n_boxes": n_boxes,
        "elapsed": elapsed,
        "was_resized": inference_image.size != image.size,
    }


# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.markdown('<div class="orb"></div>', unsafe_allow_html=True)
st.markdown('<h1 class="yolo-title" style="text-align:center;">YOLO VISION</h1>', unsafe_allow_html=True)
st.markdown('<p class="yolo-subtitle" style="text-align:center;">AI-powered object detection agent — '
            'upload an image and let the model find what\'s in it.</p>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# SIDEBAR — CONTROLS
# ----------------------------------------------------------------------------
MODEL_OPTIONS = {
    "YOLOv8s — Accurate (recommended)": "yolov8s.pt",
    "YOLOv8n — Fastest": "yolov8n.pt",
    "YOLOv8m — Most Accurate (slower)": "yolov8m.pt",
}

with st.sidebar:
    st.markdown("### ⚙️ Detection Settings")
    model_label = st.selectbox("Model", list(MODEL_OPTIONS.keys()), index=0,
                                help="Larger models are more accurate but slower. "
                                     "'s' is a good balance for demos/presentations.")
    model_name = MODEL_OPTIONS[model_label]
    confidence = st.slider("Confidence threshold", 0.10, 0.95, 0.55, 0.05,
                            help="Higher = fewer but more confident detections. "
                                 "Raise this if you're seeing wrong/false labels.")
    iou = st.slider("IoU threshold (NMS)", 0.10, 0.95, 0.45, 0.05)
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.caption(
        f"Model: **{model_label.split(' — ')[0]}** (Ultralytics), trained on the COCO dataset "
        "(80 everyday object classes: people, vehicles, animals, furniture, etc.)."
    )
    st.caption("Runs fully in this app — no external API key needed.")
    st.caption("⚠️ Pretrained models occasionally misclassify visually similar objects "
               "(e.g. bus ↔ truck). Raising the confidence threshold or using a larger "
               "model reduces this.")

# ----------------------------------------------------------------------------
# MAIN — UPLOAD + DETECTION
# ----------------------------------------------------------------------------
st.markdown('<div class="glass">', unsafe_allow_html=True)
uploaded = st.file_uploader("📤 Upload an image", type=["jpg", "jpeg", "png", "webp", "bmp"])
st.markdown('</div>', unsafe_allow_html=True)

if uploaded is not None:
    image_bytes = uploaded.getvalue()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("##### 🖼️ Original Image")
        st.image(image, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with st.spinner(f"🧠 Running {model_label.split(' — ')[0]} detection..."):
        detection = run_detection(image_bytes, confidence, iou, model_name)

    annotated_img = Image.open(io.BytesIO(detection["annotated_png"]))
    counts = detection["counts"]
    n_boxes = detection["n_boxes"]
    elapsed = detection["elapsed"]

    with col2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("##### 🎯 Detected Objects")
        st.image(annotated_img, use_container_width=True)
        if detection["was_resized"]:
            st.caption(f"Resized to max {MAX_DIM}px for faster inference — detection quality unaffected.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- Stats ----------------
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="kpi"><div class="kpi-value">{n_boxes}</div>'
                     f'<div class="kpi-label">Objects Found</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi"><div class="kpi-value">{len(counts)}</div>'
                     f'<div class="kpi-label">Unique Classes</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi"><div class="kpi-value">{elapsed:.2f}s</div>'
                     f'<div class="kpi-label">Inference Time</div></div>', unsafe_allow_html=True)

    if counts:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("**Detected classes:**")
        pills = "".join(
            f'<span class="pill pill-cyan">{name} × {n}</span>' for name, n in sorted(counts.items())
        )
        st.markdown(pills, unsafe_allow_html=True)
    else:
        st.info("No objects detected above the current confidence threshold — try lowering it in the sidebar.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- Download ----------------
    buf = io.BytesIO()
    annotated_img.save(buf, format="PNG")
    st.download_button(
        "⬇ Download Annotated Image",
        data=buf.getvalue(),
        file_name="yolo_detection_result.png",
        mime="image/png",
        use_container_width=True,
    )

else:
    st.markdown('<div class="glass" style="text-align:center; padding:2.5rem;">', unsafe_allow_html=True)
    st.markdown("👆 Upload an image above to run detection.")
    st.caption("Supported formats: JPG, JPEG, PNG, WEBP, BMP")
    st.markdown('</div>', unsafe_allow_html=True)
