#include "shared_state.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

static SemaphoreHandle_t state_mutex = NULL;
static bool detection_status = false;

void shared_state_init() {
    state_mutex = xSemaphoreCreateMutex();
}

void set_detection_status(bool status) {
    if (xSemaphoreTake(state_mutex, portMAX_DELAY)) {
        detection_status = status;
        xSemaphoreGive(state_mutex);
    }
}

bool get_detection_status() {
    bool status = false;
    if (xSemaphoreTake(state_mutex, (TickType_t)20)) { // Timeout de 20 ticks
        status = detection_status;
        xSemaphoreGive(state_mutex);
    }
    return status;
}
