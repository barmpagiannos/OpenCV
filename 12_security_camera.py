import cv2
import time
import datetime
import smtplib
from email.message import EmailMessage

# --- OPTIONAL: EMAIL ALERT FUNCTION ---
# To make this work, you need to use an "App Password" from your Google/Yahoo account.
# Regular passwords won't work due to modern security protocols.
def send_security_email(timestamp_str):
    try:
        sender_email = "YOUR_EMAIL@gmail.com"
        sender_password = "YOUR_APP_PASSWORD" 
        receiver_email = "YOUR_EMAIL@gmail.com"

        msg = EmailMessage()
        msg.set_content(f"Security Alert! Human detected on camera at {timestamp_str}.")
        msg['Subject'] = 'SECURITY ALERT - Motion Detected'
        msg['From'] = sender_email
        msg['To'] = receiver_email

        # Connect to Gmail's server (port 465 for SSL)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(" [EMAIL] Alert sent successfully!")
    except Exception as e:
        print(f" [EMAIL ERROR] Could not send email: {e}")

# --- INITIALIZE CAMERA & AI MODELS ---
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

# Load the Haar Cascade models for Face and Full Body detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')

# --- VIDEO WRITER SETUP ---
# Get camera resolution
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_size = (frame_width, frame_height)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# --- SECURITY STATE VARIABLES ---
is_recording = False
timer_started = False
out = None

# How many seconds to keep recording AFTER the person leaves the frame
SECONDS_TO_RECORD_AFTER_EXIT = 5 
stop_recording_time = 0

print("Smart Security Camera Started!")
print(" -> Monitoring for humans (Faces/Bodies)...")
print(" -> Press 'q' to QUIT.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab a frame.")
        break

    # Convert to grayscale for the Haar Cascades (it processes much faster)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces and bodies
    # scaleFactor=1.3, minNeighbors=5 helps reduce false positives
    faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)
    bodies = body_cascade.detectMultiScale(gray_frame, 1.3, 5)

    # If we found AT LEAST ONE face or body
    if len(faces) > 0 or len(bodies) > 0:
        
        # If we are NOT already recording, start doing so!
        if not is_recording:
            is_recording = True
            
            # Generate a filename using the current date and time
            # Format: DD-MM-YYYY-HH-MM-SS
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            filename = f"SECURITY_{current_time}.mp4"
            
            # Initialize the VideoWriter
            out = cv2.VideoWriter(filename, fourcc, 20.0, frame_size)
            print(f"\n[ALERT] Human Detected! Started recording: {filename}")
            
            # UNCOMMENT the line below if you want to test the email feature
            # send_security_email(current_time)
            
        # Since we see the person, ensure the stopping timer is OFF
        timer_started = False
        
        # Optional: Draw rectangles around detected faces/bodies for visual feedback
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

    # If NO human is detected, but we are currently recording...
    elif is_recording:
        # Start the countdown timer to stop recording
        if not timer_started:
            timer_started = True
            stop_recording_time = time.time() + SECONDS_TO_RECORD_AFTER_EXIT
            print(f" [*] Target lost. Stopping record in {SECONDS_TO_RECORD_AFTER_EXIT} seconds...")
            
        # If the countdown has finished
        elif time.time() >= stop_recording_time:
            is_recording = False
            timer_started = False
            out.release()
            out = None
            print(" [OK] Recording saved and stopped. Back to monitoring.")

    # --- RECORD & DISPLAY ---
    # If we are in recording mode, write the frame to the file
    if is_recording:
        # Add a visual "REC" indicator to the screen
        cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1)
        cv2.putText(frame, "REC", (50, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Write the frame (with the REC dot) to the video file
        if out is not None:
            out.write(frame)

    cv2.imshow("Smart Security Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Security System deactivated.")
        break

# --- CLEANUP SECTION ---
if out is not None:
    out.release()
cap.release()
cv2.destroyAllWindows()