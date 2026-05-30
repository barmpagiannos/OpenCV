import cv2
import numpy as np
import time

# Initialize the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

print("Invisible Cloak App Started!")
print(" -> STEP 1: Please step OUT of the camera frame.")
print(" -> Capturing the empty background in 3 seconds...")

# --- STEP 1: CAPTURE THE BACKGROUND ---
# We give the camera a few seconds to warm up and adjust its white balance and exposure.
time.sleep(3)

# Read the background frame. 
# We read it multiple times in a quick loop to ensure the camera has fully adjusted to the light.
background = 0
for i in range(60):
    ret, background = cap.read()

# Flip the background horizontally (mirror effect) so it matches our mirrored live feed later
background = cv2.flip(background, 1)

print(" -> Background captured successfully!")
print(" -> STEP 2: Step back into the frame with your GREEN cloak!")
print(" -> Press 'q' to QUIT the application.")

# --- STEP 2: THE MAIN LOOP ---
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab a frame.")
        break

    # Flip the live frame to match the background
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to HSV (Hue, Saturation, Value) for accurate color detection
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # --- STEP 3: DEFINE THE CLOAK COLOR (GREEN) ---
    # In OpenCV, Green Hue is generally between 35 and 85.
    # If your cloak is BLUE, try: lower = [90, 50, 50], upper = [130, 255, 255]
    # If your cloak is RED, you need two masks (like we did in the Color Tracker project).
    lower_green = np.array([35, 100, 100])
    upper_green = np.array([85, 255, 255])

    # Create a binary mask where the green cloak is white (255) and everything else is black (0)
    mask1 = cv2.inRange(hsv_frame, lower_green, upper_green)

    # --- STEP 4: REFINE THE MASK (MORPHOLOGY) ---
    # "MORPH_OPEN" removes small digital noise (tiny white dots in the black background).
    mask1 = cv2.morphologyEx(mask1, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=2)
    # "MORPH_DILATE" expands the white areas slightly to ensure we cover the edges of the cloak completely.
    mask1 = cv2.morphologyEx(mask1, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8), iterations=1)

    # --- STEP 5: CREATE THE INVERTED MASK ---
    # mask2 is the exact opposite of mask1.
    # Where the cloak is, mask2 is BLACK. Where your body/room is, mask2 is WHITE.
    mask2 = cv2.bitwise_not(mask1)

    # --- STEP 6: SEGMENTATION & REPLACEMENT ---
    # Part 1: Extract ONLY the foreground (you and the room, but NOT the cloak).
    # bitwise_and keeps the pixels of the 'frame' only where 'mask2' is white.
    res1 = cv2.bitwise_and(frame, frame, mask=mask2)

    # Part 2: Extract ONLY the background pixels corresponding to where the cloak is.
    # bitwise_and keeps the pixels of the saved 'background' only where 'mask1' (the cloak) is white.
    res2 = cv2.bitwise_and(background, background, mask=mask1)

    # Part 3: Combine both parts together! 
    # cv2.add simply adds the pixel values. Since the black areas in res1 are filled 
    # by the colored areas in res2, it creates a seamless final image.
    final_output = cv2.add(res1, res2)

    # --- STEP 7: DISPLAY THE RESULT ---
    cv2.imshow("Harry Potter's Invisible Cloak", final_output)

    # Listen for the 'q' key to quit the application
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("Exiting application...")
        break

# --- CLEANUP SECTION ---
cap.release()
cv2.destroyAllWindows()