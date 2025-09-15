idf_component_register(SRCS "web_server.cpp" "wifi_station.cpp" "shared_state.cpp" "model_data.cpp" "storage.cpp" "detector.cpp" "camera.cpp" "main.cpp"
                    INCLUDE_DIRS "."
                    REQUIRES tflite-micro esp32-camera sdmmc fatfs
)