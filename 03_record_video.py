import cv2
import os

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

# Video configuration
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 20.0
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# State variables
is_recording = False # Checks if we are currently recording. Initially, we are not.
out = None # VideoWriter's object.
current_filename = "" # Saves the name of the current video file being recorded.

print("Camera started successfully!")
print(" -> Press 'r' to START/STOP recording.")
print(" -> Press 'q' to QUIT (Note: Quitting while recording discards the video!).")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab a frame.")
        break

    # We take the height and width of the frame to know where to place our recording indicator (REC) on the screen.
    img_h, img_w, _ = frame.shape

    # --- LOGIC & VISUALS ---
    if is_recording:
        # On recording: color is RED (BGR format: Blue=0, Green=0, Red=255)
        color = (0, 0, 255)
        
        # We save the frame to the video file only if we are currently recording.
        # If not, we are in standby mode and we don't save.
        # Must be done before drawing the "REC" sign, otherwise it would be recorded into the video!
        if out is not None:
            out.write(frame)
    else:
        # If not recording (standby): color is GRAY (BGR format: 150, 150, 150)
        color = (150, 150, 150)

    # --- PLACE ON TOP RIGHT ---
    # We subtract pixels from the total width (img_w) to move it to the right.
    circle_x = img_w - 90
    text_x = img_w - 70

    # Draw the label on the frame that the user sees.
    cv2.circle(frame, (circle_x, 30), 10, color, -1)
    cv2.putText(frame, "REC", (text_x, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    # Image appears.
    cv2.imshow("Smart Camera App", frame)

    # --- KEYBOARD CONTROL ---
    key = cv2.waitKey(1) & 0xFF

    if key == ord('r'):
        if not is_recording:
            # --- START RECORDING ---
            counter = 1
            # We find the next available filename (e.g., video01.mp4, video02.mp4) to avoid overwriting existing videos.
            while os.path.exists(f"video{counter:02d}.mp4"):
                counter += 1
            
            current_filename = f"video{counter:02d}.mp4"
            # We open the file for writing.
            out = cv2.VideoWriter(current_filename, fourcc, fps, (frame_width, frame_height))
            is_recording = True
            print(f" [REC] Started recording: {current_filename}")
            
        else:
            # --- STOP RECORDING ---
            is_recording = False
            out.release()  # Close/save the file.
            out = None
            print(f" [OK] Recording saved successfully as '{current_filename}'!")

    elif key == ord('q'):
        # --- QUIT LOGIC ---
        if is_recording:
            print(" [!] Quit requested while recording! Discarding video...")
            is_recording = False
            out.release() # Need to free up in order to delete it.
            
            # Delete the incomplete video file if it exists, to avoid confusion and save disk space.
            if os.path.exists(current_filename):
                os.remove(current_filename)
                print(f" [!] Deleted incomplete file: {current_filename}")
        else:
            print("Exiting application cleanly...")
            
        break # Break the infinite loop and close the program.
    
# Cleanup
cap.release()
if out is not None:
    out.release() # In case of error.
cv2.destroyAllWindows()