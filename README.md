# AI-Based Crowd Monitoring System Using YOLO 🚦

## 📌 Overview
This project implements an AI-based crowd monitoring system using Python and YOLOv8.
It detects people in video footage, counts the number of individuals, and triggers alerts
when crowd density exceeds a predefined threshold. The system is designed to support
crowd safety monitoring in public places using CCTV or recorded video feeds.

---

## ✨ Features
- **Person Detection**: Accurate people detection using YOLOv8
- **Crowd Counting**: Counts the total number of detected persons in each frame
- **Overcrowding Alerts**:
  - Visual warning displayed as **"OVER CROWDED"** (Red)
  - Console alert messages
  - Automatic image capture saved in the `alerts` folder
- **Visualization**:
  - Bounding boxes around detected people
  - Live count and status displayed on video feed

---

## 🛠️ Tech Stack
- Python
- OpenCV
- YOLOv8
- NumPy
- Ultralytics

---

## 📋 Prerequisites
- Python 3.8 or above
- Internet connection (for first-time YOLO model download)

---

## ⚙️ Installation
1. Clone or download the source code
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
