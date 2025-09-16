import cv2
import sys
from config import Config
from fire_detector import Detector
import time
import logging

# --- Logging configuration to see detector error messages ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Function to choose the video source ---
def get_video_source():
    """
    Asks the user which video source to use (webcam or IP) and returns
    the appropriate identifier for OpenCV.
    """
    while True:
        print("Choose the video source:")
        print("1: Local Webcam")
        print("2: IP Camera (ESP32-S3)")
        choice = input("Enter your choice (1 or 2): ")

        if choice == '1':
            # Returns 0, which is the default index for the first webcam
            return 0
        elif choice == '2':
            ip_address = input("Enter the IP address of your ESP32-S3: ")
            
            # --- ADICIONADO: Pede a porta com 80 como padrão ---
            port_input = input("Enter the port (default is 80, just press Enter): ")
            port = "80" if not port_input else port_input
            
            # --- ALTERADO: Constrói a URL com a porta especificada ---
            url = f"http://{ip_address}:{port}/stream"
            
            print(f"Attempting to connect to stream: {url}")
            return url
        else:
            print("❌ Invalid choice. Please try again.\n")


# Coordinates for the "EXIT" button
BUTTON_X, BUTTON_Y, BUTTON_W, BUTTON_H = 20, 20, 200, 80

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if BUTTON_X <= x <= BUTTON_X + BUTTON_W and BUTTON_Y <= y <= BUTTON_Y + BUTTON_H:
            param['exit'] = True

def main():
    # Get the video source from the user
    video_source = get_video_source()

    try:
        # Initialize the detector
        detector = Detector(Config.MODEL_PATH, iou_threshold=0.20)

        # Open the chosen video source (webcam or IP)
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            print(f"❌ Could not open video source: {video_source}")
            sys.exit(1)

        # The resolution setting was removed as it can cause errors with IP streams
        
        alert_cooldown = Config.ALERT_COOLDOWN
        last_alert_time = 0
        next_detection_to_report = "any"

        # Set up the mouse callback
        mouse_param = {'exit': False}
        cv2.namedWindow("Fire Detection System")
        cv2.setMouseCallback("Fire Detection System", click_event, mouse_param)

        print("\n✅ System started. Press 'q' or click 'EXIT' to quit.")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to capture frame. The connection may have been lost.")
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

            # Draw the EXIT button
            cv2.rectangle(processed_frame, (BUTTON_X, BUTTON_Y),
                          (BUTTON_X + BUTTON_W, BUTTON_Y + BUTTON_H), (0,0,255), -1)
            cv2.putText(processed_frame, "EXIT", (BUTTON_X + 40, BUTTON_Y + 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 3)

            cv2.imshow("Fire Detection System", processed_frame)

            # Exit if the button is clicked or 'q' is pressed
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
