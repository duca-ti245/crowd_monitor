import cv2
from ultralytics import YOLO
import datetime
import os
import sys
import numpy as np
import time

class VideoCamera:
    def __init__(self):
        # Configuration
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.VIDEO_PATH = os.path.join(self.BASE_DIR, 'input_video (2).mp4')
        self.ALERT_FOLDER = os.path.join(self.BASE_DIR, 'alerts')
        
        # Settings
        self.THRESHOLD = 12
        self.USE_WEBCAM = True # Default to webcam for web app (or we could make this configurable)
        self.SHOW_HEATMAP = True
        
        # Create alert folder
        if not os.path.exists(self.ALERT_FOLDER):
            os.makedirs(self.ALERT_FOLDER)

        # Initialize Model
        print("Initializing YOLOv8 model...")
        self.model = YOLO('yolov8n.pt')

        # Initialize Video Source
        # For simplicity in this web version, we might hardcode to 0 (webcam) 
        # or try to file if 0 fails, similar to the script logic.
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Webcam not found, trying video file...")
            if os.path.exists(self.VIDEO_PATH):
                self.cap = cv2.VideoCapture(self.VIDEO_PATH)
            else:
                # Fallback search
                import glob
                video_files = glob.glob(os.path.join(self.BASE_DIR, "*.mp4"))
                if video_files:
                    self.cap = cv2.VideoCapture(video_files[0])
                else:
                     print("Warning: No video source found. Using placeholder.")
                     # We don't raise error, just let read() fail and show error frame
                     self.cap = None

        # Check if cap is None or not opened
        if self.cap is None or not self.cap.isOpened():
             print("Error opening video source. App will show error frame.")



        self.alert_cooldown = 0
        
        # Latest Stats
        self.person_count = 0
        self.last_count = 0
        self.trend = "stable" # up, down, stable
        self.last_alert_time = "None"
        self.status = "NORMAL"
        
    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

    def get_frame(self):
        if self.cap is None or not self.cap.isOpened():
             # Return error frame immediately
             blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
             cv2.putText(blank_frame, "NO CAMERA SOURCE", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
             ret, jpeg = cv2.imencode('.jpg', blank_frame)
             return jpeg.tobytes()

        success, frame = self.cap.read()
        if not success:
            # If video file ends, loop it
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = self.cap.read()
            if not success:
                # If still fails (or webcam fails), return an error frame
                blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(blank_frame, "CAMERA SOURCE ERROR", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Update status
                self.status = "CAMERA_ERR"
                ret, jpeg = cv2.imencode('.jpg', blank_frame)
                return jpeg.tobytes()

        # YOLO Inference
        results = self.model(frame, classes=[0], conf=0.5, verbose=False)
        result = results[0]
        boxes = result.boxes
        person_count = len(boxes)

        # Heatmap Generation
        # Heatmap Generation
        if self.SHOW_HEATMAP:
            # Create a blank grayscale mask for the heatmap
            heatmap_matrix = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)
            
            # Map centroids for heatmap
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                # Draw larger, softer circles (radius=60)
                cv2.circle(heatmap_matrix, (cx, cy), radius=60, color=255, thickness=-1)
            
            # Apply Strong Gaussian Blur to smooth into a "cloud"
            heatmap_blurred = cv2.GaussianBlur(heatmap_matrix, (121, 121), 0)
            
            # Apply ColorMap
            heatmap_color = cv2.applyColorMap(heatmap_blurred, cv2.COLORMAP_JET)
            
            # Create Transparency Mask: Only show areas where heat > 10
            # This makes the background transparent instead of blue tinted
            _, mask_thresh = cv2.threshold(heatmap_blurred, 10, 255, cv2.THRESH_BINARY)
            mask_3ch = cv2.cvtColor(mask_thresh, cv2.COLOR_GRAY2BGR)
            
            # Extract only the colored parts (heat)
            heatmap_color_masked = cv2.bitwise_and(heatmap_color, mask_3ch)
            
            # Black out the corresponding area in original frame to blend cleanly
            # Or just addWeighted in that region. Let's use simple weighted addition but masked.
            # Convert mask to float for alpha blending
            alpha = mask_thresh.astype(float) / 255.0 * 0.5 # 0.5 opacity
            alpha = cv2.merge([alpha, alpha, alpha])
            
            # Blend only where mask is active
            frame = (frame * (1.0 - alpha) + heatmap_color * alpha).astype(np.uint8)

        # Status Logic
        # Trend Logic
        if person_count > self.last_count:
            self.trend = "up"
        elif person_count < self.last_count:
            self.trend = "down"
        else:
            self.trend = "stable"
        
        self.last_count = person_count
        self.person_count = person_count
        
        if person_count > self.THRESHOLD:
            status = "OVER CROWDED"
            self.status = "OVER CROWDED"
            color = (0, 0, 255) # Red
            
            # Alert Logic
            if self.alert_cooldown == 0:
                print(f"[ALERT] Count: {person_count}")
                # We skip winsound here to avoid server-side noise/blocking
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                # Update last alert time for dashboard
                self.last_alert_time = datetime.datetime.now().strftime("%I:%M:%S %p")
                
                filename = f"{self.ALERT_FOLDER}/alert_{timestamp}_{person_count}_people.jpg"
                cv2.imwrite(filename, frame)
                self.alert_cooldown = 30
        else:
            status = "NORMAL"
            self.status = "NORMAL"
            color = (0, 255, 0) # Green

        if self.alert_cooldown > 0:
            self.alert_cooldown -= 1

        # Draw Annotations
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (400, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Text
        cv2.putText(frame, f"Status: {status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, f"Count: {person_count} (Threshold: {self.THRESHOLD})", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Encode JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
