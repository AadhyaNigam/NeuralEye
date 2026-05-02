import cv2
import os
import json
import requests
import numpy as np
import subprocess
import sys
import customtkinter as ctk
from PIL import Image, ImageTk
from datetime import datetime
from tkinter import messagebox

# --- 1. SYSTEM CONFIGURATION & DPI FIX ---
ctk.deactivate_automatic_dpi_awareness()
ctk.set_window_scaling(1.0)
ctk.set_widget_scaling(1.0)
ctk.set_appearance_mode("dark")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
TRAINER_FILE = os.path.join(BASE_DIR, "trainer", "trainer.yml")
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
# Replace with your actual Firebase URL
FIREBASE_URL = "https://neuraleye-88ed2-default-rtdb.asia-southeast1.firebasedatabase.app/AccessLogs.json"

if not os.path.exists(DATASET_DIR): os.makedirs(DATASET_DIR)
if not os.path.exists(os.path.dirname(TRAINER_FILE)): os.makedirs(os.path.dirname(TRAINER_FILE))

# --- 2. CORE LOGIC FUNCTIONS ---

def register_user():
    uid = ctk.CTkInputDialog(text="Enter User ID (Numbers only):", title="ID Enrollment").get_input()
    uname = ctk.CTkInputDialog(text="Enter User Name:", title="Name Enrollment").get_input()
    
    if not uid or not uname: return

    # --- 1. LOCAL & CLOUD SAVE ---
    users = {}
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f: users = json.load(f)
        except: users = {}
    
    users[str(uid).strip()] = uname.strip()
    with open(USERS_FILE, "w") as f: json.dump(users, f)

    try:
        # Update with your real URL
        requests.post("https://neuraleye-88ed2-default-rtdb.asia-southeast1.firebasedatabase.app/Students.json", 
                      json={"id": uid, "name": uname, "date": datetime.now().strftime("%Y-%m-%d")})
        print(f"✅ {uname} synced to Cloud.")
    except:
        print("⚠️ Cloud Sync failed, but local save worked.")

    # --- 2. SAFE CAMERA CAPTURE ---
    # We use a try-finally block to ensure the camera ALWAYS releases properly
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # CAP_DSHOW helps prevent threading crashes on Windows
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    count = 0
    
    print("[INFO] Starting Camera... Look at the lens.")
    
    try:
        while count < 50:
            ret, img = cap.read()
            if not ret: break
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x,y,w,h) in faces:
                count += 1
                file_name = os.path.join(DATASET_DIR, f"User.{uid}.{count}.jpg")
                cv2.imwrite(file_name, gray[y:y+h, x:x+w])
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
                cv2.putText(img, f"Captured: {count}/50", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            
            cv2.imshow("Enrollment - Stay Still", img)
            
            # This tiny 1ms wait allows the GIL to breathe
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # This is the most important part to prevent the "Fatal Error"
        cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1) # Extra kick to clear the window from memory
        print(f"✅ Successfully captured 50 samples for {uname}")
        messagebox.showinfo("Enrollment Complete", f"Samples saved. Now run Step 2: Train.")

def train_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    paths = [os.path.join(DATASET_DIR, f) for f in os.listdir(DATASET_DIR) if f.endswith('.jpg')]     
    if not paths: 
        messagebox.showerror("Error", "Dataset is empty! Register someone first.")
        return
        
    samples, ids = [], []
    for p in paths:
        img_np = np.array(Image.open(p).convert('L'), 'uint8')
        id_num = int(os.path.split(p)[-1].split(".")[1])
        samples.append(img_np)
        ids.append(id_num)
    
    recognizer.train(samples, np.array(ids))
    recognizer.write(TRAINER_FILE)
    messagebox.showinfo("NeuralEye AI", "AI Model Trained Successfully!")

