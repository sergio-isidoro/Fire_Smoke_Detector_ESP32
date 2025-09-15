<<<<<<< HEAD
#include "storage.h"
#include "esp_log.h"
#include "esp_vfs_fat.h"
#include "driver/sdmmc_host.h"
#include <stdio.h>
#include <time.h>

static const char* TAG = "STORAGE";
static sdmmc_card_t* card = nullptr;

esp_err_t Storage::init() {
    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
        .format_if_mount_failed = false,
        .max_files = 5,
        .allocation_unit_size = 16 * 1024
    };
    sdmmc_host_t host = SDMMC_HOST_DEFAULT();
    sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();

    esp_err_t ret = esp_vfs_fat_sdmmc_mount("/sdcard", &host, &slot_config, &mount_config, &card);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to mount SD card: %s", esp_err_to_name(ret));
        return ret;
    }

    return ESP_OK;
}

esp_err_t Storage::saveImage(const uint8_t* data, size_t len, const char* label) {
    char filename[64];
    time_t now; struct tm timeinfo;
    time(&now); localtime_r(&now, &timeinfo);

    snprintf(filename, sizeof(filename), "/sdcard/%s_%04d%02d%02d_%02d%02d%02d.jpg",
             label,
             timeinfo.tm_year + 1900,
             timeinfo.tm_mon + 1,
             timeinfo.tm_mday,
             timeinfo.tm_hour,
             timeinfo.tm_min,
             timeinfo.tm_sec);

    FILE* f = fopen(filename, "wb");
    if (!f) return ESP_FAIL;

    fwrite(data, 1, len, f);
    fclose(f);
    ESP_LOGI(TAG, "Image saved: %s", filename);
    return ESP_OK;
}
=======
#include "storage.h"
#include "esp_log.h"
#include "esp_vfs_fat.h"
#include "driver/sdmmc_host.h"
#include <stdio.h>
#include <time.h>

static const char* TAG = "STORAGE";
static sdmmc_card_t* card = nullptr;

esp_err_t Storage::init() {
    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
        .format_if_mount_failed = false,
        .max_files = 5,
        .allocation_unit_size = 16 * 1024
    };
    sdmmc_host_t host = SDMMC_HOST_DEFAULT();
    sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();

    esp_err_t ret = esp_vfs_fat_sdmmc_mount("/sdcard", &host, &slot_config, &mount_config, &card);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to mount SD card: %s", esp_err_to_name(ret));
        return ret;
    }

    return ESP_OK;
}

esp_err_t Storage::saveImage(const uint8_t* data, size_t len, const char* label) {
    char filename[64];
    time_t now; struct tm timeinfo;
    time(&now); localtime_r(&now, &timeinfo);

    snprintf(filename, sizeof(filename), "/sdcard/%s_%04d%02d%02d_%02d%02d%02d.jpg",
             label,
             timeinfo.tm_year + 1900,
             timeinfo.tm_mon + 1,
             timeinfo.tm_mday,
             timeinfo.tm_hour,
             timeinfo.tm_min,
             timeinfo.tm_sec);

    FILE* f = fopen(filename, "wb");
    if (!f) return ESP_FAIL;

    fwrite(data, 1, len, f);
    fclose(f);
    ESP_LOGI(TAG, "Image saved: %s", filename);
    return ESP_OK;
}
>>>>>>> d31e8cd0349ebce9ce230923473a3a3b17772633
