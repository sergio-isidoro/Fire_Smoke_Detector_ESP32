idf_component_register(SRCS "model_data.cpp" "storage.cpp" "detector.cpp" "camera.cpp" "main.cpp"
                    INCLUDE_DIRS "."
                    REQUIRES tflite-micro esp32-camera sdmmc fatfs
)