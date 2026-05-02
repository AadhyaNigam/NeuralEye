import cv2
import mediapipe as mp
import requests
import time
from datetime import datetime

# --- CONFIG ---
FIREBASE_URL = "https://neuraleye-88ed2-default-rtdb.asia-southeast1.firebasedatabase.app/Accidents.json"

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

fall_detected = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:
        # Get coordinates for Nose (0) and Mid-Hip (23/24)
        nose = results.pose_landmarks.landmark[0]
        hip_y = (results.pose_landmarks.landmark[23].y + results.pose_landmarks.landmark[24].y) / 2
        
        # 1. THE MATH: Vertical-to-Horizontal Ratio
        # Normal standing: Nose is much higher than hip (Low Y value)
        # Falling: Nose Y value moves very close to Hip Y value
        vertical_dist = hip_y - nose.y

        # 2. TRIGGER: If the head drops below a certain threshold relative to hips
        if vertical_dist < 0.15 and not fall_detected:
            print("⚠️ EMERGENCY: FALL DETECTED!")
            fall_detected = True
            
            # 3. IoT CLOUD ALERT
            event = {"event": "FALL", "time": datetime.now().strftime("%H:%M:%S"), "status": "CRITICAL"}
            try: requests.post(FIREBASE_URL, json=event)
            except: pass

        elif vertical_dist > 0.4:
            fall_detected = False # Reset if person stands back up

    # Visual Feedback
    status_text = "STATUS: FALL DETECTED" if fall_detected else "STATUS: NORMAL"
    color = (0, 0, 255) if fall_detected else (0, 255, 0)
    cv2.putText(frame, status_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
    
    cv2.imshow("NeuralEye - Accident Monitor", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()