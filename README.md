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
```

## ⚙️ Installation & Setup
1. Clone the repository:

* Bash
* git clone [https://github.com/AadhyaNigam/NeuralEye.git](https://github.com/AadhyaNigam/NeuralEye.git)
* cd NeuralEye

2. Install dependencies:

* Bash
* pip install -r requirements.txt

3. Configure Firebase (IoT):

* Create a Firebase Realtime Database.
* Set Read/Write rules to true (for local testing).
* Replace the FIREBASE_URL placeholder in the Python scripts with your actual Firebase URL.

4. Run the Dashboard:

* Bash
* python main.py


## 💻 Usage Flow

* Register: Click "Register New User" to capture 50 face samples. (Data is synced to Firebase Master List).
* Train: Click "Train AI Model" to generate the trainer.yml file.
* Launch Security: Use the dashboard to launch the live face monitor, customer counter, or accident detection modules.
* Press q to safely close any active camera window and return to the dashboard.

---

## 📜 License

This project is licensed under the MIT License.

## 👤 Author

Aadhya Nigam [(https://github.com/AadhyaNigam)]
