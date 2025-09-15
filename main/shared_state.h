#pragma once
#include <stdbool.h>

void shared_state_init();
void set_detection_status(bool status);
bool get_detection_status();
