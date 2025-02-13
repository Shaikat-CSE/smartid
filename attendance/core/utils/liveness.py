# core/utils/liveness.py

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class LivenessDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )

    def detect_liveness(self, image_array):
        """
        Enhanced liveness detection with multiple checks and adjusted thresholds.
        Returns True for a real face, False for potential spoofing attempts.
        """
        try:
            if image_array is None:
                return False

            # Convert to grayscale
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
            
            # 1. Face Detection
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) != 1:  # Ensure exactly one face is detected
                return False
                
            # Get the face region
            (x, y, w, h) = faces[0]
            face_roi_gray = gray[y:y+h, x:x+w]
            
            # 2. Eye Detection
            eyes = self.eye_cascade.detectMultiScale(
                face_roi_gray,
                scaleFactor=1.1,
                minNeighbors=3,
                minSize=(20, 20)
            )
            
            if len(eyes) < 1:  # Reduced requirement to at least one eye
                return False
                
            # 3. Texture Analysis
            # Calculate local binary pattern variance as a texture measure
            laplacian_var = cv2.Laplacian(face_roi_gray, cv2.CV_64F).var()
            if laplacian_var < 50:  # Reduced threshold for texture variation
                return False
                
            # 4. Image Quality Check
            brightness = np.mean(face_roi_gray)
            contrast = np.std(face_roi_gray)
            
            if brightness < 40 or brightness > 250:  # Check for reasonable brightness
                return False
            if contrast < 20:  # Check for reasonable contrast
                return False
                
            # 5. Face Proportion Check
            face_ratio = w / h
            if face_ratio < 0.5 or face_ratio > 1.5:  # Check for reasonable face proportions
                return False

            return True

        except Exception as e:
            logger.error(f"Error in liveness detection: {str(e)}")
            return False