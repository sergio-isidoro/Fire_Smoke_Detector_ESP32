import cv2
import sys
from config import Config
from fire_detector import Detector
import time

# Coordinates of the "EXIT" button for Full HD
BUTTON_X, BUTTON_Y, BUTTON_W, BUTTON_H = 20, 20, 200, 80

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if BUTTON_X <= x <= BUTTON_X + BUTTON_W and BUTTON_Y <= y <= BUTTON_Y + BUTTON_H:
            param['exit'] = True

def main():
    try:
        # Initialize detector
        detector = Detector(Config.MODEL_PATH, iou_threshold=0.20)
        
        # Open webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Could not open webcam")
            sys.exit(1)

        # Set Full HD resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        alert_cooldown = Config.ALERT_COOLDOWN
        last_alert_time = 0
        next_detection_to_report = "any"

        # Set mouse callback
        mouse_param = {'exit': False}
        cv2.namedWindow("Fire Detection System")
        cv2.setMouseCallback("Fire Detection System", click_event, mouse_param)

        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to capture frame from webcam")
                break

            # Detection pipeline
            processed_frame, detection = detector.process_frame(frame)

            if detection:
                current_time = time.time()
                if (next_detection_to_report == "any" or detection == next_detection_to_report) \
                        and (current_time - last_alert_time) > alert_cooldown:
                    print(f"🐦‍🔥 {detection} detected!")
                    last_alert_time = current_time
                    next_detection_to_report = "Smoke" if detection == "Fire" else "Fire"

            # Draw EXIT button
            cv2.rectangle(processed_frame, (BUTTON_X, BUTTON_Y), 
                          (BUTTON_X + BUTTON_W, BUTTON_Y + BUTTON_H), (0,0,255), -1)
            cv2.putText(processed_frame, "EXIT", (BUTTON_X + 40, BUTTON_Y + 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 3)

            cv2.imshow("Fire Detection System", processed_frame)

            # Exit if button clicked or 'q' pressed
            if cv2.waitKey(1) & 0xFF == ord('q') or mouse_param['exit']:
                break

    except Exception as e:
        print(f"🚨 Critical failure: {str(e)}")
        sys.exit(1)
    finally:
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()