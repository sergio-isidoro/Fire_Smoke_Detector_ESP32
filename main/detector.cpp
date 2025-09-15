<<<<<<< HEAD
#include "detector.h"
#include "storage.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "model_data.h"

// TensorFlow Lite Micro headers
#include "tensorflow/lite/c/common.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"

#define TAG "DETECTOR"

// Initialize static members
uint64_t Detector::lastAlertTime = 0;

static const tflite::Model* model = nullptr;
static tflite::MicroInterpreter* interpreter = nullptr;
static TfLiteTensor* input = nullptr;
static uint8_t tensorArena[64*1024];  // Adjust size based on model

esp_err_t Detector::init() {
    // Initialize LED
    gpio_reset_pin(LED_GPIO);
    gpio_set_direction(LED_GPIO, GPIO_MODE_OUTPUT);
    gpio_set_level(LED_GPIO, 0);

    // Load TFLite model
    model = tflite::GetModel(model_data);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        ESP_LOGE(TAG, "Model schema version mismatch");
        return ESP_FAIL;
    }

    // Setup operator resolver
    static tflite::MicroMutableOpResolver<5> resolver;
    resolver.AddConv2D();
    resolver.AddMaxPool2D();
    resolver.AddFullyConnected();
    resolver.AddSoftmax();
    resolver.AddReshape();

    // Create interpreter
    static tflite::MicroInterpreter staticInterpreter(model, resolver, tensorArena, sizeof(tensorArena));
    interpreter = &staticInterpreter;

    if (interpreter->AllocateTensors() != kTfLiteOk) {
        ESP_LOGE(TAG, "Tensor allocation failed");
        return ESP_FAIL;
    }

    input = interpreter->input(0);
    ESP_LOGI(TAG, "Detector initialized successfully");
    return ESP_OK;
}

bool Detector::processFrame(const uint8_t* frame, int width, int height, size_t length) {
    if (!interpreter || !input) return false;

    // Preprocess frame: normalize to [0,1]
    int expectedSize = input->bytes / sizeof(float);
    for (int i = 0; i < expectedSize && i < width*height; i++) {
        input->data.f[i] = frame[i] / 255.0f;
    }

    // Run inference
    if (interpreter->Invoke() != kTfLiteOk) return false;

    // Get output probabilities
    TfLiteTensor* output = interpreter->output(0);
    float fireProb = output->data.f[0];
    float smokeProb = output->data.f[1];

    // Check cooldown using FreeRTOS tick count
    uint64_t now = xTaskGetTickCount() * portTICK_PERIOD_MS; // ms
    if ((fireProb > 0.5f || smokeProb > 0.5f) && (now - lastAlertTime > COOLDOWN_MS)) {
        lastAlertTime = now;
        gpio_set_level(LED_GPIO, 1);

        const char* label = fireProb > smokeProb ? "fire" : "smoke";
        ESP_LOGW(TAG, "🔥 Detection: %s", label);

        // Save frame to SD card
        Storage::saveImage(frame, length, label);

        return true;
    } else {
        gpio_set_level(LED_GPIO, 0);
        return false;
    }
}
=======
#include "detector.h"
#include "storage.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "model_data.h"

// TensorFlow Lite Micro headers
#include "tensorflow/lite/c/common.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"

#define TAG "DETECTOR"

// Initialize static members
uint64_t Detector::lastAlertTime = 0;

static const tflite::Model* model = nullptr;
static tflite::MicroInterpreter* interpreter = nullptr;
static TfLiteTensor* input = nullptr;
static uint8_t tensorArena[64*1024];  // Adjust size based on model

esp_err_t Detector::init() {
    // Initialize LED
    gpio_reset_pin(LED_GPIO);
    gpio_set_direction(LED_GPIO, GPIO_MODE_OUTPUT);
    gpio_set_level(LED_GPIO, 0);

    // Load TFLite model
    model = tflite::GetModel(model_data);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        ESP_LOGE(TAG, "Model schema version mismatch");
        return ESP_FAIL;
    }

    // Setup operator resolver
    static tflite::MicroMutableOpResolver<5> resolver;
    resolver.AddConv2D();
    resolver.AddMaxPool2D();
    resolver.AddFullyConnected();
    resolver.AddSoftmax();
    resolver.AddReshape();

    // Create interpreter
    static tflite::MicroInterpreter staticInterpreter(model, resolver, tensorArena, sizeof(tensorArena));
    interpreter = &staticInterpreter;

    if (interpreter->AllocateTensors() != kTfLiteOk) {
        ESP_LOGE(TAG, "Tensor allocation failed");
        return ESP_FAIL;
    }

    input = interpreter->input(0);
    ESP_LOGI(TAG, "Detector initialized successfully");
    return ESP_OK;
}

bool Detector::processFrame(const uint8_t* frame, int width, int height, size_t length) {
    if (!interpreter || !input) return false;

    // Preprocess frame: normalize to [0,1]
    int expectedSize = input->bytes / sizeof(float);
    for (int i = 0; i < expectedSize && i < width*height; i++) {
        input->data.f[i] = frame[i] / 255.0f;
    }

    // Run inference
    if (interpreter->Invoke() != kTfLiteOk) return false;

    // Get output probabilities
    TfLiteTensor* output = interpreter->output(0);
    float fireProb = output->data.f[0];
    float smokeProb = output->data.f[1];

    // Check cooldown using FreeRTOS tick count
    uint64_t now = xTaskGetTickCount() * portTICK_PERIOD_MS; // ms
    if ((fireProb > 0.5f || smokeProb > 0.5f) && (now - lastAlertTime > COOLDOWN_MS)) {
        lastAlertTime = now;
        gpio_set_level(LED_GPIO, 1);

        const char* label = fireProb > smokeProb ? "fire" : "smoke";
        ESP_LOGW(TAG, "🔥 Detection: %s", label);

        // Save frame to SD card
        Storage::saveImage(frame, length, label);

        return true;
    } else {
        gpio_set_level(LED_GPIO, 0);
        return false;
    }
}
>>>>>>> d31e8cd0349ebce9ce230923473a3a3b17772633
