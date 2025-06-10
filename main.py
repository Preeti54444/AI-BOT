from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="MindEase API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase Admin
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Firebase initialization error: {e}")

# Initialize Firestore
db = firestore.client()

# Models
class Message(BaseModel):
    content: str
    user_id: str
    timestamp: Optional[datetime] = None

class MoodEntry(BaseModel):
    user_id: str
    mood_score: int  # 1-5
    note: Optional[str] = None
    timestamp: Optional[datetime] = None

class UserProfile(BaseModel):
    user_id: str
    email: Optional[str] = None
    is_anonymous: bool
    created_at: Optional[datetime] = None

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to MindEase API"}

@app.post("/chat")
async def chat(message: Message):
    try:
        # Store message in Firestore
        message.timestamp = datetime.now()
        chat_ref = db.collection('chats').document()
        chat_ref.set(message.dict())
        
        # TODO: Implement AI response logic
        response = {
            "message": "I understand you're feeling this way. Would you like to talk more about it?",
            "sentiment": "neutral"
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mood")
async def log_mood(mood: MoodEntry):
    try:
        mood.timestamp = datetime.now()
        mood_ref = db.collection('moods').document()
        mood_ref.set(mood.dict())
        return {"status": "success", "message": "Mood logged successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mood/history/{user_id}")
async def get_mood_history(user_id: str):
    try:
        moods = db.collection('moods').where('user_id', '==', user_id).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(30).stream()
        return [mood.to_dict() for mood in moods]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resources")
async def get_resources():
    # TODO: Implement dynamic resource fetching
    resources = [
        {
            "title": "Breathing Exercise",
            "description": "5-minute guided breathing exercise",
            "url": "https://example.com/breathing",
            "type": "exercise"
        },
        {
            "title": "Meditation Guide",
            "description": "10-minute meditation for stress relief",
            "url": "https://example.com/meditation",
            "type": "meditation"
        }
    ]
    return resources

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 