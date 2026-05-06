import cv2
import time
from deepfake_detector import DeepfakeDetector
from voice_analyzer import VoiceDetector
from decision_engine import DecisionEngine
from database_manager import DatabaseManager
from yolo_detector import YoloFaceDetector
from liveness_detector import LivenessDetector

def main():
    # Initialize all detectors
    print("Loading AI Models (YOLOv8, Audio, Liveness)...")
    face_detector = DeepfakeDetector()
    voice_detector = VoiceDetector()
    decision_engine = DecisionEngine()
    db_mgr = DatabaseManager()
    yolo_face_detector = YoloFaceDetector()
    liveness_detector = LivenessDetector()
    
    # Start webcam
    cap = cv2.VideoCapture(0)
    
    print("\n--- Multi-Modal Deepfake Decision System Started ---")
    print("Using YOLOv8 + MediaPipe Liveness Detection")
    print("Press 'v' to trigger Voice Liveness check.")
    print("Press 'q' to exit.")

    # Shared state for the loop
    current_face_label = "WAITING"
    last_logged_voice_result = None
    last_log_time = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # --- 1. LIVENESS DETECTION (BLINK CHECK) ---
        l_status, blink_count, l_status_text = liveness_detector.check_liveness(frame)

        # --- 2. FACE DETECTION (YOLOv8) ---
        faces = yolo_face_detector.detect_faces(frame)

        current_face_label = "WAITING"
        for (x, y, w, h) in faces:
            y = max(0, y)
            x = max(0, x)
            face_roi = frame[y:y+h, x:x+w]
            
            if face_roi.size > 0:
                label, confidence = face_detector.predict(face_roi)
                current_face_label = label
                
                f_color = (0, 255, 0) if label == "REAL" else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x+w, y+h), f_color, 2)
                
                # Label box
                cv2.rectangle(frame, (x, y-30), (x+w, y), f_color, -1)
                cv2.putText(frame, f"{label} | Blinks: {blink_count}", (x+5, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # --- 3. VOICE DETECTION STATUS ---
        current_voice_label = voice_detector.last_result
        
        # --- 4. FINAL DECISION ENGINE ---
        final_msg, final_color = decision_engine.evaluate(current_face_label, current_voice_label)
        
        # Override decision if no blink detected (Liveness Check)
        if blink_count == 0 and current_face_label != "WAITING":
            final_msg = "LIVENESS FAIL: PLEASE BLINK"
            final_color = (0, 165, 255) # Orange for warning

        # --- 5. LOG TO DATABASE (PERIODICALLY EVERY 2 SECONDS) ---
        current_time = time.time()
        if current_time - last_log_time > 2: # 2 second interval
            trust_score = 95 if final_msg == "ACCESS GRANTED" else (40 if "LIVENESS" in final_msg else (10 if final_msg != "STANDBY" else 0))
            
            # Push data even if waiting to show live connection
            db_mgr.log_detection(current_face_label, current_voice_label, trust_score, final_msg)
            print(f"DEBUG: Pushed Status to Dashboard [Face: {current_face_label}, Decision: {final_msg}]")
            last_log_time = current_time



        # UI Overlay
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 120), (0, 0, 0), -1)
        cv2.putText(frame, f"STATUS: {final_msg}", (20, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, final_color, 2)
        cv2.putText(frame, f"Liveness: {l_status} ({blink_count} blinks)", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        cv2.putText(frame, f"Face: {current_face_label} | Voice: {current_voice_label}", (20, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        if voice_detector.is_recording:
            cv2.putText(frame, "RECORDING AUDIO...", (frame.shape[1]-250, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            last_logged_voice_result = "ANALYZING..." 

        # --- 5. INPUT HANDLING ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('v'): # Trigger voice check
            voice_detector.start_analysis_thread()

        # Display output
        cv2.imshow('AIVENTRA | Multi-Modal Security System', frame)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()



