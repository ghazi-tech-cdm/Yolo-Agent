# 🎯 YOLO Vision — AI Object Detection Agent

A simple, good-looking Streamlit app that uses **YOLOv8** (Ultralytics) to
detect objects in any image you upload — with bounding boxes, class labels,
confidence scores, and a downloadable annotated result.

## Features
- Upload an image (JPG/PNG/WEBP/BMP)
- Adjustable **confidence** and **IoU (NMS)** thresholds
- Bounding-box visualization with class labels
- Detected-object stats: total objects, unique classes, inference time
- Download the annotated image
- Clean dark / purple glassmorphism UI

## Model
Uses **YOLOv8n** (nano), pretrained on the COCO dataset (80 common object
classes — people, vehicles, animals, furniture, everyday items, etc.).
The weights (`yolov8n.pt`, ~6MB) download automatically the first time the
app runs — no API key or manual setup needed.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Push this folder to a GitHub repository (root of the repo, or point
   Streamlit Cloud to this folder).
2. Go to [share.streamlit.io](https://share.streamlit.io), connect your
   GitHub repo, and set **Main file path** to `app.py`.
3. Deploy. Streamlit Cloud will install everything in `requirements.txt`
   and `packages.txt` automatically, and the model weights will download
   on first run.

## Project structure
```
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
├── packages.txt            # System libraries (for OpenCV on Streamlit Cloud)
├── .streamlit/config.toml  # Theme + server config
└── .gitignore
```

## Notes for your assignment
- The detection logic runs entirely through `ultralytics.YOLO(...).predict(...)`
  — a real, working model (not mocked), so results reflect actual model
  inference on your images.
- To swap in a custom-trained model, just replace `"yolov8n.pt"` in
  `load_model()` with the path to your own `best.pt` weights file.
- To detect only specific classes, pass `classes=[...]` (COCO class indices)
  to `model.predict(...)`.
