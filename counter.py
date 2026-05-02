import cv2
import json
import os
import requests
from datetime import datetime

# --- SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
TRAINER_FILE = os.path.join(BASE_DIR, "trainer", "trainer.yml")
LOG_FILE = os.path.join(BASE_DIR, "visitor_log.json")
FIREBASE_URL = "https://neuraleye-88ed2-default-rtdb.asia-southeast1.firebasedatabase.app/LiveAnalytics.json"

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(TRAINER_FILE)

with open(USERS_FILE, "r") as f:
    users_data = json.load(f)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
cap = cv2.VideoCapture(0)

# --- TRACKING VARIABLES ---
LINE_Y = 240  # Set exactly to the middle of a standard 480p camera
BUFFER = 30   # Creates a 60-pixel "dead zone" to prevent flickering counts
user_states = {} 
total_entries = 0
total_exits = 0

def log_event(name, direction):
    event = {"name": name, "action": direction, "time": datetime.now().strftime("%H:%M:%S")}
    try:
        logs = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f: logs = json.load(f)
        logs.append(event)
        with open(LOG_FILE, "w") as f: json.dump(logs, f, indent=4)
        requests.post(FIREBASE_URL, json=event)
        print(f"✅ Logged: {name} {direction}")
    except Exception as e:
        print(f"⚠️ Event logging failed: {e}")

while True:
    ret, img = cap.read()
    if not ret: break
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    # Draw the Trigger Line and Buffer Zones
    cv2.line(img, (0, LINE_Y), (640, LINE_Y), (0, 255, 255), 2)
    cv2.line(img, (0, LINE_Y - BUFFER), (640, LINE_Y - BUFFER), (50, 50, 50), 1)
    cv2.line(img, (0, LINE_Y + BUFFER), (640, LINE_Y + BUFFER), (50, 50, 50), 1)

    for (x, y, w, h) in faces:
        id_num, conf = recognizer.predict(gray[y:y+h, x:x+w])
        center_y = y + (h // 2)

        # Identify User
        if conf < 75:
            name = users_data.get(str(id_num), "Unknown")
            person_key = str(id_num)
        else:
            name = "Unknown"
            person_key = "unknown_temp"

        # --- BULLETPROOF CROSSING LOGIC ---
        prev_state = user_states.get(person_key)

        # Moving Down (Entering)
        if center_y > (LINE_Y + BUFFER) and prev_state == "above":
            log_event(name, "Entered")
            total_entries += 1
            user_states[person_key] = "below"
            
        # Moving Up (Exiting)
        elif center_y < (LINE_Y - BUFFER) and prev_state == "below":
            log_event(name, "Exited")
            total_exits += 1
            user_states[person_key] = "above"
        
        # Initial State Capture
        elif prev_state is None:
            if center_y < LINE_Y: user_states[person_key] = "above"
            elif center_y > LINE_Y: user_states[person_key] = "below"

        # UI Visuals
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.circle(img, (x + w//2, center_y), 5, (255,0,0), -1) # Draw the centroid dot
        cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
        cv2.putText(img, f"{name} ({prev_state})", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Dashboard Overlay
    cv2.putText(img, f"IN: {total_entries} | OUT: {total_exits}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    cv2.imshow("NeuralEye - Analytical Counter", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()