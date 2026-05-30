# Computer Vision & AI Mini-Projects

A complete collection of 14 Python scripts exploring Computer Vision, Image Processing, and Artificial Intelligence using **OpenCV**, **MediaPipe**, and **Face Recognition**. The projects scale from basic camera operations to advanced, real-world AI applications.

---

## Important Note on Execution (Python Versions)
Due to specific library dependencies (like MediaPipe, dlib, and PyAutoGUI), some scripts require a specific Python version (3.11) to run stably on Windows. 
* Scripts in **Phase 1 & 2** and **Project 12** can be executed using the standard Python command: `py <script_name.py>`
* Scripts using AI Models (**Phase 3** and **Projects 13 & 14**) **must** be executed with Python 3.11 explicitly: `py -3.11 <script_name.py>`

## Quick Setup (Install Everything)
If you want to install all required libraries at once, open your terminal and run these two commands:
```powershell
py -m pip install opencv-python numpy
py -3.11 -m pip install opencv-python numpy mediapipe==0.10.11 pyautogui cmake face_recognition
```
*(Note: Installing `face_recognition` on Windows requires Visual Studio C++ Build Tools installed on your system).*

---

## Phase 1: Camera Basics
*Fundamental OpenCV operations for camera and video manipulation.*

* **`01_open_camera.py`** - The "Hello World" of OpenCV. Opens the webcam, displays the live video feed, and closes gracefully when 'q' is pressed. 
  * *Run:* `py 01_open_camera.py`
  * *Install:* `py -m pip install opencv-python`

* **`02_take_picture.py`** - A simple camera app. Pressing 's' captures the current frame and saves it locally as `photo.jpg`. 
  * *Run:* `py 02_take_picture.py`
  * *Install:* `py -m pip install opencv-python`

* **`03_record_video.py`** - Acts as a camcorder. It records the live feed and compiles it into a `video.avi` file upon exiting. 
  * *Run:* `py 03_record_video.py`
  * *Install:* `py -m pip install opencv-python`

* **`04_timelapse_maker.py`** - Automatically captures a photo every 5 seconds and stitches them together into a fast-motion timelapse video. 
  * *Run:* `py 04_timelapse_maker.py`
  * *Install:* `py -m pip install opencv-python`

## Phase 2: Image Processing (Filters & Math)
*Applying mathematical transformations to pixels without AI.*

* **`05_grayscale_and_blur.py`** - Displays the video feed in grayscale and toggles a blur effect on/off with a keypress. 
  * *Run:* `py 05_grayscale_and_blur.py`
  * *Install:* `py -m pip install opencv-python`

* **`06_edge_detection.py`** - Uses the Canny Edge Detection algorithm to isolate and display only the outlines of objects, creating a live pencil-sketch effect. 
  * *Run:* `py 06_edge_detection.py`
  * *Install:* `py -m pip install opencv-python`

* **`07_color_tracker.py`** - Isolates a specific color (e.g., a red object), draws a bounding circle around it, and tracks its movement across the screen. 
  * *Run:* `py 07_color_tracker.py`
  * *Install:* `py -m pip install opencv-python numpy`

* **`08_invisible_cloak.py`** - The classic "Harry Potter Cloak". It tracks a specific color (like a green sheet) and replaces it dynamically with a pre-captured background, rendering the object/person invisible! 
  * *Run:* `py 08_invisible_cloak.py`
  * *Install:* `py -m pip install opencv-python numpy`

## Phase 3: Anatomy & MediaPipe AI
*Advanced neural network models for real-time body tracking.*

* **`09_face_mesh_art.py`** - Maps 468 facial landmarks in real-time to draw a futuristic 3D mesh mask over the user's face. 
  * *Run:* `py -3.11 09_face_mesh_art.py`
  * *Install:* `py -3.11 -m pip install opencv-python numpy mediapipe==0.10.11`

* **`10_finger_counter.py`** - Scans both hands, calculates joint angles, and prints the total number of raised fingers (0 to 10) on a graphical UI. 
  * *Run:* `py -3.11 10_finger_counter.py`
  * *Install:* `py -3.11 -m pip install opencv-python mediapipe==0.10.11`

* **`11_pose_estimation.py`** - An AI Personal Trainer. Tracks full-body pose, calculates the real-time angles of both elbows, and independently counts bicep curl repetitions for the left and right arm. 
  * *Run:* `py -3.11 11_pose_estimation.py`
  * *Install:* `py -3.11 -m pip install opencv-python numpy mediapipe==0.10.11`

## Phase 4: Smart Applications (The "Bosses")
*Combining everything into complex, real-world software.*

* **`12_security_camera.py`** - A smart CCTV system. It actively monitors the feed but only starts recording when a **Human (Face/Body)** is detected using Haar Cascades. Saves the footage with a timestamp and includes an optional Email Alert feature. 
  * *Run:* `py 12_security_camera.py`
  * *Install:* `py -m pip install opencv-python`

* **`13_virtual_mouse.py`** - Sci-Fi computer control. Moves the physical computer mouse cursor by tracking the index finger in the air. Pinching the index and thumb together triggers a Left Click. 
  * *Run:* `py -3.11 13_virtual_mouse.py`
  * *Install:* `py -3.11 -m pip install opencv-python numpy mediapipe==0.10.11 pyautogui`

* **`14_attendance_system.py`** - A corporate-level Facial Recognition system. It reads known faces from an `Images` folder, identifies them on camera, and logs their name and exact timestamp into an `Attendance.txt` file, featuring a 5-minute cooldown timer to prevent spam logging. 
  * *Run:* `py -3.11 14_attendance_system.py`
  * *Install:* `py -3.11 -m pip install opencv-python numpy cmake face_recognition`