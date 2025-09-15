#include "camera.h"
#include "detector.h"
#include "storage.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "nvs_flash.h"

// Includes dos novos módulos
#include "wifi_station.h"
#include "web_server.h"
#include "shared_state.h"

#define WIFI_SSID "COLOQUE_AQUI_O_NOME_DA_SUA_REDE"
#define WIFI_PASS "COLOQUE_AQUI_A_SENHA_DA_SUA_REDE"

extern "C" void app_main() {
    ESP_LOGI("MAIN", "Starting Fire Detection System...");

    // 1. Inicializar NVS (necessário para o Wi-Fi)
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
      ESP_ERROR_CHECK(nvs_flash_erase());
      ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // 2. Inicializar o estado partilhado
    shared_state_init();

    // 3. Conectar ao Wi-Fi
    wifi_init_sta(WIFI_SSID, WIFI_PASS);

    // 4. Inicializar os módulos de hardware e software
    Storage::init(); //
    Camera::init(); //
    Detector::init(); //

    // 5. Iniciar o servidor web (corre nas suas próprias tarefas)
    start_web_server();

    ESP_LOGI("MAIN", "Initialization complete. Starting detection loop.");
    
    // 6. Loop principal para deteção
    while (true) {
        uint8_t* frame = NULL;
        size_t length = 0;
        int width = 0, height = 0;

        // Captura um frame
        if (Camera::captureFrame(&frame, &length, &width, &height) == ESP_OK) {
            // Processa o frame para deteção
            bool detected = Detector::processFrame(frame, width, height, length);
            
            // Atualiza o estado global para o servidor web
            set_detection_status(detected);

            // Liberta o frame
            Camera::returnFrame(frame);
        } else {
            ESP_LOGE("MAIN", "Failed to capture frame");
        }

        // Delay para controlar a taxa de inferência
        vTaskDelay(pdMS_TO_TICKS(200)); 
    }
}
