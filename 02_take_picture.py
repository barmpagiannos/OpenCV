import cv2
import os  # Standard Python library to interact with the operating system/files

# Initialize the webcam (0 is the default built-in camera)
cap = cv2.VideoCapture(0)

# Check if the camera was opened successfully
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

print("Camera started successfully!")
print(" -> Press 's' to take a picture/snapshot.")
print(" -> Press 'q' to quit the application.")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to grab a frame.")
        break

    # Display the live stream in a window named "Snapshot Studio"
    cv2.imshow("Snapshot Studio", frame)

    # Listen for keyboard input (1ms delay)
    key = cv2.waitKey(1) & 0xFF

    # Check if the user pressed 's' (Snapshot)
    if key == ord('s'):
        counter = 1
        
        # This loop automatically finds the next available filename.
        # f"image{counter:02d}.jpg" formats the number to always have 2 digits (e.g., 01, 02, 10).
        # os.path.exists checks if a file with that name already lives in the folder.
        while os.path.exists(f"image{counter:02d}.jpg"):
            counter += 1  # If image01 exists, try image02, then image03, etc.
            
        # Define the final safe filename
        filename = f"image{counter:02d}.jpg"
        
        # cv2.imwrite saves the 'frame' (image array) to your hard drive as a file
        cv2.imwrite(filename, frame)
        print(f" Successfully saved snapshot as: {filename}")

    # Check if the user pressed 'q' (Quit)
    elif key == ord('q'):
        print("Exiting application...")
        break

# Clean up and release the camera resource
cap.release()
cv2.destroyAllWindows()
print("Camera closed cleanly.")