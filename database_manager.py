import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Path to your service account key
        cred_path = "serviceAccountKey.json"
        
        if not os.path.exists(cred_path):
            print(f"CRITICAL ERROR: {cred_path} not found.")
            self.db = None
            return

        try:
            # Check if firebase is already initialized
            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            print("Successfully connected to Firebase Firestore.")
        except Exception as e:
            print(f"Firebase Initialization Error: {e}")
            self.db = None

    def log_detection(self, face_status, voice_status, trust_score, decision):
        """Saves a detection result to the 'detections' collection."""
        if self.db is None:
            print("Database not connected. Skipping log.")
            return

        try:
            doc_ref = self.db.collection('detections').document()
            data = {
                'timestamp': datetime.datetime.now(),
                'face_status': face_status,
                'voice_status': voice_status,
                'trust_score': trust_score,
                'decision': decision
            }
            doc_ref.set(data)
            print(f"Log saved to Firebase: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            print(f"Error saving log to Firebase: {e}")
            return None

if __name__ == "__main__":
    # Test connection
    db_mgr = DatabaseManager()
    db_mgr.log_detection("REAL", "REAL", 98, "ACCESS GRANTED")
