import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# --- CONFIGURATION ---
# Disable PyAutoGUI's failsafe so the program doesn't crash if you move the mouse to a corner
pyautogui.FAILSAFE = False

# Variables for the Smoothing effect
smoothening = 5
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0

# Variables for the Click logic
is_clicked = False
click_threshold = 30 # Distance in pixels between index and thumb to trigger a click

# Camera dimensions and Interaction Box size
cam_w, cam_h = 640, 480
frame_reduction = 100 # Margin from the camera edges

# Get the actual resolution of your computer screen (e.g., 1920x1080)
screen_w, screen_h = pyautogui.size()

# --- INITIALIZE MEDIAPIPE HANDS ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,                 # We only need 1 hand to control the mouse
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Initialize the webcam
cap = cv2.VideoCapture(0)
cap.set(3, cam_w)
cap.set(4, cam_h)

if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

print("Virtual Mouse Started!")
print(" -> Move your INDEX finger to move the cursor.")
print(" -> PINCH your index and thumb together to CLICK.")
print(" -> Press 'q' on your physical keyboard to QUIT.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab a frame.")
        break

    # Flip the frame for a natural mirror effect
    frame = cv2.flip(frame, 1)
    
    # Draw the Interaction Box on the screen (visual guide)
    # Your finger needs to move inside this pink box to cover the entire computer monitor
    cv2.rectangle(frame, (frame_reduction, frame_reduction), 
                 (cam_w - frame_reduction, cam_h - frame_reduction), (255, 0, 255), 2)

    # Convert to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            
            # Draw hand skeleton (optional, can be commented out for a cleaner look)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Extract the coordinates for the Index tip (8) and Thumb tip (4)
            # We multiply by the camera dimensions to get the exact pixel location
            x_index = int(hand_landmarks.landmark[8].x * cam_w)
            y_index = int(hand_landmarks.landmark[8].y * cam_h)
            
            x_thumb = int(hand_landmarks.landmark[4].x * cam_w)
            y_thumb = int(hand_landmarks.landmark[4].y * cam_h)

            # --- 1. MOUSE MOVEMENT LOGIC ---
            # Check if the index finger is inside our Interaction Box
            # We map the coordinates from the small camera box to your massive monitor resolution
            # np.interp() translates a value from one scale to another
            screen_x = np.interp(x_index, (frame_reduction, cam_w - frame_reduction), (0, screen_w))
            screen_y = np.interp(y_index, (frame_reduction, cam_h - frame_reduction), (0, screen_h))

            # Apply the Smoothing formula to prevent jittering
            curr_x = prev_x + (screen_x - prev_x) / smoothening
            curr_y = prev_y + (screen_y - prev_y) / smoothening

            # Move the actual computer mouse!
            pyautogui.moveTo(curr_x, curr_y)

            # Update previous coordinates for the next frame
            prev_x, prev_y = curr_x, curr_y

            # Draw a circle on the index finger so you know it's tracking
            cv2.circle(frame, (x_index, y_index), 10, (255, 0, 0), cv2.FILLED)

            # --- 2. MOUSE CLICK LOGIC ---
            # Calculate the distance between the Index tip and Thumb tip
            # np.hypot uses the Pythagorean theorem to find the exact distance
            distance = np.hypot(x_index - x_thumb, y_index - y_thumb)

            if distance < click_threshold:
                # If they are close enough, draw a green circle between them
                cx, cy = (x_index + x_thumb) // 2, (y_index + y_thumb) // 2
                cv2.circle(frame, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
                
                # Check the state flag so we don't click 30 times per second
                if not is_clicked:
                    pyautogui.click()
                    is_clicked = True
            else:
                # If fingers are spread apart, reset the click state
                is_clicked = False

    # Display the final frame
    cv2.imshow("Virtual Mouse Controller", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Virtual Mouse deactivated.")
        break

# --- CLEANUP ---
cap.release()
cv2.destroyAllWindows()