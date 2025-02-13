import cv2
import face_recognition
import logging

logger = logging.getLogger(__name__)

class FaceDetector:
    def get_face_encoding(self, image):
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_image, model="hog")
            
            if not face_locations:
                logger.error("No face detected")
                return None
                
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            return face_encodings[0] if face_encodings else None
            
        except Exception as e:
            logger.error("Face detection failed")
            return None
    
    def verify_face(self, known_encoding, face_encoding):
        if known_encoding is None or face_encoding is None:
            return False
        return face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.6)[0]
    
    def find_duplicate_face(self, new_encoding, existing_encodings):
        if not existing_encodings or new_encoding is None:
            return False
        return any(face_recognition.compare_faces(existing_encodings, new_encoding, tolerance=0.6))