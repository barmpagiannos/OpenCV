import cv2
import time
import os

# --- TIMELAPSE CONFIGURATION ---
TOTAL_PHOTOS = 15          # How many photos to take in total
INTERVAL_SECONDS = 2      # How many seconds to wait between each photo
VIDEO_FPS = 5.0           # Frames Per Second for the final video (5 fps means our 5 photos will make a 1-second video)

# Initialize camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

# Variables to keep track of our progress
photos_taken = 0
captured_filenames = []   # List to store the names of our temporary images

# Record the exact time we start the process
last_capture_time = time.time()

print("Timelapse Maker Started!")
print(f"Goal: Take {TOTAL_PHOTOS} photos, 1 every {INTERVAL_SECONDS} seconds.")
print("Press 'q' at any time to abort.")

# --- STEP 1: CAPTURE THE PHOTOS ---
# We loop until we have taken all exactly 5 photos
while photos_taken < TOTAL_PHOTOS:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab a frame.")
        break

    # We make a copy of the frame to draw our UI text on it.
    # We do this so the text doesn't get saved into the actual photograph!
    display_frame = frame.copy()

    # Calculate how much time has passed since the last photo
    current_time = time.time()
    elapsed_time = current_time - last_capture_time
    time_left = INTERVAL_SECONDS - elapsed_time

    # Display progress (e.g., "Photos: 2/5")
    cv2.putText(display_frame, f"Photos: {photos_taken}/{TOTAL_PHOTOS}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the countdown timer
    # We use int(time_left) + 1 to show 3, 2, 1 instead of decimals
    cv2.putText(display_frame, f"Next in: {int(time_left) + 1}s", (20, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)

    # Check if it is time to take a picture!
    if time_left <= 0:
        # Create a temporary filename (e.g., temp_00.jpg, temp_01.jpg)
        filename = f"temp_photo_{photos_taken:02d}.jpg"
        
        # Save the pure, clean frame (NOT the display_frame with the text)
        cv2.imwrite(filename, frame)
        captured_filenames.append(filename)
        
        photos_taken += 1
        print(f" [SNAP] Took photo {photos_taken}/{TOTAL_PHOTOS}")
        
        # Reset the timer for the next photo
        last_capture_time = time.time()
        
        # Create a brief white "flash" effect on the screen to let the user know a photo was taken
        cv2.rectangle(display_frame, (0, 0), (display_frame.shape[1], display_frame.shape[0]), (255, 255, 255), -1)
        # Show the white flash frame immediately on screen
        cv2.imshow("Timelapse Capture", display_frame)
        # Pause for 100 milliseconds so the human eye can always capture the flash before it gets overwritten
        cv2.waitKey(100)

    # Show the live feed with the UI
    cv2.imshow("Timelapse Capture", display_frame)

    # Press 'q' to abort the process early
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Process aborted by user.")
        break

# Turn off the camera window as we don't need it anymore
cap.release()
cv2.destroyAllWindows()

# --- STEP 2: CREATE THE VIDEO ---
# We only create the video if we successfully captured photos
if len(captured_filenames) > 0:
    print("\nProcessing timelapse video...")
    
    # Read the very first image just to get the width and height needed for the VideoWriter
    first_image = cv2.imread(captured_filenames[0])
    height, width, _ = first_image.shape
    
    # Initialize the VideoWriter (saving as 'my_timelapse01.mp4', 'my_timelapse02.mp4', etc.)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    video_counter = 1
    # Loop until we find a filename that does NOT exist yet to prevent overwriting old timelapses
    while os.path.exists(f"my_timelapse{video_counter:02d}.mp4"):
        video_counter += 1
    video_filename = f"my_timelapse{video_counter:02d}.mp4"
    
    out = cv2.VideoWriter(video_filename, fourcc, VIDEO_FPS, (width, height))
    
    # Loop through our saved temporary images, write them to the video, and then delete them!
    for img_name in captured_filenames:
        # 1. Read the image from the hard drive
        img = cv2.imread(img_name)
        
        # 2. Add it as a frame in our video
        out.write(img)
        
        # 3. Delete the temporary image file to keep our folder clean (Housekeeping)
        os.remove(img_name)
        
    # Finalize the video file
    out.release()
    print(f" SUCCESS! '{video_filename}' has been created and saved.")
else:
    print("No photos were taken. Video creation skipped.")