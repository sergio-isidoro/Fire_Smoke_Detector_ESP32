#pragma once
#include <stdint.h>
#include <stddef.h>
#include "esp_err.h"

class Storage {
public:
    static esp_err_t init();
    static esp_err_t saveImage(const uint8_t* data, size_t len, const char* label);
};