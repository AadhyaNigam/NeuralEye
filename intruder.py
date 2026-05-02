import cv2
import requests
from datetime import datetime

# Define Forbidden Zone (Top-Left X, Y and Bottom-Right X, Y)
ZONE_START = (350, 100) 
ZONE_END = (600, 400)
FIREBASE_URL = "https://neuraleye-88ed2-default-rtdb.asia-southeast1.firebasedatabase.app/Accidents.json"

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Draw the Forbidden Zone (Red Box)
    cv2.rectangle(frame, ZONE_START, ZONE_END, (0, 0, 255), 2)
    cv2.putText(frame, "RESTRICTED AREA", (350, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    for (x, y, w, h) in faces:
        # Calculate center of the person
        cx, cy = x + w//2, y + h//2
        
        # 1. TRIGGER: Check if center point is inside the Red Box
        if (ZONE_START[0] < cx < ZONE_END[0]) and (ZONE_START[1] < cy < ZONE_END[1]):
            cv2.putText(frame, "!!! INTRUDER !!!", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            
            # 2. IoT CLOUD ALERT
            try:
                requests.post(FIREBASE_URL, json={"event": "INTRUSION", "time": datetime.now().strftime("%H:%M:%S")})
            except: pass

        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)

    cv2.imshow("NeuralEye - Intruder Alert", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()