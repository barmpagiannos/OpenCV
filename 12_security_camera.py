import cv2
import time
import datetime
import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

# --- ΕΞΥΠΝΗ ΦΟΡΤΩΣΗ ΤΟΥ .env ΑΠΟ ΤΟΝ ΦΑΚΕΛΟ ΤΟΥ SCRIPT ---
script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path)

# --- ΕΞΥΠΝΗ ΣΥΝΑΡΤΗΣΗ ΑΠΟΣΤΟΛΗΣ EMAIL ---
def send_security_email(timestamp_str):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port_str = os.getenv("SMTP_PORT")

    # Safety check: Βεβαιωνόμαστε ότι διαβάστηκαν όλα
    if not all([sender_email, sender_password, receiver_email, smtp_server, smtp_port_str]):
        print(" [EMAIL WARNING] Λείπουν στοιχεία από το .env. Το email δεν στάλθηκε.")
        return

    try:
        # Μετατρέπουμε το Port από κείμενο σε αριθμό
        smtp_port = int(smtp_port_str)
        
        msg = EmailMessage()
        msg.set_content(f"Security Alert! Human detected on camera at {timestamp_str}.")
        msg['Subject'] = 'SECURITY ALERT - Motion Detected'
        msg['From'] = sender_email
        msg['To'] = receiver_email

        # Δυναμική σύνδεση ανάλογα με την πόρτα (465 = SSL, 587 = TLS)
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(" [EMAIL] Το Alert στάλθηκε με επιτυχία!")
    except Exception as e:
        print(f" [EMAIL ERROR] Αποτυχία αποστολής: {e}")

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

    # Convert to grayscale for the Haar Cascades
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces and bodies
    faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)
    bodies = body_cascade.detectMultiScale(gray_frame, 1.3, 5)

    # If we found AT LEAST ONE face or body
    if len(faces) > 0 or len(bodies) > 0:
        
        # If we are NOT already recording, start doing so!
        if not is_recording:
            is_recording = True
            
            # Generate a filename using the current date and time
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            filename = f"SECURITY_{current_time}.mp4"
            
            # Initialize the VideoWriter
            out = cv2.VideoWriter(filename, fourcc, 20.0, frame_size)
            print(f"\n[ALERT] Human Detected! Started recording: {filename}")
            
            # Trigger the smart email alert
            send_security_email(current_time)
            
        # Since we see the person, ensure the stopping timer is OFF
        timer_started = False
        
        # Optional: Draw rectangles around detected faces/bodies
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
    if is_recording:
        # Add a visual "REC" indicator to the screen
        cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1)
        cv2.putText(frame, "REC", (50, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
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