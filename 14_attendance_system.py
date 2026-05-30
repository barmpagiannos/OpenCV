import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import time # Required for the cooldown timer logic

# --- CONFIGURATION ---
# The folder where we keep the photos of the people we want to recognize
path = 'Images'
images = []
classNames = []

# NEW: A dictionary to remember the exact time (in seconds) each person was last logged.
# Format: {'VASILIS': 1684500000.0}
last_logged_time = {}

# NEW: How many seconds must pass before logging the same person again? (300 sec = 5 mins)
COOLDOWN_SECONDS = 300 

# Check if the database folder exists. If not, create it automatically.
if not os.path.exists(path):
    os.makedirs(path)
    print(f"Created folder '{path}'. Please put some .jpg photos inside and run again!")
    exit()

# --- STEP 1: READ THE "DATABASE" (FOLDER) ---
myList = os.listdir(path)
print(f"Loading images from database: {myList}")

for cl in myList:
    # Read each image from the folder
    curImg = cv2.imread(f'{path}/{cl}')
    if curImg is not None:
        images.append(curImg)
        # Extract the name without the file extension (e.g., "Vasilis.jpg" -> "Vasilis")
        classNames.append(os.path.splitext(cl)[0])
    
print(f"Recognized Names: {classNames}")

# --- STEP 2: EXTRACT ENCODINGS ---
def findEncodings(images_list):
    encodeList = []
    for img in images_list:
        # Convert BGR (OpenCV format) to RGB (face_recognition format)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Extract the 128 unique facial measurements (encodings)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding faces... This might take a few seconds...")
encodeListKnown = findEncodings(images)
print("Encoding Complete! Starting Camera...")

# --- STEP 3: SMART ATTENDANCE LOGGING FUNCTION ---
def markAttendance(name):
    # Get the current time in seconds since the Epoch
    current_time = time.time()
    
    # 1. COOLDOWN CHECK: Have we seen this person recently?
    if name in last_logged_time:
        # Calculate how many seconds have passed since they were last seen
        time_passed = current_time - last_logged_time[name]
        if time_passed < COOLDOWN_SECONDS:
            # If 5 minutes haven't passed, exit the function silently (do nothing)
            return
            
    # 2. FILE WRITING WITH CRASH PROTECTION
    now = datetime.now()
    # Format the current date and time: DD/MM/YYYY HH:MM:SS
    dtString = now.strftime('%d/%m/%Y %H:%M:%S') 
    
    try:
        # Try to open the file in append mode ('a+'). 
        # We MUST use encoding='utf-8' to safely write Greek characters without crashing.
        with open('Attendance.txt', 'a+', encoding='utf-8') as f:
            f.writelines(f'Εντοπίστηκε {name} {dtString}\n')
            
        # If the writing was successful, update the timer for this specific person
        last_logged_time[name] = current_time
        print(f" [LOG] Successfully logged: {name} at {dtString}")
        
    except PermissionError:
        # If the file is locked/open in another program (like Excel or Notepad),
        # catch the error gracefully instead of crashing the camera feed!
        print(f" [WARNING] Cannot write to file! Is Attendance.txt currently open?")

# --- STEP 4: LIVE RECOGNITION (WEBCAM) ---
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        print("Error: Failed to grab a frame.")
        break
        
    # Resize the live frame to 1/4 size to speed up the recognition process significantly
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    
    # 1. Find all face locations in the current live frame
    facesCurFrame = face_recognition.face_locations(imgS)
    
    # 2. Extract the encodings for all faces found in the frame
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    
    # Loop through all detected faces simultaneously (using zip)
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        # Compare the live face with our known database
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        # Calculate the mathematical distance (lower distance = better match)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        
        # Find the best match index (the one with the lowest distance)
        matchIndex = np.argmin(faceDis)
        
        # If it's a confirmed match
        if matches[matchIndex]:
            # Get the person's name and convert it to uppercase
            name = classNames[matchIndex].upper()
            
            # --- DRAW THE UI ---
            # Scale the coordinates back up by 4 (since we reduced the frame to 0.25 earlier)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            
            # Draw a green bounding box around the face
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # Draw a filled box for the text background
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            # Display the recognized name
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            
            # Call our smart logging function
            markAttendance(name)

    # Show the final frame
    cv2.imshow('Smart Attendance System', img)
    
    # Listen for the 'q' key to quit the application
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Closing System...")
        break

# --- CLEANUP ---
cap.release()
cv2.destroyAllWindows()