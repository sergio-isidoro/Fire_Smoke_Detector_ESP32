import cv2
import threading
from ultralytics import YOLO
import torch
import queue
import time

# ---- Models ----
MODEL_OBJECTS_PATH = "models/yolo11n.pt"       # general objects
MODEL_FIRE_SMOKE_PATH = "models/model.pt"      # fire/smoke

# ---- Device setup ----
device = "cuda" if torch.cuda.is_available() else "cpu"

# ---- Load Models ----
model_objects = YOLO(MODEL_OBJECTS_PATH).to(device)
model_fire_smoke = YOLO(MODEL_FIRE_SMOKE_PATH).to(device)

# Only use FP16 if GPU is available
if device == "cuda":
    model_objects.half()
    model_fire_smoke.half()

# Face classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Webcam
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   # lower resolution for speed
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 192)

# ---- Shared frame queue ----
frame_queue = queue.Queue(maxsize=1)
results_objects = None
results_fire = None
running = True

# ---- Thread 1: capture frames ----
def capture_frames():
    global running
    frame_skip = 2   # process 1 frame out of 3
    count = 0
    while running:
        ret, f = cap.read()
        if not ret or f is None:
            continue
        count += 1
        if count % frame_skip != 0:
            continue
        if not frame_queue.full():
            frame_queue.put(f)

# ---- Thread 2: general objects inference ----
def inference_objects():
    global results_objects, running
    while running:
        if not frame_queue.empty():
            f = frame_queue.get()
            f_resized = cv2.resize(f, (320, 192))
            with torch.no_grad():
                results_objects = model_objects.predict(f_resized, conf=0.4, classes=[0])

# ---- Thread 3: fire/smoke inference ----
def inference_fire_smoke():
    global results_fire, running
    while running:
        if not frame_queue.empty():
            f = frame_queue.get()
            f_resized = cv2.resize(f, (320, 192))
            with torch.no_grad():
                results_fire = model_fire_smoke.predict(f_resized, conf=0.2)

# ---- Start threads ----
threads = [
    threading.Thread(target=capture_frames, daemon=True),
    threading.Thread(target=inference_objects, daemon=True),
    threading.Thread(target=inference_fire_smoke, daemon=True)
]
for t in threads:
    t.start()

# ---- Main loop ----
while True:
    f = None
    r_objects = results_objects
    r_fire = results_fire

    if not frame_queue.empty():
        f = frame_queue.queue[-1].copy()   # take latest frame

    if f is not None and f.size > 0:
        h_scale = f.shape[1] / 320
        v_scale = f.shape[0] / 192

        # ---- General objects ----
        if r_objects is not None:
            for res in r_objects:
                boxes = res.boxes
                for box in boxes:
                    names = model_objects.names
                    cls = int(box.cls[0])
                    label = names[cls].lower()
                    if label == "person":
                        conf = float(box.conf[0]) * 100
                        if conf < 50:  # skip low-confidence boxes
                            continue
                        x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                        x1, y1, x2, y2 = int(x1*h_scale), int(y1*v_scale), int(x2*h_scale), int(y2*v_scale)
                        color = (0, 255, 255)
                        text = f"Person {conf:.1f}%"
                        cv2.rectangle(f, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(f, text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        # ---- Fire/Smoke ----
        if r_fire is not None:
            for res in r_fire:
                boxes = res.boxes
                for box in boxes:
                    names = model_fire_smoke.names
                    cls = int(box.cls[0])
                    label = names[cls].lower()
                    conf = float(box.conf[0]) * 100
                    if conf < 40:  # skip low-confidence boxes
                        continue
                    x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                    x1, y1, x2, y2 = int(x1*h_scale), int(y1*v_scale), int(x2*h_scale), int(y2*v_scale)
                    color = (0, 0, 255)
                    text = f"Action: {label.upper()} {conf:.1f}%"
                    cv2.rectangle(f, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(f, text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.putText(f, "Press 'q' to exit", (2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (155, 166, 255), 1)
        cv2.imshow("Detection", f)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        running = False
        break

cap.release()
cv2.destroyAllWindows()
