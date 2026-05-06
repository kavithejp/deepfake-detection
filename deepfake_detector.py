import cv2
import numpy as np

class DeepfakeDetector:
    def __init__(self):
        # In a real-world application, you would load a pre-trained model here:
        # self.model = load_model('deepfake_model.h5')
        print("Deepfake Detector Initialized (Using Texture Analysis Heuristic)")

    def predict(self, face_image):
        """
        Predicts if a face is REAL or FAKE.
        For this prototype, we use 'Laplacian Variance' to analyze image texture.
        Real faces usually have sharp textures, while some fakes/photos appear smoother.
        """
        # Convert face to grayscale
        gray_face = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance (measure of sharpness/texture)
        variance = cv2.Laplacian(gray_face, cv2.CV_64F).var()
        
        # Threshold for texture analysis (Heuristic)
        # Note: In a production app, this would be a Deep Learning model prediction
        threshold = 100 
        
        if variance > threshold:
            label = "REAL"
            confidence = min(99.0, variance / 5)
        else:
            label = "FAKE"
            confidence = 100 - (variance / 5)
            
        return label, confidence

def main():
    # Load face detection classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Initialize our custom detector
    detector = DeepfakeDetector()
    
    # Start webcam
    cap = cv2.VideoCapture(0)
    
    print("Deepfake Detection Prototype Started. Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Detection: Find faces in the frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            # 2. Pre-processing: Crop the face region
            face_roi = frame[y:y+h, x:x+w]
            
            if face_roi.size > 0:
                # 3. Classification: Predict if Real or Fake
                label, confidence = detector.predict(face_roi)
                
                # 4. Visualization: Draw results
                color = (0, 255, 0) if label == "REAL" else (0, 0, 255) # Green for Real, Red for Fake
                
                # Draw bounding box
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                # Add Label Text
                text = f"{label} ({confidence:.1f}%)"
                cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Display the output
        cv2.imshow('Deepfake Detection Prototype', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
