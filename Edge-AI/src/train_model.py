# fine_tune_model.py
import os
from pathlib import Path
from ultralytics import YOLO
import yaml

# ----------------------------
# Paths & Config
# ----------------------------
PROJECT_ROOT = Path(__file__).parent
DATASET_DIR = PROJECT_ROOT / "dataset"  # organize as dataset/fire, dataset/smoke, dataset/no_fire
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

PRETRAINED_MODEL = MODEL_DIR / "model.pt"           # Pretrained model to fine-tune
OUTPUT_MODEL = MODEL_DIR / "model_fine-tuning.pt"   # Fine-tuned output

# ----------------------------
# Create dataset YAML for YOLO
# ----------------------------
dataset_yaml = {
    "train": str(DATASET_DIR / "train"),
    "val": str(DATASET_DIR / "val"),
    "names": ["no_fire", "fire", "smoke"]
}

yaml_path = PROJECT_ROOT / "dataset.yaml"
with open(yaml_path, "w") as f:
    yaml.dump(dataset_yaml, f)

print(f"Dataset YAML created at {yaml_path}")

# ----------------------------
# Load YOLO model
# ----------------------------
model = YOLO(str(PRETRAINED_MODEL))
print(f"Loaded pretrained model from {PRETRAINED_MODEL}")

# ----------------------------
# Training parameters
# ----------------------------
EPOCHS = 100
IMG_SIZE = 640
BATCH_SIZE = 16
LEARNING_RATE = 0.001
DEVICE = "0"  # GPU 0 or CPU as 'cpu'

# ----------------------------
# Fine-tune
# ----------------------------
print("Starting fine-tuning YOLOv11...")
results = model.train(
    data=str(yaml_path),
    epochs=EPOCHS,
    imgsz=IMG_SIZE,
    batch=BATCH_SIZE,
    lr=LEARNING_RATE,
    device=DEVICE,
    name="fire_smoke_model",
    exist_ok=True
)

# ----------------------------
# Save fine-tuned model
# ----------------------------
if results.best is not None:
    # Export best checkpoint to PyTorch
    best_model_path = results.best
    print(f"Best checkpoint found at: {best_model_path}")
    
    # Save as model_fine-tuning.pt
    model.model.export(format="pt")
    model.model.save(str(OUTPUT_MODEL))
    print(f"✅ Fine-tuned model saved as {OUTPUT_MODEL}")
else:
    print("⚠️ No best checkpoint found, training may have failed.")
