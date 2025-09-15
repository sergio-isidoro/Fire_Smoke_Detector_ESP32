# Fire & Smoke Detection (Edge AI) ESP32-S3 Sense + TFCard + Python Fine-Tuning

Real-time **fire and smoke detection** using **ESP32-S3 Sense** with camera module and **TFCard storage**, combined with **Python training & fine-tuning** of the detection model.  

The project has two parts:

1. **Python Scripts**: Training, fine-tuning, and testing a YOLO model for fire/smoke detection.
2. **ESP32 Firmware**: Real-time inference using TFLite Micro, camera capture, LED alert, cooldown, and TFCard storage.

---

## 📋 Features

### Python Side
- 🖥️ **Fine-tuning**: Train or continue training a YOLOv11 model with your own dataset.  
- 📊 **Model Evaluation**: Test model performance with metrics and confusion matrix.  
- 💾 **Export `.pt` model**: Save as `model.pt` to deploy on ESP32.  
- 🧪 **Adjust thresholds**: Customize `min_confidence` and `smoke_confidence`.

### ESP32-S3 Side
- 🌐 **Camera Capture**: JPEG frames from OV2640 / ESP32-S3 camera.  
- 🔥 **Detection & LED**: TFLite Micro inference, GPIO LED alerts.  
- 💾 **TFCard Storage**: Save detection frames with timestamped filenames.  
- ⏱️ **Cooldown**: Prevents repeated detection triggers.  

---

## ✅ Compatible Hardware

- **ESP32-S3 Sense** (DevKit, AiThinker, Seeed XIAO S3)  
- Camera module OV2640 or compatible  
- TFCard/SD card slot for storage  

---

## ⚡ Operation Modes

- **Real-time Detection Loop**: Captures camera frames, performs TFLite Micro inference, triggers LED, and saves images on TFCard with timestamped filenames.  
- **Cooldown Mechanism**: Prevents repeated alerts within a configurable time interval (default: 5 seconds).  
- **TFCard Storage**: Saves images in JPEG format directly to SD/TFCard.  

---

## ⚙️ How to Train the Model and Generate `model.h`

1. **Train or Fine-Tune the Model in Python**:
   - Use your dataset of fire, smoke, and no-fire images.
   - Fine-tune the YOLOv11 model to improve detection on your environment.
   - Export the trained model as a `.pt` file, for example `model.pt`.

2. **Convert `.pt` to TensorFlow Lite (`.tflite`)**:
   - Use `torch2tflite` or an export script to convert the PyTorch `.pt` model to `.tflite`.
   - Ensure optimizations for microcontrollers (quantization recommended).

3. **Generate `model.h` for ESP32**:
   - Convert `.tflite` file into a C header file containing a byte array (`model.h`) for inclusion in ESP32 firmware.
   - Tools like `xxd` or Python scripts can produce this:
     ```
     xxd -i model.tflite > model_data.h
     ```
   - Include `model_data.h` in your firmware to load the TFLite model into memory.

4. **Deploy to ESP32**:
   - Flash the firmware with `main.c`, `detector.c/h`, `camera.c/h`, `storage.c/h` and `model_data.h`.
   - The ESP32 will run the model on camera frames, trigger LED, and save images on TFCard.

---

## ⚙️ Code Structure

| File               | Description                                       |
|-------------------|--------------------------------------------------|
| `main.c`           | Main loop, initializes camera, detector, storage |
| `camera.c/h`       | Camera initialization and frame capture          |
| `detector.c/h`     | TFLite Micro inference, LED control, cooldown    |
| `storage.c/h`      | TFCard initialization and image saving           |
| `model_data.h`     | TFLite model array for ESP32 deployment          |

---

## 💡 Notes

- Fine-tuning improves detection on your specific environment.  
- Adjust `min_confidence` and `smoke_confidence` in the detector for better accuracy.  
- TFCard storage is optional but recommended for logging.  
- `COOLDOWN_MS` in `detector.c` can be modified to change alert frequency.  
- JPEG mode is recommended for fast storage and low memory usage.  

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
