import cv2

# Initialize the webcam (0 is the default built-in camera)
cap = cv2.VideoCapture(0)

# Check if the camera was opened successfully
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

# --- LOAD FACE DETECTOR ---
# We load OpenCV's built-in Machine Learning model for face detection.
# 'haarcascade_frontalface_default.xml' is a pre-trained file that comes packaged with cv2.
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# State variables (Toggles) for our filters
# We start with everything False, meaning just normal Grayscale.
is_blurred = False
is_face_focus = False

print("Filter App Started!")
print(" -> The camera is running in Grayscale (Black & White).")
print(" -> Press 'b' to toggle FULL BLUR.")
print(" -> Press 'f' to toggle FACE FOCUS (Portrait Mode).")
print(" -> Press 'q' to QUIT the application.")

while True:
    # Capture the frame-by-frame feed from the camera
    ret, frame = cap.read()

    # If we fail to grab a frame, break out of the loop
    if not ret:
        print("Error: Failed to grab a frame.")
        break

    # --- BASE LAYER: GRAYSCALE ---
    # Convert the raw BGR color frame into a Grayscale image.
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # We create a copy of the grayscale frame. 
    # This 'display_frame' will be the canvas where we apply our effects.
    display_frame = gray_frame.copy()

    # --- FILTER LOGIC ---
    
    # 1. FACE FOCUS EFFECT (Portrait Mode)
    if is_face_focus:
        # Step A: Detect faces in the grayscale image.
        # scaleFactor=1.1 compensates for faces being closer/further from the camera.
        # minNeighbors=5 ensures we don't get false positives (random shadows detected as faces).
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)
        
        # Step B: Blur the ENTIRE background extremely heavily.
        # We use a large kernel (55, 55) so the background is unrecognizable.
        display_frame = cv2.GaussianBlur(gray_frame, (55, 55), 0)
        
        # Step C: Loop through every face detected (usually just 1)
        # x, y = top-left coordinates of the face. w = width, h = height.
        for (x, y, w, h) in faces:
            # MAGIC TRICK: We extract the sharp, unblurred pixels from the original 'gray_frame'
            # and paste them exactly over the blurred face in the 'display_frame'.
            display_frame[y:y+h, x:x+w] = gray_frame[y:y+h, x:x+w]
            
            # Optional: Draw a thin white rectangle around the face to show the detection boundary
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 255, 255), 1)
            
        # Add a text overlay indicating the effect is active
        cv2.putText(display_frame, "FACE FOCUS: ON", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # 2. FULL BLUR EFFECT
    elif is_blurred:
        # Apply a Gaussian Blur to the entire image.
        display_frame = cv2.GaussianBlur(gray_frame, (35, 35), 0)
        cv2.putText(display_frame, "FULL BLUR: ON", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    
    # 3. NO EFFECTS (Just Grayscale)
    else:
        cv2.putText(display_frame, "FILTERS: OFF", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Display the final processed frame
    cv2.imshow("Grayscale & Blur Filters", display_frame)

    # --- KEYBOARD CONTROLS ---
    key = cv2.waitKey(1) & 0xFF

    # If the user presses 'b', toggle Full Blur.
    # We automatically turn off Face Focus to avoid conflicts.
    if key == ord('b'):
        is_blurred = not is_blurred
        is_face_focus = False 
        print(f" [TOGGLE] Full Blur is now {'ON' if is_blurred else 'OFF'}")

    # If the user presses 'f', toggle Face Focus.
    # We automatically turn off Full Blur to avoid conflicts.
    elif key == ord('f'):
        is_face_focus = not is_face_focus
        is_blurred = False
        print(f" [TOGGLE] Face Focus is now {'ON' if is_face_focus else 'OFF'}")

    # If the user presses 'q', exit the infinite loop.
    elif key == ord('q'):
        print("Exiting application...")
        break

# --- CLEANUP SECTION ---
cap.release()
cv2.destroyAllWindows()