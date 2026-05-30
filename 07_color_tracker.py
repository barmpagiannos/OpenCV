import cv2
import numpy as np

# Initialize the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

print("Color Tracker App Started!")
print(" -> Show a BRIGHT RED object to the camera (like a bottle cap).")
print(" -> Press 'q' to QUIT the application.")

while True:
    # Capture the frame-by-frame feed from the camera
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab a frame.")
        break

    # Flip the frame horizontally (mirror effect) so moving left/right feels natural
    frame = cv2.flip(frame, 1)

    # --- STEP 1: COLOR SPACE CONVERSION ---
    # Convert the BGR image to HSV (Hue, Saturation, Value).
    # This makes it much easier to isolate a specific color regardless of lighting.
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # --- STEP 2: DEFINE THE RED COLOR RANGE ---
    # In OpenCV's HSV space, the Hue (color) goes from 0 to 179.
    # Red is tricky because it sits at the very beginning (0-10) AND the very end (170-179) of this scale.
    # Therefore, we need to create TWO boundaries and combine them.

    # Lower boundary of RED (Hue: 0 to 10)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    
    # Upper boundary of RED (Hue: 170 to 179)
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # --- STEP 3: CREATE THE MASK ---
    # cv2.inRange checks every pixel. If the pixel's color falls within our defined range,
    # it turns it WHITE (255). If it doesn't, it turns it BLACK (0).
    mask1 = cv2.inRange(hsv_frame, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv_frame, lower_red2, upper_red2)
    
    # Combine both masks to capture all shades of red
    full_red_mask = mask1 + mask2

    # --- STEP 4: CLEAN UP THE MASK (MORPHOLOGY) ---
    # The raw mask might have "noise" (tiny white dots in the background).
    # We use 'erode' to shrink/delete tiny dots, and 'dilate' to restore the size of our actual object.
    full_red_mask = cv2.erode(full_red_mask, None, iterations=2)
    full_red_mask = cv2.dilate(full_red_mask, None, iterations=2)

    # --- STEP 5: FIND CONTOURS (OUTLINES) ---
    # Now we ask OpenCV to find the outlines (contours) of all the white blobs in our mask.
    contours, _ = cv2.findContours(full_red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Check if we found at least one contour (meaning, a red object is on screen)
    if len(contours) > 0:
        # Find the LARGEST contour in the list (we assume the largest red blob is our target object)
        largest_contour = max(contours, key=cv2.contourArea)

        # Calculate the minimum enclosing circle around this largest contour
        ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)

        # Only draw the tracking circle if the object is large enough (filters out small distant red dots)
        if radius > 10:
            # Draw a thick YELLOW circle around the object
            # Arguments: (image, center_coordinates, radius, color_BGR, thickness)
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 3)
            
            # Draw a small RED dot exactly in the center of the target
            cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)
            
            # Optional: Add text tracking the coordinates of the object
            cv2.putText(frame, f"Tracking: {int(x)}, {int(y)}", (int(x) - 40, int(y) - int(radius) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # --- STEP 6: DISPLAY THE RESULTS ---
    # Show the main colored window with the tracking circle
    cv2.imshow("Color Tracker", frame)
    
    # (Bonus) Show what the computer's "brain" is seeing: The black & white mask!
    # This is incredibly helpful for debugging your lighting conditions.
    cv2.imshow("Computer Vision Mask", full_red_mask)

    # Listen for the 'q' key to quit the application
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("Exiting application...")
        break

# --- CLEANUP SECTION ---
cap.release()
cv2.destroyAllWindows()