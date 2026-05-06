from ultralytics import YOLO
import cv2

class YoloFaceDetector:
    def __init__(self):
        # We use the nano version of YOLOv8 for speed
        # This will download the model automatically on first run
        try:
            # Note: Standard yolov8n detects 80 classes. 
            # For a production app, you'd use a face-specific trained YOLO model.
            self.model = YOLO('yolov8n.pt') 
            print("YOLOv8 initialized successfully.")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            self.model = None

    def detect_faces(self, frame):
        """
        Detects people and returns bounding boxes for their head area.
        In a real scenario, you'd use a model specifically trained on faces.
        """
        if self.model is None:
            return []

        results = self.model(frame, classes=[0], verbose=False) # Class 0 is 'person'
        
        faces = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Get coordinates
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Heuristic: The head is usually in the top 30% of the person's bounding box
                # For a true deepfake app, we would use a face-specific YOLO model.
                h = y2 - y1
                face_y2 = y1 + int(h * 0.4) 
                
                # We return the coordinates in (x, y, w, h) format to match Haar Cascade
                faces.append((x1, y1, x2 - x1, face_y2 - y1))
                
        return faces

if __name__ == "__main__":
    # Test
    cap = cv2.VideoCapture(0)
    detector = YoloFaceDetector()
    while True:
        ret, frame = cap.read()
        if not ret: break
        faces = detector.detect_faces(frame)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.imshow("YOLO Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    cap.release()
    cv2.destroyAllWindows()
