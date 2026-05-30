import cv2
import mediapipe as mp

# --- INITIALIZE MEDIAPIPE HANDS ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Configure the Hands AI model.
hands = mp_hands.Hands(
    max_num_hands=2,                 # UPGRADED: Now we track up to 2 hands!
    min_detection_confidence=0.7,    # Needs 70% confidence to detect a hand initially
    min_tracking_confidence=0.7      # Needs 70% confidence to keep tracking it
)

# --- FINGER TIP IDs ---
# According to MediaPipe's 21 hand landmarks mapping:
# 4: Thumb, 8: Index, 12: Middle, 16: Ring, 20: Pinky
tip_ids = [4, 8, 12, 16, 20]

# Initialize the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

print("Smart Finger Counter (Dual Hand) Started!")
print(" -> Show one or both hands to the camera to see the count (0-10).")
print(" -> Press 'q' to QUIT the application.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab a frame.")
        break

    # Flip the frame horizontally for a natural selfie-view
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to RGB for MediaPipe processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the image and find the hand landmarks
    results = hands.process(rgb_frame)

    # Initialize the master counter for the current frame
    total_fingers = 0

    # --- LOGIC: COUNTING FINGERS FOR ALL DETECTED HANDS ---
    # Check if the AI found any hands in the current frame
    if results.multi_hand_landmarks:
        
        # We use 'enumerate' to get both the index (idx) and the hand data (hand_landmarks)
        # This allows us to process hand #1 and then hand #2 sequentially.
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            
            # Determine if the CURRENT hand is a "Left" or "Right" hand.
            # Note: Because we flipped the frame, your real Right hand appears as a "Left" hand.
            hand_label = results.multi_handedness[idx].classification[0].label

            # Draw the hand skeleton on the video frame for this specific hand
            mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

            # Create an empty list to store the status of each finger for this specific hand
            fingers = []

            # 1. THUMB LOGIC
            # The thumb moves on the X-axis (horizontally).
            if hand_label == "Left":
                # For a Left hand (which is your real Right hand in the mirror), 
                # the thumb is open if the tip is further to the right (greater X) than the joint.
                if hand_landmarks.landmark[tip_ids[0]].x > hand_landmarks.landmark[tip_ids[0] - 1].x:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else: 
                # For a Right hand, the thumb is open if the tip is further to the left (smaller X).
                if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0] - 1].x:
                    fingers.append(1)
                else:
                    fingers.append(0)

            # 2. THE OTHER 4 FINGERS LOGIC
            # These move on the Y-axis (vertically).
            for id in range(1, 5):
                # A finger is "open" if its Tip's Y is SMALLER (higher up) than its middle joint's Y.
                if hand_landmarks.landmark[tip_ids[id]].y < hand_landmarks.landmark[tip_ids[id] - 2].y:
                    fingers.append(1) # Open
                else:
                    fingers.append(0) # Closed

            # Add this hand's open fingers to our master total!
            total_fingers += fingers.count(1)

        # --- DRAW UI FOR ACTIVE HANDS ---
        # Draw a beautiful green box and text to display the final combined count
        cv2.rectangle(frame, (20, 20), (200, 100), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, f"COUNT: {total_fingers}", (35, 75), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)

    else:
        # --- DRAW UI FOR NO HANDS ---
        # If no hand is detected at all, show "COUNT: 0" in a red box
        cv2.rectangle(frame, (20, 20), (200, 100), (0, 0, 255), cv2.FILLED)
        cv2.putText(frame, "COUNT: 0", (35, 75), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)

    # Display the final frame
    cv2.imshow("Smart Finger Counter", frame)

    # Listen for keyboard input (1ms delay)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting application...")
        break

# --- CLEANUP SECTION ---
hands.close()
cap.release()
cv2.destroyAllWindows()