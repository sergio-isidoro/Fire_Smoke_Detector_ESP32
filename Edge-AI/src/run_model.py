
import cv2
import threading
from ultralytics import YOLO

# ---- Modelos ----
MODEL_OBJECTS_PATH = "../models/yolo11n.pt"       # objetos gerais
MODEL_FIRE_SMOKE_PATH = "../models/model.pt"      # fogo/fumo

# ---- Modelos ----
model_objects = YOLO(MODEL_OBJECTS_PATH)
model_fire_smoke = YOLO(MODEL_FIRE_SMOKE_PATH)

# Classificador facial
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Webcam
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 384)

frame = None
results_objects = None
results_fire = None
lock = threading.Lock()
running = True

# ---- Thread 1: captura de frames ----
def capture_frames():
    global frame, running
    while running:
        ret, f = cap.read()
        if not ret or f is None:
            continue
        with lock:
            frame = f

# ---- Thread 2: inferência objetos gerais ----
def inference_objects():
    global frame, results_objects, running
    while running:
        f = None
        with lock:
            if frame is not None:
                # Reduz tamanho para inferência mais rápida
                f = cv2.resize(frame, (640, 384))
        if f is not None:
            results_objects = model_objects(f, conf=0.4, stream=False, classes=[0])

# ---- Thread 3: inferência fogo/fumo ----
def inference_fire_smoke():
    global frame, results_fire, running
    while running:
        f = None
        with lock:
            if frame is not None:
                f = cv2.resize(frame, (640, 384))
        if f is not None:
            results_fire = model_fire_smoke(f, conf=0.2, stream=False)

# Iniciar threads
threads = [
    threading.Thread(target=capture_frames, daemon=True),
    threading.Thread(target=inference_objects, daemon=True),
    threading.Thread(target=inference_fire_smoke, daemon=True)
]
for t in threads:
    t.start()

# ---- Loop principal ----
while True:
    f = None
    r_objects = None
    r_fire = None
    with lock:
        if frame is not None:
            f = frame.copy()
        if results_objects is not None:
            r_objects = results_objects
        if results_fire is not None:
            r_fire = results_fire

    if f is not None and f.size > 0:
        h_scale = f.shape[1] / 640
        v_scale = f.shape[0] / 384

        # ---- Objetos gerais ----
        if r_objects is not None:
            for res in r_objects:
                boxes = res.boxes
                
                for box in boxes:
                    names = model_objects.names
                    cls = int(box.cls[0])
                    label = names[cls].lower()
                
                    if label=="person":
                        x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                        x1, y1, x2, y2 = int(x1*h_scale), int(y1*v_scale), int(x2*h_scale), int(y2*v_scale)
                        color = (0,255,255)
                        conf = float(box.conf[0]) * 100
                        text = f"Person {conf:.1f}%"
                        cv2.rectangle(f, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(f, text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        # ---- Fogo/Fumo ----
        if r_fire is not None:
            for res in r_fire:
                boxes = res.boxes
                
                for box in boxes:
                    names = model_fire_smoke.names
                    x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                    x1, y1, x2, y2 = int(x1*h_scale), int(y1*v_scale), int(x2*h_scale), int(y2*v_scale)
                    cls = int(box.cls[0])
                    label = names[cls].lower()

                    if label=="fire":
                        color = (0,0,255)
                        conf = float(box.conf[0]) * 100
                        text = f"Acao: FOGO {conf:.1f}%"
                        cv2.rectangle(f,(x1,y1),(x2,y2),color,2)
                        cv2.putText(f,text,(x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX,0.4,color,1)

                    if label=="smoke":
                        color = (0,0,255)
                        conf = float(box.conf[0]) * 100
                        text = f"Acao: Fumo {conf:.1f}%"
                        cv2.rectangle(f,(x1,y1),(x2,y2),color,2)
                        cv2.putText(f,text,(x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX,0.7,color,2)
        
        cv2.putText(f, "Press 'q' to exit", (2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (155,166,255), 1)
        cv2.imshow("Detection", f)
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        running=False
        break

cap.release()
cv2.destroyAllWindows()
