
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
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)

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
            results_objects = model_objects(f, conf=0.25, stream=False)

# ---- Thread 3: inferência fogo/fumo ----
def inference_fire_smoke():
    global frame, results_fire, running
    while running:
        f = None
        with lock:
            if frame is not None:
                f = cv2.resize(frame, (640, 384))
        if f is not None:
            results_fire = model_fire_smoke(f, conf=0.25, stream=False)

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
                names = model_objects.names
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                    x1, y1, x2, y2 = int(x1*h_scale), int(y1*v_scale), int(x2*h_scale), int(y2*v_scale)
                    cls = int(box.cls[0])
                    label = names[cls].lower()

                    color = (0,0,255) if label=="person" else (0,255,0)
                    text = "Pessoa" if label=="person" else label.capitalize()

                    cv2.rectangle(f, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(f, text, (x1, y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                    if label=="person":
                        roi_gray = cv2.cvtColor(f[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(roi_gray, 1.1, 5)
                        for (fx, fy, fw, fh) in faces:
                            cv2.rectangle(f, (x1+fx, y1+fy), (x1+fx+fw, y1+fy+fh), (255,0,0),2)
                            cv2.putText(f,"Rosto",(x1+fx,y1+fy-10),
                                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,0),2)

        # ---- Fogo/Fumo ----
        if r_fire is not None:
            for res in r_fire:
                boxes = res.boxes
                names = model_fire_smoke.names
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                    x1, y1, x2, y2 = int(x1*h_scale), int(y1*v_scale), int(x2*h_scale), int(y2*v_scale)
                    cls = int(box.cls[0])
                    label = names[cls].lower()

                    color = (0,0,255) if label=="fire" else (0,165,255)
                    text = "Acao: FOGO" if label=="fire" else "Acao: FUMO"
                    cv2.rectangle(f,(x1,y1),(x2,y2),color,2)
                    cv2.putText(f,text,(x1,y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX,0.7,color,2)

        cv2.imshow("Detecção Super Rápida", f)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        running=False
        break

cap.release()
cv2.destroyAllWindows()
