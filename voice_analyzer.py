import sounddevice as sd
import numpy as np
import librosa
from scipy.io.wavfile import write
import threading
import time

class VoiceDetector:
    def __init__(self, sample_rate=22050, duration=2):
        self.sample_rate = sample_rate
        self.duration = duration
        self.is_recording = False
        self.last_result = "WAITING"
        self.last_confidence = 0.0

    def record_and_analyze(self):
        """Records a short audio clip and analyzes it."""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.last_result = "ANALYZING..."
        
        try:
            # Record audio
            recording = sd.rec(int(self.duration * self.sample_rate), 
                              samplerate=self.sample_rate, channels=1)
            sd.wait() # Wait for recording to finish
            
            # Convert to float for librosa
            audio_data = recording.flatten()
            
            # Extract Features using librosa
            # MFCCs (Mel-frequency cepstral coefficients) are standard for voice analysis
            mfccs = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
            mfcc_mean = np.mean(mfccs, axis=1)
            
            # Prototype Logic: Spectral Flatness 
            # (Real voices usually have specific spectral patterns; synthesized ones might differ)
            flatness = librosa.feature.spectral_flatness(y=audio_data)
            avg_flatness = np.mean(flatness)
            
            # Heuristic Placeholder:
            # In a real model, you'd pass 'mfcc_mean' into a neural network
            if 0.001 < avg_flatness < 0.1: # Typical range for human speech
                self.last_result = "REAL"
                self.last_confidence = 90.0 + (avg_flatness * 10)
            else:
                self.last_result = "FAKE"
                self.last_confidence = 85.0
                
        except Exception as e:
            print(f"Audio Error: {e}")
            self.last_result = "ERROR"
        
        self.is_recording = False

    def start_analysis_thread(self):
        """Runs the recording in a background thread so the video doesn't freeze."""
        thread = threading.Thread(target=self.record_and_analyze)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    # Test the module independently
    print("Testing Voice Detector... Speak into the microphone.")
    vd = VoiceDetector()
    vd.record_and_analyze()
    print(f"Result: {vd.last_result} (Confidence: {vd.last_confidence:.1f}%)")
