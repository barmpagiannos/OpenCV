import cv2
import mediapipe as mp
import numpy as np

# --- HELPER FUNCTION: CALCULATE ANGLE ---
def calculate_angle(a, b, c):
    """
    Calculates the angle between three points.
    a: First point (e.g., Shoulder)
    b: Middle point (e.g., Elbow) - The vertex of the angle
    c: End point (e.g., Wrist)
    """
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    # Calculate the angle in radians using arctan2, then convert to degrees
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    # Ensure the angle is always between 0 and 180 degrees
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

# --- INITIALIZE MEDIAPIPE POSE ---
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Configure the Pose AI model.
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# --- TRACKING VARIABLES FOR BOTH ARMS ---
# Left Arm State
counter_left = 0 
stage_left = None 

# Right Arm State
counter_right = 0
stage_right = None

# Initialize the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

print("AI Personal Trainer (Dual Arm) Started!")
print(" -> Stand back so the camera can see BOTH your arms.")
print(" -> Start doing bicep curls to see the counters go up!")
print(" -> Press 'q' to QUIT.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab a frame.")
        break

    # Get the width and height of the video frame (useful for UI placement)
    frame_height, frame_width, _ = frame.shape

    # Convert BGR to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the image and find body landmarks
    results = pose.process(rgb_frame)

    # --- LOGIC: POSE ESTIMATION & GYM TRACKER ---
    try:
        # Extract the list of all 33 body landmarks
        landmarks = results.pose_landmarks.landmark
        
        # ==================== LEFT ARM LOGIC ====================
        # Get coordinates for the LEFT arm.
        shoulder_l = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, 
                      landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        
        elbow_l = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, 
                   landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        
        wrist_l = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, 
                   landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        
        # Calculate the angle for the left arm
        angle_left = calculate_angle(shoulder_l, elbow_l, wrist_l)
        
        # Visualize the angle on the left elbow
        elbow_l_coords = tuple(np.multiply(elbow_l, [frame_width, frame_height]).astype(int))
        cv2.putText(frame, str(int(angle_left)), 
                    (elbow_l_coords[0] - 40, elbow_l_coords[1] + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Curl counter logic for Left Arm
        if angle_left > 160:
            stage_left = "down"
        if angle_left < 30 and stage_left == 'down':
            stage_left = "up"
            counter_left += 1
            print(f" [LEFT] Reps: {counter_left}")

        # ==================== RIGHT ARM LOGIC ====================
        # Get coordinates for the RIGHT arm.
        shoulder_r = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, 
                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        
        elbow_r = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, 
                   landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        
        wrist_r = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, 
                   landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        
        # Calculate the angle for the right arm
        angle_right = calculate_angle(shoulder_r, elbow_r, wrist_r)
        
        # Visualize the angle on the right elbow
        elbow_r_coords = tuple(np.multiply(elbow_r, [frame_width, frame_height]).astype(int))
        cv2.putText(frame, str(int(angle_right)), 
                    (elbow_r_coords[0] + 10, elbow_r_coords[1] + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Curl counter logic for Right Arm
        if angle_right > 160:
            stage_right = "down"
        if angle_right < 30 and stage_right == 'down':
            stage_right = "up"
            counter_right += 1
            print(f" [RIGHT] Reps: {counter_right}")
            
    except:
        # If landmarks are missing, silently pass
        pass

    # --- DRAW THE UI ---
    
    # 1. LEFT ARM UI BOX (Top Left Corner)
    cv2.rectangle(frame, (0,0), (250,90), (245, 117, 16), -1)
    cv2.putText(frame, 'L-REPS', (15, 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(frame, str(counter_left), (15, 75), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(frame, 'STAGE', (110, 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(frame, str(stage_left).upper(), (110, 75), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)

    # 2. RIGHT ARM UI BOX (Top Right Corner)
    # We subtract 250 from frame_width to align the box to the right edge
    start_x = frame_width - 250
    cv2.rectangle(frame, (start_x, 0), (frame_width, 90), (16, 117, 245), -1)
    cv2.putText(frame, 'R-REPS', (start_x + 15, 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(frame, str(counter_right), (start_x + 15, 75), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(frame, 'STAGE', (start_x + 110, 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(frame, str(stage_right).upper(), (start_x + 110, 75), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)
    
    # Render the actual body skeleton on the frame
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, 
            results.pose_landmarks, 
            mp_pose.POSE_CONNECTIONS,
            mp_drawing_styles.get_default_pose_landmarks_style()
        )

    # Show the final frame
    cv2.imshow('AI Personal Trainer - Dual Arm', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Workout finished! Exiting...")
        break

# --- CLEANUP SECTION ---
pose.close()
cap.release()
cv2.destroyAllWindows()