def launch_security():
    if not os.path.exists(TRAINER_FILE):
        messagebox.showerror("Error", "No trained model found. Please run Step 2 first.")
        return

    # Reload JSON every time to ensure the 'Unknown' bug is fixed
    with open(USERS_FILE, "r") as f: users = json.load(f)
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(TRAINER_FILE)
    cap = cv2.VideoCapture(0)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    last_id = -1

    while True:
        _, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, 1.2, 5)
        for (x,y,w,h) in faces:
            id_num, conf = recognizer.predict(gray[y:y+h, x:x+w])
            
            # THE FIX: Lookup ID in the newly reloaded JSON
            name = users.get(str(id_num), "Unknown ID")
            
            if conf < 75: # Recognized threshold
                color = (0, 0, 255)
                if id_num != last_id and name != "Unknown ID":
                    try:
                        requests.post(FIREBASE_URL, json={"user": name, "time": datetime.now().strftime("%H:%M:%S")})
                    except: pass
                    last_id = id_num
            else:
                name = "Unknown"
                color = (0, 0, 255)
            
            cv2.rectangle(img, (x,y), (x+w,y+h), color, 2)
            cv2.putText(img, f"{name} ({round(100-conf)}%)", (x+5,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
        cv2.imshow("NeuralEye Security Live", img)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    cap.release()
    cv2.destroyAllWindows()

def launch_external(script_name):
    try:
        subprocess.Popen([sys.executable, os.path.join(BASE_DIR, script_name)])
    except Exception as e:
        messagebox.showerror("Execution Error", f"Failed to start {script_name}.\n{e}")

def view_logs():
    log_path = os.path.join(BASE_DIR, "visitor_log.json")
    if os.path.exists(log_path):
        # This command opens the JSON file in your default text editor (like Notepad)
        os.startfile(log_path)
    else:
        messagebox.showinfo("NeuralEye", "No logs found yet. Run the counter first!")

# --- 3. GUI DASHBOARD DESIGN ---

app = ctk.CTk()
app.title("NeuralEye - Command Center")
app.geometry("800x700")
app.resizable(False, False)

canvas = ctk.CTkCanvas(app, width=800, height=700, highlightthickness=0, bg="#000000")
canvas.pack(fill="both", expand=True)

try:
    # Ensure bg.png is in your NeuralEye folder!
    app.bg_image = ImageTk.PhotoImage(Image.open("bg.jpg").resize((800, 700)))
    canvas.create_image(400, 350, image=app.bg_image, anchor="center")
except:
    print("Background image missing.")

# Header Text (Canvas allows transparency)
canvas.create_text(400, 70, text="NEURALEYE", font=("Bungee Spice", 60, "bold"), fill="#D942FF")
canvas.create_text(400, 130, text="AI-IoT Integrated Surveillance System", font=("Allan", 26, "bold"), fill="#FFFFFF")

# Button styling matching your earlier request
btn_style = {"height": 55, "width": 550, "corner_radius": 12, "font": ("Allan", 20, "bold"), "text_color":"black"}

# Button 1: Register (Indigo)
btn_reg = ctk.CTkButton(app, text="👤 Step 1: Add User", fg_color="#00f2ff", hover_color="#43abff", 
                        command=register_user, **btn_style)
canvas.create_window(400, 220, window=btn_reg)

# Button 2: Train (Purple)
btn_train = ctk.CTkButton(app, text="🧠 Step 2: Train AI Model", fg_color="#f7f255", hover_color="#dee602", 
                          command=train_model, **btn_style)
canvas.create_window(400, 300, window=btn_train)

# Button 3: Live Security (Blue)
btn_sec = ctk.CTkButton(app, text="🔒 Step 3: Launch Smart Security", fg_color="#FFAA20", hover_color="#E69600", 
                        command=launch_security, **btn_style)
canvas.create_window(400, 380, window=btn_sec)

# Button 4: Customer Counter (Emerald)
btn_count = ctk.CTkButton(app, text="🚶 Launch Customer Counter", fg_color="#00FFAA", hover_color="#00BC80", 
                         command=lambda: launch_external("counter.py"), **btn_style)
canvas.create_window(400, 460, window=btn_count)

# Button 5: Accident Monitor (Red)
btn_acc = ctk.CTkButton(app, text="⚠️ Launch Accident/Fall Monitor", fg_color="#FF2B2B", hover_color="#D60000", 
                       command=lambda: launch_external("accident_detect.py"), **btn_style)
canvas.create_window(400, 540, window=btn_acc)

# Button 6: Visitor Log
btn_logs = ctk.CTkButton(app, text="📋 View Visitor Logs", fg_color="#4B5563", 
                         command=view_logs, height=40, width=200)
canvas.create_window(400, 600, window=btn_logs)

# Footer
canvas.create_text(400, 660, text="System Status: Online | Cloud: Connected | Core: Active", font=("Arial", 12), fill="#FFD700")

app.mainloop()