# 👁️ NeuralEye: AI-IoT Integrated Surveillance System

NeuralEye is an edge-based, AI-powered smart surveillance dashboard that integrates Computer Vision, IoT, and real-time alert mechanisms to enhance traditional security systems. Moving beyond passive CCTV monitoring, NeuralEye actively detects events, analyzes human behavior, and generates cloud-synced alerts instantly.

## 🚀 Key Features

* **Intruder Detection & Facial Recognition:** Utilizes LBPH algorithms to differentiate between registered personnel and "Unknown" individuals.
* **Analytical Customer Counter:** Tracks entry and exit footfall using positional memory and centroid tracking, logging identities in real-time.
* **Emergency & Fall Detection:** Employs MediaPipe Pose Estimation to calculate vertical-to-horizontal torso ratios, detecting sudden falls or accidents.
* **Digital Fencing (Intrusion):** Defines restricted Regions of Interest (ROI) and triggers alerts upon coordinate intersection.
* **IoT Cloud Sync:** Pushes real-time event logs, timestamps, and alerts to a Firebase Realtime Database.

## 🛠️ Technologies Used

* **Frontend GUI:** CustomTkinter (Modern Python UI)
* **Backend Logic:** Python Edge Architecture
* **AI / Computer Vision:** OpenCV (Facial Recognition), Google MediaPipe (Pose/Fall Estimation)
* **IoT & Cloud Database:** Firebase Realtime Database (REST API)

## 📂 Project Structure

```text
NeuralEye/
├── dataset/                # (Auto-generated) Stores grayscale face samples
├── trainer/                # (Auto-generated) Stores the trained LBPH model
├── main.py                 # The centralized CustomTkinter Command Dashboard
├── integrated_counter.py   # Identity-aware entry/exit counter
├── accident_detect.py      # Pose-estimation fall detector
├── intruder.py             # ROI-based digital fence monitor
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation