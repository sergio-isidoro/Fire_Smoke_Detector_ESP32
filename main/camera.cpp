#include "camera.h"
#include "esp_camera.h"
#include "esp_log.h"

static const char* TAG = "CAMERA";

esp_err_t Camera::init() {
    camera_config_t config = {
        .pin_pwdn = -1, 
        .pin_reset = -1, 
        .pin_xclk = 21,
        .pin_sccb_sda = 26, 
        .pin_sccb_scl = 27,
        .pin_d7 = 35, 
        .pin_d6 = 34, 
        .pin_d5 = 39, 
        .pin_d4 = 36,
        .pin_d3 = 19, 
        .pin_d2 = 18, 
        .pin_d1 = 5, 
        .pin_d0 = 4,
        .pin_vsync = 25, 
        .pin_href = 23, 
        .pin_pclk = 22,
        .xclk_freq_hz = 20000000,
        .ledc_timer = LEDC_TIMER_0, 
        .ledc_channel = LEDC_CHANNEL_0,
        .pixel_format = PIXFORMAT_JPEG,
        .frame_size = FRAMESIZE_QVGA,
        .jpeg_quality = 12,
        .fb_count = 1
    };

    if (esp_camera_init(&config) != ESP_OK) {
        ESP_LOGE(TAG, "Failed to initialize camera");
        return ESP_FAIL;
    }
    return ESP_OK;
}

esp_err_t Camera::captureFrame(uint8_t** buffer, size_t* length, int* width, int* height) {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) return ESP_FAIL;
    *buffer = fb->buf;
    *length = fb->len;
    *width = fb->width;
    *height = fb->height;
    return ESP_OK;
}

void Camera::returnFrame(uint8_t* buffer) {
    esp_camera_fb_return(reinterpret_cast<camera_fb_t*>(buffer));
}