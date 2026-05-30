import cv2
import mediapipe as mp
import numpy as np

# --- INITIALIZE MEDIAPIPE FACE MESH ---
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Configure the FaceMesh AI model.
# refine_landmarks=True adds 10 extra points specifically for the irises (eyes).
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=2,                # How many faces to track at the same time
    refine_landmarks=True,          # Get extra precision around the eyes
    min_detection_confidence=0.5,   # Minimum confidence to detect a face (0.0 to 1.0)
    min_tracking_confidence=0.5     # Minimum confidence to keep tracking it
)

# Initialize the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

# State variable to toggle the black background ("Hologram Mode")
show_black_background = False

print("Face Mesh Art App Started!")
print(" -> You should see a futuristic 3D mask mapped onto your face.")
print(" -> Press 'b' to toggle HOLOGRAM MODE (Black background).")
print(" -> Press 'q' to QUIT the application.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab a frame.")
        break

    # Flip the frame horizontally for a natural selfie-view display
    frame = cv2.flip(frame, 1)

    # --- STEP 1: PREPARE THE IMAGE FOR THE AI ---
    # MediaPipe requires RGB images, but OpenCV captures in BGR.
    # We must convert the color space before feeding it to the model.
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Optional: Improve performance by marking the image as not writeable
    # This saves memory during the AI processing phase.
    rgb_frame.flags.writeable = False
    
    # Process the image and find the face landmarks!
    results = face_mesh.process(rgb_frame)
    
    # --- STEP 2: PREPARE THE CANVAS ---
    # If the user wants Hologram Mode, we create a pure black canvas.
    # Otherwise, we use the real video frame as our canvas.
    if show_black_background:
        # np.zeros creates a completely black image with the exact same dimensions as our frame
        canvas = np.zeros(frame.shape, dtype=np.uint8)
    else:
        canvas = frame

    # --- STEP 3: DRAW THE 3D MASK ---
    # Check if the AI actually found any faces in the current frame
    if results.multi_face_landmarks:
        # Loop through every face detected (up to the max_num_faces we set earlier)
        for face_landmarks in results.multi_face_landmarks:
            
            # 1. Draw the Tessellation (The spider-web connecting the 468 points)
            # We use a built-in style that makes it look like a futuristic mesh.
            mp_drawing.draw_landmarks(
                image=canvas,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
            )
            
            # 2. Draw the Contours (The thick outlines of the eyes, lips, and eyebrows)
            # This uses a different style to make the facial features pop out.
            mp_drawing.draw_landmarks(
                image=canvas,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
            )
            
            # 3. Draw the Irises (The center of the eyes)
            # This only works because we set refine_landmarks=True!
            mp_drawing.draw_landmarks(
                image=canvas,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_IRISES,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_iris_connections_style()
            )

    # --- STEP 4: UI & CONTROLS ---
    # Add a small text overlay to show the current mode
    mode_text = "MODE: HOLOGRAM" if show_black_background else "MODE: REALITY"
    cv2.putText(canvas, mode_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Display the final piece of art
    cv2.imshow("MediaPipe Face Mesh Art", canvas)

    # Keyboard interactions
    key = cv2.waitKey(1) & 0xFF
    if key == ord('b'):
        # Toggle the boolean variable
        show_black_background = not show_black_background
    elif key == ord('q'):
        print("Exiting application...")
        break

# --- CLEANUP SECTION ---
# Properly close the MediaPipe model and OpenCV windows
face_mesh.close()
cap.release()
cv2.destroyAllWindows()