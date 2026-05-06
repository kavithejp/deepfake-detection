class DecisionEngine:
    def __init__(self):
        self.final_status = "INITIALIZING"
        self.color = (255, 255, 255) # White

    def evaluate(self, face_label, voice_label):
        """
        Combines Face and Voice results into a final security decision.
        
        Logic:
        - Face REAL + Voice REAL -> TRUSTED (Green)
        - One FAKE -> SUSPICIOUS (Yellow/Orange)
        - Both FAKE -> DEEPFAKE (Red)
        """
        
        if face_label == "REAL" and voice_label == "REAL":
            self.final_status = "TRUSTED"
            self.color = (0, 255, 0) # Green
            
        elif face_label == "FAKE" and voice_label == "FAKE":
            self.final_status = "DEEPFAKE DETECTED"
            self.color = (0, 0, 255) # Red
            
        elif face_label == "FAKE" or voice_label == "FAKE":
            self.final_status = "SUSPICIOUS ACTIVITY"
            self.color = (0, 165, 255) # Orange
            
        else:
            # Handles 'Scanning' or 'Waiting' states
            self.final_status = "ANALYZING..."
            self.color = (255, 255, 255) # White
            
        return self.final_status, self.color

if __name__ == "__main__":
    # Test Logic
    engine = DecisionEngine()
    print(engine.evaluate("REAL", "REAL"))
    print(engine.evaluate("REAL", "FAKE"))
    print(engine.evaluate("FAKE", "FAKE"))
