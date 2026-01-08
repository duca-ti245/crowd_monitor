# AI-Based Crowd Monitoring Using YOLO

This project implements an automated crowd monitoring system using Python and YOLOv8. It detects people in video footage, counts them, and triggers alerts if a crowd threshold is exceeded.

## Features
- **Person Detection**: Uses YOLOv8 to accurately detect people in each frame.
- **Crowd Counting**: counts the number of detected persons.
- **Overcrowding Alert**: 
    - Visual Warning: Status changes to "OVER CROWDED" (Red).
    - Console Alert: Prints alert messages.
    - Image Capture: Saves the frame as an image in the `alerts` folder.
- **Visualisation**: Draws bounding boxes and displays count/status on video.

## Prerequisites
- Python 3.8+
- Internet connection (for first-time model download)

## Installation

1.  **Clone or Download source code** into a folder.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Prepare Video**:
    - Place your CCTV or crowd video file in the project directory.
    - Rename it to `input_video.mp4` OR update the `VIDEO_PATH` variable in `detect_video.py` to match your filename.

2.  **Run the System**:
    ```bash
    python detect_video.py
    ```

3.  **Controls**:
    - Press **'q'** to quit the video window.

## Configuration
Open `detect_video.py` to adjust:
- `THRESHOLD`: Number of people to trigger an alert (Default: 10).
- `VIDEO_PATH`: Path to your input video.
- `ALERT_FOLDER`: Directory to save alert images.
