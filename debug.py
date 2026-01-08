import cv2
import os
import sys

print("Python executable:", sys.executable)
print("Current working dir:", os.getcwd())

video_path = 'input_video.mp4'
if os.path.exists(video_path):
    print(f"Video file found: {os.path.abspath(video_path)}")
    print(f"File size: {os.path.getsize(video_path)} bytes")
else:
    print(f"ERROR: Video file NOT found at: {os.path.abspath(video_path)}")
    sys.exit(1)

try:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("ERROR: cv2.VideoCapture could not open the file.")
    else:
        ret, frame = cap.read()
        if ret:
            print(f"Success: Video opened. Frame shape: {frame.shape}")
        else:
            print("ERROR: Video opened but could not read first frame.")
    cap.release()
except Exception as e:
    print(f"Exception opening video: {e}")

try:
    import ultralytics
    print(f"Ultralytics version: {ultralytics.__version__}")
    from ultralytics import YOLO
    model = YOLO('yolov8n.pt')
    print("Success: YOLO model loaded.")
except Exception as e:
    print(f"Exception loading YOLO: {e}")
