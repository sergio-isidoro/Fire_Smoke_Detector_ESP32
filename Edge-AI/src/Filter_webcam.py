import cv2
import numpy as np

# --- Initial Settings ---
# Global variable to store the active filter
active_filter = "None"

# Dictionary to define the buttons (text, position, dimensions)
buttons = {
    "None":      (20, 20, 150, 40),
    "Grayscale": (20, 70, 150, 40),
    "Negative":  (20, 120, 150, 40),
    "Canny":     (20, 170, 150, 40),
    "Sepia":     (20, 220, 150, 40),
    "Color":     (20, 270, 150, 40),
}

# Callback function for mouse events (button clicks)
def manage_clicks(event, x, y, flags, param):
    global active_filter
    # If the left mouse button is pressed
    if event == cv2.EVENT_LBUTTONDOWN:
        # Check if the click was inside any of our buttons
        for name, (bx, by, bw, bh) in buttons.items():
            if bx <= x <= bx + bw and by <= y <= by + bh:
                active_filter = name
                print(f"Active filter: {active_filter}")
                break

# Empty function for the sliders (trackbars)
def nothing(x):
    pass

# --- Main Function ---
def main():
    global active_filter

    # Start video capture from the first webcam (index 0)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Create the main window and associate the mouse callback function
    window_name = "Webcam Filters - Press 'q' to exit"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, manage_clicks)

    # Create a separate window for the color controls (sliders)
    controls_name = "Color Controls (for 'Color' Filter)"
    cv2.namedWindow(controls_name)
    cv2.resizeWindow(controls_name, 600, 300)

    # Create the sliders for the color filter (HSV color space)
    # H -> Hue, S -> Saturation, V -> Value/Brightness
    cv2.createTrackbar("H Min", controls_name, 0, 179, nothing)
    cv2.createTrackbar("H Max", controls_name, 179, 179, nothing)
    cv2.createTrackbar("S Min", controls_name, 0, 255, nothing)
    cv2.createTrackbar("S Max", controls_name, 255, 255, nothing)
    cv2.createTrackbar("V Min", controls_name, 0, 255, nothing)
    cv2.createTrackbar("V Max", controls_name, 255, 255, nothing)

    # Main loop that runs while the camera is open
    while True:
        # Capture a frame from the camera
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Flip the frame horizontally (mirror effect)
        frame = cv2.flip(frame, 1) # <-- THIS IS THE CORRECTED LINE
        
        # Copy the original frame to apply the filter to
        filtered_frame = frame.copy()

        # --- Filter Application ---
        if active_filter == "Grayscale":
            # Convert to grayscale and then back to BGR to maintain 3 color channels
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            filtered_frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        elif active_filter == "Negative":
            filtered_frame = cv2.bitwise_not(frame)

        elif active_filter == "Canny":
            # Canny edge detector
            edges = cv2.Canny(frame, 100, 200)
            filtered_frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        elif active_filter == "Sepia":
            # Transformation matrix for the Sepia effect
            sepia_matrix = np.array([[0.272, 0.534, 0.131],
                                     [0.349, 0.686, 0.168],
                                     [0.393, 0.769, 0.189]])
            sepia = cv2.transform(frame, sepia_matrix)
            # Ensure pixel values do not exceed 255
            sepia = np.clip(sepia, 0, 255).astype(np.uint8)
            filtered_frame = sepia

        elif active_filter == "Color":
            # Convert the frame to the HSV color space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Get the current values from the sliders
            h_min = cv2.getTrackbarPos("H Min", controls_name)
            h_max = cv2.getTrackbarPos("H Max", controls_name)
            s_min = cv2.getTrackbarPos("S Min", controls_name)
            s_max = cv2.getTrackbarPos("S Max", controls_name)
            v_min = cv2.getTrackbarPos("V Min", controls_name)
            v_max = cv2.getTrackbarPos("V Max", controls_name)
            
            # Define the color range to be isolated
            lower_bound = np.array([h_min, s_min, v_min])
            upper_bound = np.array([h_max, s_max, v_max])
            
            # Create a mask with the pixels that are within the range
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
            
            # Apply the mask to the original frame
            filtered_frame = cv2.bitwise_and(frame, frame, mask=mask)


        # --- UI Drawing (Buttons) ---
        for name, (bx, by, bw, bh) in buttons.items():
            # Button color changes if it's active
            button_color = (0, 200, 0) if name == active_filter else (200, 100, 0)
            cv2.rectangle(filtered_frame, (bx, by), (bx + bw, by + bh), button_color, -1)
            cv2.putText(filtered_frame, name, (bx + 10, by + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)


        # Show the final frame with filters and UI
        cv2.imshow(window_name, filtered_frame)

        # Wait for a keypress. If it's 'q', exit the loop.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and destroy all windows
    cap.release()
    cv2.destroyAllWindows()

# Script entry point
if __name__ == "__main__":
    main()