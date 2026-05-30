import cv2

# Initialize the webcam (0 is the default built-in camera)
cap = cv2.VideoCapture(0)

# Check if the camera was opened successfully
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

print("Edge Detection App Started!")
print(" -> The camera is now showing outlines only (Canny algorithm).")
print(" -> Press 'q' to QUIT the application.")

while True:
    # Capture the frame-by-frame feed from the camera
    ret, frame = cap.read()

    # If we fail to grab a frame, break out of the loop
    if not ret:
        print("Error: Failed to grab a frame.")
        break

    # --- PRE-PROCESSING STEPS ---
    # Canny edge detection works best on Grayscale images and images with low noise.
    
    # 1. Convert the BGR (color) image to Grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 2. Apply a light Gaussian Blur to reduce high-frequency noise.
    # Noise is bad for edge detection because it creates false edges.
    # We use a small kernel size (5, 5) for subtle blurring.
    blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

    # --- THE CANNY ALGORITHM ---
    # This single line of code performs the full multi-stage Canny process.
    # Arguments: (source_image, low_threshold, high_threshold)
    # The thresholds control which edges get kept:
    #   - Gradient > High Threshold: Confirmed strong edge (Kept).
    #   - Gradient < Low Threshold: Noise (Discarded).
    #   - Gradient in-between: Discarded unless connected to a strong edge.
    # A standard 1:3 ratio is often used for thresholds (like 50:150).
    edges_frame = cv2.Canny(blurred_frame, 10, 50)

    # Note: Canny output is a binary image (just black and white).
    # Background is black (0 intensity), detected edges are pure white (255 intensity).

    # Display the final edge detection frame
    cv2.imshow("Canny Edge Detection", edges_frame)

    # Listen for the 'q' key to quit the application
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("Exiting application...")
        break

# --- CLEANUP SECTION ---
# Release the camera resource and close all opened windows
cap.release()
cv2.destroyAllWindows()