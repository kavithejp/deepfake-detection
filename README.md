# AI Fake Image and Voice Detection

This repository contains prototypes for multi-modal AI-generated content detection.

## 🚀 Projects Included

### 1. 🖥️ Sentinel AI Dashboard (Frontend)
A highly modern, futuristic cybersecurity dashboard for demonstrating the Deepfake Detection System.
-   **Features**: Neon UI, Live Webcam feed, Animated Scanning, Trust Score indicators, and System Logs.
-   **Run**: Simply open `index.html` in any modern web browser.

### 2. 🤖 Integrated Multi-Modal Detection (Python Backend)
The core logic combining Face Texture Analysis and Voice Liveness detection.
-   **Run**: `python integrated_detector.py`
-   **Key Commands**: Press **'v'** for voice check, **'q'** to quit.

---

## 🛠️ Installation
If you haven't already, install the required Python libraries:
```bash
pip install opencv-python numpy librosa sounddevice scipy
```

## 📂 File Structure
- `index.html` / `style.css` / `app.js`: Futuristic Frontend.
- `integrated_detector.py`: Multi-modal Python logic.
- `decision_engine.py`: Logic for combining face/voice results.
- `voice_analyzer.py`: Audio feature extraction.
- `deepfake_detector.py`: Image texture analysis.
