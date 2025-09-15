<<<<<<< HEAD
#pragma once
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "esp_err.h"
#include "driver/gpio.h" // Include for gpio_num_t

class Detector {
public:
    static esp_err_t init();
    static bool processFrame(const uint8_t* frame, int width, int height, size_t length);

private:
    static uint64_t lastAlertTime;
    static const gpio_num_t LED_GPIO = GPIO_NUM_2; // Inline initialization
    static const int COOLDOWN_MS = 5000;
};
=======
#pragma once
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "esp_err.h"
#include "driver/gpio.h" // Include for gpio_num_t

class Detector {
public:
    static esp_err_t init();
    static bool processFrame(const uint8_t* frame, int width, int height, size_t length);

private:
    static uint64_t lastAlertTime;
    static const gpio_num_t LED_GPIO = GPIO_NUM_2; // Inline initialization
    static const int COOLDOWN_MS = 5000;
};
>>>>>>> d31e8cd0349ebce9ce230923473a3a3b17772633
