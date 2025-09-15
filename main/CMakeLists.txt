idf_component_register(SRCS "web_server.cpp" "wifi_station.cpp" "shared_state.cpp" "model_data.cpp" "storage.cpp" "detector.cpp" "camera.cpp" "main.cpp"
                    INCLUDE_DIRS "."
                    REQUIRES tflite-micro esp32-camera sdmmc fatfs esp_wifi esp_event esp_netif esp_http_server nvs_flash
)