import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np

# Page ka title aur layout set karo
st.set_page_config(page_title="YOLO Object Detection Agent", page_icon="🔍")

st.title("🔍 YOLO Object Detection Agent")
st.write("Koi bhi image upload karein, agent usme objects detect karke dikhayega (cars, people, animals, etc.)")


# YOLO model load karo - @st.cache_resource se ye ek hi baar load hoga, baar baar nahi
@st.cache_resource
def load_model():
    return YOLO('yolov8n.pt')


model = load_model()

# File uploader
uploaded_file = st.file_uploader("Image Upload Karein", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Uploaded image ko PIL Image mein convert karo
    image = Image.open(uploaded_file).convert("RGB")

    # Original image dikhao
    st.subheader("Original Image")
    st.image(image, use_container_width=True)

    # YOLO detection chalao
    with st.spinner("Objects detect ho rahe hain..."):
        results = model(np.array(image))

    # Result image nikalo (boxes ke sath)
    result_array = results[0].plot()  # BGR format mein hota hai
    result_image = Image.fromarray(result_array[..., ::-1])  # BGR se RGB mein convert

    st.subheader("Detection Result")
    st.image(result_image, use_container_width=True)

    # Detected objects ki summary
    st.subheader("Detected Objects")
    if len(results[0].boxes) == 0:
        st.write("Koi object detect nahi hua.")
    else:
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            confidence = float(box.conf[0])
            st.write(f"**{class_name}** — {round(confidence * 100, 1)}% confidence")
