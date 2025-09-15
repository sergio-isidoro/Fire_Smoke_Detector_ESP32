#include "web_server.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_camera.h"
#include "shared_state.h" // To access detection status

static const char *TAG = "WEB_SERVER";

// Handler for MJPEG video stream
static esp_err_t stream_handler(httpd_req_t *req) {
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    char part_buf[128];

    res = httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=--frame");
    if (res != ESP_OK) {
        return res;
    }

    while (true) {
        fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE(TAG, "Camera capture failed");
            res = ESP_FAIL;
        } else {
            if (fb->format == PIXFORMAT_JPEG) {
                res = httpd_resp_send_chunk(req, "--frame\r\n", 9);
                if (res == ESP_OK) {
                    sprintf(part_buf, "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", fb->len);
                    res = httpd_resp_send_chunk(req, part_buf, strlen(part_buf));
                }
                if (res == ESP_OK) {
                    res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
                }
                if (res == ESP_OK) {
                    res = httpd_resp_send_chunk(req, "\r\n", 2);
                }
            }
        }
        
        if (fb) {
            esp_camera_fb_return(fb);
        }

        if (res != ESP_OK) {
            break; // Exit loop if there is a send error
        }
        
        vTaskDelay(pdMS_TO_TICKS(100)); // Small delay to avoid overload
    }
    return res;
}

// Handler for detection status (returns JSON)
static esp_err_t status_handler(httpd_req_t *req) {
    httpd_resp_set_type(req, "application/json");
    const char *json_response;

    if (get_detection_status()) {
        json_response = "{\"status\":\"detected\"}";
    } else {
        json_response = "{\"status\":\"clear\"}";
    }
    
    return httpd_resp_send(req, json_response, strlen(json_response));
}

// Handler for the main HTML page
static esp_err_t index_handler(httpd_req_t *req) {
    const char* html = R"html(
<html>
<head>
<title>ESP32 Fire Detection</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; text-align: center; background-color: #282c34; color: white; }
    h1 { font-weight: 300; }
    #stream { border: 5px solid #4CAF50; border-radius: 8px; }
    #stream.detected { border: 5px solid #F44336; }
    h1.detected { color: #F44336; font-weight: 500; }
</style>
</head>
<body>
    <h1 id="title">Fire Detection System</h1>
    <img id="stream" src="/stream" width="320" height="240">
    <script>
        setInterval(function() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    const img = document.getElementById('stream');
                    const title = document.getElementById('title');
                    if (data.status === 'detected') {
                        img.classList.add('detected');
                        title.classList.add('detected');
                        title.innerText = "ALERT: FIRE/SMOKE DETECTED!";
                    } else {
                        img.classList.remove('detected');
                        title.classList.remove('detected');
                        title.innerText = "Fire Detection System";
                    }
                })
                .catch(error => console.error('Error fetching status:', error));
        }, 1000); // Check status every second
    </script>
</body>
</html>
)html";
    return httpd_resp_send(req, html, strlen(html));
}

void start_web_server() {
    httpd_handle_t server = NULL;
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.lru_purge_enable = true;

    ESP_LOGI(TAG, "Starting server on port: '%d'", config.server_port);
    if (httpd_start(&server, &config) == ESP_OK) {
        httpd_uri_t index_uri = { "/", HTTP_GET, index_handler, NULL };
        httpd_register_uri_handler(server, &index_uri);

        httpd_uri_t status_uri = { "/status", HTTP_GET, status_handler, NULL };
        httpd_register_uri_handler(server, &status_uri);

        httpd_uri_t stream_uri = { "/stream", HTTP_GET, stream_handler, NULL };
        httpd_register_uri_handler(server, &stream_uri);
    } else {
        ESP_LOGI(TAG, "Error starting server!");
    }
}
