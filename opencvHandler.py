import cv2
import threading
import time
import numpy as np
from datetime import datetime

class PersonDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.person_detected = False
        self.last_detection_time = None
        self.running = True
        self.detection_callback = None
        self.loss_callback = None
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.last_notification = 0
        self.person_present = False
        
    def start(self, detection_callback=None, loss_callback=None):
        self.detection_callback = detection_callback
        self.loss_callback = loss_callback
        self.detection_thread.start()
        
    def stop(self):
        self.running = False
        self.detection_thread.join()
        self.cap.release()
        cv2.destroyAllWindows()
        
    def _detection_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            current_time = time.time()
            if len(faces) > 0:
                if not self.person_present and current_time - self.last_notification > 5:
                    if self.detection_callback:
                        self.detection_callback()
                        self.last_notification = current_time
                self.person_present = True
            else:
                if self.person_present and current_time - self.last_notification > 5:
                    if self.loss_callback:
                        self.loss_callback()
                        self.last_notification = current_time
                self.person_present = False
            
            time.sleep(0.1)  # Reduce CPU usage
