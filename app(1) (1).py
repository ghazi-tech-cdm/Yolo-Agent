import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
from collections import Counter

st.set_page_config(
    page_title="YOLO Vision Agent",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Tech-style UI
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

    .stApp {
        background:
            radial-gradient(circle at 15% 15%, rgba(0, 229, 255, .09), transparent 25%),
            radial-gradient(circle at 85% 20%, rgba(124, 58, 237, .10), transparent 25%),
            linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px),
            #070b12;
        background-size: auto, auto, 36px 36px, 36px 36px;
        color: #e8eef7;
    }

    .block-container { max-width: 1450px; padding-top: 2rem; }
    h1, h2, h3, p, label, div { font-family: Inter, sans-serif; }

    .hero {
        border: 1px solid rgba(0,229,255,.18);
        background: linear-gradient(135deg, rgba(10,18,31,.92), rgba(10,14,25,.72));
        border-radius: 22px;
        padding: 28px 32px;
        margin-bottom: 22px;
        box-shadow: 0 0 45px rgba(0,229,255,.06), inset 0 1px rgba(255,255,255,.04);
        position: relative;
        overflow: hidden;
    }
    .hero:after {
        content: '';
        position: absolute; right: -90px; top: -100px;
        width: 280px; height: 280px;
        border: 1px solid rgba(0,229,255,.15);
        border-radius: 50%;
        box-shadow: 0 0 0 30px rgba(0,229,255,.025), 0 0 0 60px rgba(0,229,255,.018);
    }
    .eyebrow { color: #00e5ff; font: 700 12px 'Space Mono', monospace; letter-spacing: 2px; }
    .hero h1 { font-size: 42px; margin: 8px 0 8px; letter-spacing: -1.5px; }
    .hero p { color: #93a4ba; margin: 0; max-width: 760px; font-size: 15px; }

    .panel {
        border: 1px solid rgba(148,163,184,.13);
        background: rgba(10,15,24,.76);
        border-radius: 18px;
        padding: 18px;
        height: 100%;
        box-shadow: inset 0 1px rgba(255,255,255,.025);
    }
    .panel-title { font-weight: 700; font-size: 15px; margin-bottom: 12px; }
    .mono { font-family: 'Space Mono', monospace; color: #7dd3fc; font-size: 12px; }

    .metric {
        background: rgba(15,23,36,.9);
        border: 1px solid rgba(148,163,184,.12);
        border-radius: 14px;
        padding: 15px;
        text-align: center;
    }
    .metric .value { font: 800 24px 'Space Mono', monospace; color: #eaf7ff; }
    .metric .label { color: #718198; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

    [data-testid="stFileUploaderDropzone"] {
        background: rgba(8,15,25,.72);
        border: 1px dashed rgba(0,229,255,.35);
        border-radius: 16px;
    }
    [data-testid="stSidebar"] { background: #080d15; border-right: 1px solid rgba(148,163,184,.12); }
    .stButton button { border-radius: 10px; }
    .status { display:inline-flex; align-items:center; gap:8px; color:#a7f3d0; font-size:12px; font-family:'Space Mono',monospace; }
    .dot { width:8px; height:8px; background:#22c55e; border-radius:50%; box-shadow:0 0 12px #22c55e; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Model
# -----------------------------
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

with st.spinner("Initializing vision model..."):
    model = load_model()

# -----------------------------
# Sidebar controls
# -----------------------------
with st.sidebar:
    st.markdown("## ◈ VISION CONTROL")
    st.caption("YOLO Object Detection Agent")
    st.divider()

    confidence = st.slider("Detection confidence", 0.10, 0.95, 0.35, 0.05)
    st.caption("Lower = more detections · Higher = stricter matching")

    st.divider()
    st.markdown("**MODEL STATUS**")
    st.markdown('<div class="status"><span class="dot"></span> ONLINE</div>', unsafe_allow_html=True)
    st.markdown("<div class='mono' style='margin-top:10px'>MODEL // YOLOv8n</div>", unsafe_allow_html=True)
    st.markdown("<div class='mono'>MODE // OBJECT DETECTION</div>", unsafe_allow_html=True)
    st.markdown("<div class='mono'>INPUT // JPG / JPEG / PNG</div>", unsafe_allow_html=True)

# -----------------------------
# Hero
# -----------------------------
st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">AI VISION SYSTEM / LIVE INFERENCE</div>
      <h1>YOLO Vision Agent</h1>
      <p>Upload an image and let the agent detect objects, estimate confidence, and visualize every prediction in a clean technical dashboard.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Upload
# -----------------------------
left, right = st.columns([2.4, 1], gap="large")
with left:
    st.markdown('<div class="panel"><div class="panel-title">◉ INPUT IMAGE</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drop an image here",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown(
        """
        <div class="panel">
          <div class="panel-title">SYSTEM INFO</div>
          <div class="mono">STATUS&nbsp;&nbsp;&nbsp;READY</div><br>
          <div class="mono">ENGINE&nbsp;&nbsp;&nbsp;ULTRALYTICS</div><br>
          <div class="mono">PIPELINE&nbsp;&nbsp;IMAGE → YOLO → UI</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if uploaded_file is None:
    st.markdown(
        "<div style='text-align:center;color:#5f7188;margin:60px 0;font-family:Space Mono'>WAITING FOR IMAGE INPUT...</div>",
        unsafe_allow_html=True,
    )
    st.stop()

# -----------------------------
# Inference
# -----------------------------
image = Image.open(uploaded_file).convert("RGB")

with st.spinner("Running neural inference..."):
    results = model(np.array(image), conf=confidence, verbose=False)

result = results[0]
result_array = result.plot()
result_image = Image.fromarray(result_array[..., ::-1])

boxes = result.boxes
count = len(boxes)
classes = [model.names[int(box.cls[0])] for box in boxes]
confidences = [float(box.conf[0]) for box in boxes]
counts = Counter(classes)
avg_conf = (sum(confidences) / count * 100) if count else 0

# -----------------------------
# Metrics
# -----------------------------
st.markdown("### INFERENCE OVERVIEW")
m1, m2, m3, m4 = st.columns(4)
for col, value, label in [
    (m1, count, "Objects detected"),
    (m2, len(counts), "Unique classes"),
    (m3, f"{avg_conf:.1f}%", "Avg confidence"),
    (m4, f"{image.width}×{image.height}", "Input resolution"),
]:
    with col:
        st.markdown(f'<div class="metric"><div class="value">{value}</div><div class="label">{label}</div></div>', unsafe_allow_html=True)

st.write("")

# -----------------------------
# Images
# -----------------------------
col1, col2 = st.columns(2, gap="large")
with col1:
    st.markdown('<div class="panel"><div class="panel-title">ORIGINAL FRAME</div>', unsafe_allow_html=True)
    st.image(image, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="panel"><div class="panel-title">DETECTION FRAME</div>', unsafe_allow_html=True)
    st.image(result_image, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Detection table / summary
# -----------------------------
st.markdown("### DETECTION LOG")
if count == 0:
    st.info("No objects detected at the current confidence threshold. Try lowering the confidence slider.")
else:
    summary_cols = st.columns(min(4, max(1, len(counts))))
    for i, (name, qty) in enumerate(counts.items()):
        with summary_cols[i % len(summary_cols)]:
            st.markdown(
                f'<div class="metric"><div class="value">{qty}</div><div class="label">{name}</div></div>',
                unsafe_allow_html=True,
            )

    rows = []
    for idx, box in enumerate(boxes, start=1):
        class_id = int(box.cls[0])
        rows.append({
            "#": idx,
            "Object": model.names[class_id],
            "Confidence": f"{float(box.conf[0]) * 100:.1f}%",
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

st.caption("YOLO Vision Agent · Object detection only · Closed-set celebrity recognition is a separate pipeline from this detector.")
