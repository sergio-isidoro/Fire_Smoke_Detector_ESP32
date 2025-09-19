import sys
from pathlib import Path
import random
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# ----------------------------
# Configuration
# ----------------------------
DATASET_DIR = Path("train")  # Only this folder
IMAGES_DIR = DATASET_DIR / "images"
LABELS_DIR = DATASET_DIR / "labels"

OUTPUT_DIR = Path("dataset_fire_smoke_tf")
CLASSES = {0: "fire", 1: "smoke", 2: "neutral"}
CLASS_NAMES = list(CLASSES.values())

IMG_SIZE = (64, 64)  # Reduce to (32,32) for faster testing
BATCH_SIZE = 32
EPOCHS = 15
TEST_RATIO = 0.2
PROGRESS_STEP = 500  # Print every 500 images

# ----------------------------
# Check dataset
# ----------------------------
image_files = list(IMAGES_DIR.glob("*.jpg")) + list(IMAGES_DIR.glob("*.png"))
if len(image_files) == 0:
    print("❌ No images found in the dataset folder!")
    sys.exit(1)
print(f"✅ Found {len(image_files)} images in {IMAGES_DIR}")

# ----------------------------
# Prepare folders
# ----------------------------
for split in ["train", "test"]:
    for cls in CLASS_NAMES:
        (OUTPUT_DIR / split / cls).mkdir(parents=True, exist_ok=True)

# ----------------------------
# Split dataset
# ----------------------------
random.shuffle(image_files)
split_index = int(len(image_files) * (1 - TEST_RATIO))
train_imgs = image_files[:split_index]
test_imgs = image_files[split_index:]

# ----------------------------
# Function to process images
# ----------------------------
def process_and_copy(img_list, split):
    for i, img_path in enumerate(img_list, 1):
        # Read class from YOLO label
        label_file = LABELS_DIR / (img_path.stem + ".txt")
        if not label_file.exists():
            class_id = 2  # neutral
        else:
            with open(label_file) as f:
                lines = f.readlines()
                if len(lines) == 0:
                    class_id = 2
                else:
                    class_id = int(lines[0].split()[0])
        cls_name = CLASSES.get(class_id, "neutral")

        # Ensure save folder exists
        save_dir = OUTPUT_DIR / split / cls_name
        save_dir.mkdir(parents=True, exist_ok=True)

        # Resize and save image
        img = Image.open(img_path).convert("RGB").resize(IMG_SIZE)
        img.save(save_dir / img_path.name)

        # Print progress
        if i % PROGRESS_STEP == 0 or i == len(img_list):
            print(f"Processed {i}/{len(img_list)} images for {split}")

# ----------------------------
# Process images
# ----------------------------
print("Processing training images...")
process_and_copy(train_imgs, "train")
print("Processing test images...")
process_and_copy(test_imgs, "test")

# ----------------------------
# Load dataset
# ----------------------------
train_ds = tf.keras.utils.image_dataset_from_directory(
    OUTPUT_DIR / "train",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical"
)

test_ds = tf.keras.utils.image_dataset_from_directory(
    OUTPUT_DIR / "test",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical"
)

# Normalize
normalization_layer = layers.Rescaling(1./255)
train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
test_ds = test_ds.map(lambda x, y: (normalization_layer(x), y))

# ----------------------------
# Define CNN model
# ----------------------------
model = models.Sequential([
    layers.Conv2D(16, (3,3), activation='relu', input_shape=IMG_SIZE + (3,)),
    layers.MaxPooling2D(),
    layers.Conv2D(32, (3,3), activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(len(CLASSES), activation='softmax')
])

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# ----------------------------
# Train model
# ----------------------------
print("Starting training...")
history = model.fit(
    train_ds,
    validation_data=test_ds,
    epochs=EPOCHS
)

# ----------------------------
# Evaluate
# ----------------------------
loss, acc = model.evaluate(test_ds)
print(f"✅ Test accuracy: {acc*100:.2f}%")

# ----------------------------
# Confusion matrix
# ----------------------------
print("Generating confusion matrix...")
y_true = []
y_pred = []

for images, labels in test_ds:
    preds = model.predict(images)
    y_true.extend(np.argmax(labels.numpy(), axis=1))
    y_pred.extend(np.argmax(preds, axis=1))

cm = confusion_matrix(y_true, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=CLASS_NAMES)
disp.plot(cmap=plt.cm.Blues)
plt.title("Confusion Matrix")
plt.show()

# ----------------------------
# Export TFLite model
# ----------------------------
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open("fire_smoke_model.tflite", "wb") as f:
    f.write(tflite_model)

print("🔥 Exported model to fire_smoke_model.tflite")