import cv2

# Initialize the video capture object.
# The argument '0' refers to the default camera (usually the built-in laptop webcam).
# If you have multiple cameras (like a USB camera), you can try changing this to 1, 2, etc.
cap = cv2.VideoCapture(0)

# Verify that the camera initialized successfully.
# Sometimes another program might be using the camera, causing this to fail.
if not cap.isOpened():
    print("Error: Could not open the camera. Check if another app is using it.")
    exit()

print("Camera started successfully!")
print("Press the 'q' key on your keyboard to exit the video stream.")

# Start an infinite loop. 
# A video is just a rapid sequence of images (frames). This loop captures them one by one.
while True:
    # Read a single frame from the camera.
    # 'ret' (return) is a boolean (True/False) that tells us if the read was successful.
    # 'frame' contains the actual image data (a multi-dimensional NumPy array of pixels).
    ret, frame = cap.read()

    # If 'ret' is False, something went wrong (e.g., camera disconnected). We must stop.
    if not ret:
        print("Error: Failed to grab a frame from the camera.")
        break

    # Display the captured frame in a graphical window on the screen.
    # The first argument "My Camera" is the title of the window.
    cv2.imshow("My Camera", frame)

    # Wait for 1 millisecond to see if the user presses a key.
    # Without this waitKey, the window would freeze and not display the image.
    # The bitwise AND operation '& 0xFF' ensures compatibility across 32/64-bit systems.
    key = cv2.waitKey(1) & 0xFF

    # Check if the pressed key is 'q' (ord('q') gets the ASCII value of 'q').
    # If it is, break out of the infinite loop.
    if key == ord('q'):
        print("Closing the camera...")
        break

# --- CLEANUP SECTION ---
# This part is crucial. If you don't release the camera, it might stay "on" 
# (with the green light on) even after the script finishes, and other apps won't be able to use it.

# Release the hardware resource (turn off the camera).
cap.release()

# Destroy/close all graphical windows opened by OpenCV.
cv2.destroyAllWindows()