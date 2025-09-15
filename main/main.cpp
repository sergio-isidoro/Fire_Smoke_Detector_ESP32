#include "camera.h"
#include "detector.h"
#include "storage.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "nvs_flash.h"

// Includes for new modules
#include "wifi_station.h"
#include "web_server.h"
#include "shared_state.h"

#define WIFI_SSID "PUT_YOUR_NETWORK_NAME_HERE"
#define WIFI_PASS "PUT_YOUR_NETWORK_PASSWORD_HERE"

extern "C" void app_main() {
    ESP_LOGI("MAIN", "Starting Fire Detection System...");

    // 1. Initialize NVS (required for Wi-Fi)
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
      ESP_ERROR_CHECK(nvs_flash_erase());
      ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // 2. Initialize shared state
    shared_state_init();

    // 3. Connect to Wi-Fi
    wifi_init_sta(WIFI_SSID, WIFI_PASS);

    // 4. Initialize hardware and software modules
    Storage::init();
    Camera::init();
    Detector::init();

    // 5. Start the web server (runs in its own tasks)
    start_web_server();

    ESP_LOGI("MAIN", "Initialization complete. Starting detection loop.");
    
    // 6. Main detection loop
    while (true) {
        uint8_t* frame = NULL;
        size_t length = 0;
        int width = 0, height = 0;

        // Capture a frame
        if (Camera::captureFrame(&frame, &length, &width, &height) == ESP_OK) {
            // Process the frame for detection
            bool detected = Detector::processFrame(frame, width, height, length);
            
            // Update global state for the web server
            set_detection_status(detected);

            // Release the frame
            Camera::returnFrame(frame);
        } else {
            ESP_LOGE("MAIN", "Failed to capture frame");
        }

        // Delay to control inference rate
        vTaskDelay(pdMS_TO_TICKS(200)); 
    }
}
