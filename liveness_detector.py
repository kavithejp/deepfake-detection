import cv2
import numpy as np
import mediapipe as mp

class LivenessDetector:
    def __init__(self):
        # Initializing MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        # Eye landmarks indices (MediaPipe Face Mesh)
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        
        self.blink_count = 0
        self.is_blinking = False
        self.liveness_score = 0
        self.status = "CHECKING LIVENESS"

    def calculate_ear(self, landmarks, eye_indices, img_w, img_h):
        """Calculates Eye Aspect Ratio (EAR)"""
        coords = []
        for idx in eye_indices:
            lm = landmarks[idx]
            coords.append(np.array([lm.x * img_w, lm.y * img_h]))
        
        coords = np.array(coords)
        # Vertical distances
        v1 = np.linalg.norm(coords[1] - coords[5])
        v2 = np.linalg.norm(coords[2] - coords[4])
        # Horizontal distance
        h = np.linalg.norm(coords[0] - coords[3])
        
        ear = (v1 + v2) / (2.0 * h)
        return ear

    def check_liveness(self, frame):
        """Processes frame for blink detection and liveness"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        is_live = False
        h, w, _ = frame.shape

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            
            left_ear = self.calculate_ear(landmarks, self.LEFT_EYE, w, h)
            right_ear = self.calculate_ear(landmarks, self.RIGHT_EYE, w, h)
            avg_ear = (left_ear + right_ear) / 2.0

            # Blink Detection Logic
            if avg_ear < 0.2: # Eye closed
                self.is_blinking = True
                self.status = "BLINK DETECTED"
            else:
                if self.is_blinking:
                    self.blink_count += 1
                    self.is_blinking = False
                self.status = "PLEASE BLINK"

            # Liveness Score based on blinks
            if self.blink_count > 0:
                self.liveness_score = 100
                self.status = "LIVENESS PASSED"
                is_live = True
            else:
                self.liveness_score = 40 # Suspicious until blink
        else:
            self.status = "NO FACE DETECTED"
            
        return is_live, self.liveness_score, self.status
