#include "camera.h"
#include "detector.h"
#include "storage.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

extern "C" void app_main() {
    ESP_LOGI("MAIN", "Starting Fire Detection System...");

    Storage::init();
    Camera::init();
    Detector::init();

    while (true) {
        uint8_t* frame;
        size_t length;
        int width, height;

        if (Camera::captureFrame(&frame, &length, &width, &height) == ESP_OK) {
            Detector::processFrame(frame, width, height, length);
            Camera::returnFrame(frame);
        }

        vTaskDelay(200 / portTICK_PERIOD_MS); // ~5 FPS
    }
}