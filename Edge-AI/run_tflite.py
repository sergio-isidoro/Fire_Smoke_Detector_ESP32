import cv2
import threading
import torch
from ultralytics import YOLO
import queue
import numpy as np
import tensorflow as tf

# ---- Paths ----
MODEL_OBJECTS_PATH = "models/yolo11n.pt"
MODEL_FIRE_SMOKE_TFLITE = "fire_smoke_model.tflite"

# ---- Device setup for YOLO ----
device = "cuda" if torch.cuda.is_available() else "cpu"

# ---- Load YOLO general objects model ----
model_objects = YOLO(MODEL_OBJECTS_PATH).to(device)
if device == "cuda":
    model_objects.half()

# ---- Load TFLite Fire/Smoke model ----
interpreter = tf.lite.Interpreter(model_path=MODEL_FIRE_SMOKE_TFLITE)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
tflite_input_size = input_details[0]['shape'][1:3]  # height, width
fire_classes = ["fire", "smoke", "neutral"]

# ---- Webcam ----
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 192)

# ---- Shared frame queue ----
frame_queue = queue.Queue(maxsize=1)
results_objects = None
results_fire = []
running = True

# ---- IoU function to merge overlapping boxes ----
def iou(box1, box2):
    xA = max(box1[2], box2[2])
    yA = max(box1[3], box2[3])
    xB = min(box1[4], box2[4])
    yB = min(box1[5], box2[5])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    box1Area = (box1[4]-box1[2])*(box1[5]-box1[3])
    box2Area = (box2[4]-box2[2])*(box2[5]-box2[3])
    return interArea / float(box1Area + box2Area - interArea + 1e-6)

# ---- Thread 1: capture frames ----
def capture_frames():
    global running
    frame_skip = 2
    count = 0
    while running:
        ret, f = cap.read()
        if not ret or f is None:
            continue
        count += 1
        if count % frame_skip != 0:
            continue
        # Keep only latest frame
        while not frame_queue.empty():
            frame_queue.get()
        frame_queue.put(f)

# ---- Thread 2: YOLO person detection ----
def inference_objects():
    global results_objects, running
    while running:
        if not frame_queue.empty():
            f = frame_queue.queue[-1].copy()  # latest frame
            f_resized = cv2.resize(f, (320, 192))
            with torch.no_grad():
                results_objects = model_objects.predict(f_resized, conf=0.4, classes=[0])

# ---- Thread 3: Fire/Smoke multi-patch TFLite ----
def inference_fire_smoke():
    global results_fire, running
    patch_size = tflite_input_size[0]
    stride = patch_size  # no overlap for speed
    smoke_threshold = 0.65
    fire_threshold = 0.4

    while running:
        if not frame_queue.empty():
            f = frame_queue.queue[-1].copy()  # latest frame
            results_fire = []
            h, w, _ = f.shape
            for y in range(0, h - patch_size + 1, stride):
                for x in range(0, w - patch_size + 1, stride):
                    patch = f[y:y+patch_size, x:x+patch_size]
                    patch_rgb = cv2.cvtColor(patch, cv2.COLOR_BGR2RGB).astype(np.float32)/255.0
                    patch_rgb = np.expand_dims(patch_rgb, axis=0)
                    interpreter.set_tensor(input_details[0]['index'], patch_rgb)
                    interpreter.invoke()
                    preds = interpreter.get_tensor(output_details[0]['index'])[0]
                    cls_id = int(np.argmax(preds))
                    conf = float(preds[cls_id])

                    if cls_id == 0 and conf >= fire_threshold:
                        results_fire.append((cls_id, conf, x, y, x+patch_size, y+patch_size))
                    elif cls_id == 1 and conf >= smoke_threshold:
                        results_fire.append((cls_id, conf, x, y, x+patch_size, y+patch_size))

            # Merge overlapping smoke boxes
            merged = []
            for box in results_fire:
                if box[0] == 1:
                    added = False
                    for i, m in enumerate(merged):
                        if m[0] == 1 and iou(box, m) > 0.3:
                            merged[i] = (1,
                                         max(box[1], m[1]),
                                         min(box[2], m[2]),
                                         min(box[3], m[3]),
                                         max(box[4], m[4]),
                                         max(box[5], m[5]))
                            added = True
                            break
                    if not added:
                        merged.append(box)
                else:
                    merged.append(box)
            results_fire = merged

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
    f_display = None
    r_objects = results_objects
    r_fire = results_fire

    if not frame_queue.empty():
        f_display = frame_queue.queue[-1].copy()

    if f_display is not None and f_display.size > 0:
        h_scale = f_display.shape[1] / 320
        v_scale = f_display.shape[0] / 192

        # ---- YOLO person ----
        if r_objects is not None:
            for res in r_objects:
                boxes = res.boxes
                for box in boxes:
                    names = model_objects.names
                    cls = int(box.cls[0])
                    label = names[cls].lower()
                    if label == "person":
                        conf_obj = float(box.conf[0]) * 100
                        if conf_obj < 50:
                            continue
                        x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                        x1, y1, x2, y2 = int(x1*h_scale), int(y1*v_scale), int(x2*h_scale), int(y2*v_scale)
                        color = (0, 255, 255)
                        text = f"Person {conf_obj:.1f}%"
                        cv2.rectangle(f_display, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(f_display, text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        # ---- Fire/Smoke ----
        if r_fire is not None:
            for cls_id, conf, x1, y1, x2, y2 in r_fire:
                label = fire_classes[cls_id].upper()
                color = (0,0,255) if label=="FIRE" else (0,165,255)
                cv2.rectangle(f_display, (x1,y1), (x2,y2), color, 2)
                cv2.putText(f_display, f"{label} {conf*100:.1f}%", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        cv2.putText(f_display, "Press 'q' to exit", (2,12), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (155,166,255),1)
        cv2.imshow("Detection", f_display)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        running = False
        break

cap.release()
cv2.destroyAllWindows()
