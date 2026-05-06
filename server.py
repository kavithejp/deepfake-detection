from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from database_manager import DatabaseManager
from firebase_admin import firestore

app = FastAPI()
db_mgr = DatabaseManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTES MUST COME BEFORE STATIC MOUNT ---

@app.get("/latest")
async def get_latest_detection():
    if db_mgr.db is None:
        return {"error": "Database not connected"}
    
    try:
        # Query Firestore for the latest detection
        docs = db_mgr.db.collection('detections')\
            .order_by('timestamp', direction=firestore.Query.DESCENDING)\
            .limit(1).get()
        
        for doc in docs:
            data = doc.to_dict()
            if 'timestamp' in data:
                data['timestamp'] = data['timestamp'].isoformat()
            return data
        
        return {"message": "No detections found"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze")
async def analyze_identity():
    face_status = "REAL"
    voice_status = "REAL"
    trust_score = 98
    decision = "ACCESS GRANTED"
    db_mgr.log_detection(face_status, voice_status, trust_score, decision)
    return {
        "face_status": face_status,
        "voice_status": voice_status,
        "trust_score": trust_score,
        "decision": decision
    }

# Serve static files from the current directory (Mount this LAST)
app.mount("/", StaticFiles(directory=".", html=True), name="static")

@app.get("/")
def home():
    return FileResponse("index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
