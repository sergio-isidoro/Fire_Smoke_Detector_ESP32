<<<<<<< HEAD
#pragma once
#include <stdint.h>
#include "esp_err.h"

class Camera {
public:
    static esp_err_t init();
    static esp_err_t captureFrame(uint8_t** buffer, size_t* length, int* width, int* height);
    static void returnFrame(uint8_t* buffer);
};
=======
#pragma once
#include <stdint.h>
#include "esp_err.h"

class Camera {
public:
    static esp_err_t init();
    static esp_err_t captureFrame(uint8_t** buffer, size_t* length, int* width, int* height);
    static void returnFrame(uint8_t* buffer);
};
>>>>>>> d31e8cd0349ebce9ce230923473a3a3b17772633
