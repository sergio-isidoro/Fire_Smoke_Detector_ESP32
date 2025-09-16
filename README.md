# Fire & Smoke Detection (Edge AI) ESP32-S3 Sense + TFCard + Web Server + Python Fine-Tuning

Real-time **fire and smoke detection** using **ESP32-S3 Sense** with camera module and **TFCard storage**, combined with **Python training & fine-tuning** of the detection model.  

The project has two parts:

1. **Python Scripts**: Training, fine-tuning, and testing a YOLO model for fire/smoke detection.
2. **ESP32 Firmware**: Real-time inference using TFLite Micro, camera capture, LED alert, cooldown, and TFCard storage.

---

## 📋 Features

### Python Side

- 🧠 **Model Fine-Tuning**: Train a YOLO model from scratch or fine-tune a pre-existing one on your custom dataset to specialize in fire and smoke detection.
- 📊 **Performance Evaluation**: Assess the model's performance using precision metrics and visualize the results with a confusion matrix.
- 💾 **Model Export**: Export the trained model to the `.pt` (PyTorch) format, making it ready for deployment.
- 🧪 **Parameter Tuning**: Easily customize thresholds like `min_confidence` and `iou_threshold` to optimize the trade-off between detection accuracy and speed.

### ESP32-S3 Side
- 🌐 **Camera Capture**: JPEG frames from OV2640 / ESP32-S3 camera.  
- 🔥 **Detection & LED**: TFLite Micro inference, GPIO LED alerts.  
- 💾 **TFCard Storage**: Save detection frames with timestamped filenames.  
- ⏱️ **Cooldown**: Prevents repeated detection triggers.  

---

## ✅ Compatible Hardware

- **ESP32-S3 Sense** (DevKit, AiThinker, **Seeed XIAO S3**)  
- Camera module OV2640 or compatible  
- TFCard/SD card slot for storage  

---

## ⚡ Operation Modes

- **Real-time Detection Loop**: Captures camera frames, performs TFLite Micro inference, triggers LED, and saves images on TFCard with timestamped filenames.  
- **Cooldown Mechanism**: Prevents repeated alerts within a configurable time interval (default: 5 seconds).  
- **TFCard Storage**: Saves images in JPEG format directly to SD/TFCard.  

---

## ⚙️ How to Train and Generate the Model File

Follow these steps to train your own model and prepare it for deployment on the ESP32.

### 1. Train the Model (on PC)
First, train or fine-tune the object detection model on your computer.

-   Prepare your **dataset** with images of fire, smoke, and no-fire scenarios.
-   Use the `fine_tune_model.py` script to train a **YOLO** model (e.g., YOLOv8 or higher) on your data.
-   At the end of the training, the best model will be saved as a `.pt` file (e.g., `models/model.pt`).

### 2. Convert the `.pt` Model to `.h`
To allow the microcontroller to read the model, we need to convert it into a C++ byte array.

-   Use the `RUN_export_pt-to-h.bat` script provided in the project.
-   Run the converter from your terminal, providing the trained model (`.pt`) as input and the desired header file (`.h`) as output:
    ```bash
    python export_pt-to-h.py models/model.pt model_data.h
    ```
-   This command will generate the `model_data.h` file, which contains the model in the correct format for the firmware.

### 3. Deploy to the ESP32
Finally, integrate the new model into the ESP32 firmware.

-   Replace the existing `model_data.h` file in your PlatformIO (or Arduino) project with the one you just generated.
-   Compile and upload the updated firmware to your ESP32 board.
-   The device will now use your custom model to detect fire and smoke, trigger alerts, and save images to the memory card.

---

## ⚙️ Code Structure

| File               | Description                                       |
|-------------------|--------------------------------------------------|
| `main.cpp`           | Main loop, initializes camera, detector, storage |
| `camera.cpp/h`       | Camera initialization and frame capture          |
| `detector.cpp/h`     | TFLite Micro inference, LED control, cooldown    |
| `storage.cpp/h`      | TFCard initialization and image saving           |
| `model_data.h`     | TFLite model array for ESP32 deployment          |

---

## 💡 Notes

- Fine-tuning improves detection on your specific environment.  
- Adjust `min_confidence` and `smoke_confidence` in the detector for better accuracy.  
- TFCard storage is optional but recommended for logging.  
- `COOLDOWN_MS` in `detector.cpp` can be modified to change alert frequency.  
- JPEG mode is recommended for fast storage and low memory usage.  

---

## 🚀 Project Status

- [x] 🔥 Fire detection model  
- [x] 💨 Smoke detection model  
- [ ] 💾 TF card storage  
- [ ] 🟢 Real-time camera input  
- [ ] 📊 Accuracy benchmark results  

---

# ✨ Thanks for using this project!

- Combines **Python YOLO fine-tuning** + **ESP32-S3 real-time detection**  
- Edge AI solution for fire and smoke monitoring  
- Modular and expandable: add Wi-Fi alerts, MQTT, buzzer, etc.

---

## 🎬 Video

<div align="center">

https://github.com/user-attachments/assets/c5750561-74fc-4f8f-a46b-9d0102d9603a

</div>
