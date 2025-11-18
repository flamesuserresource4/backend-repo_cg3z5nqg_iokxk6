import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime

from database import create_document, get_documents
from schemas import SongRequest, Song

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Birthday Song Generator API"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# Simple rule-based lyric generator as a fallback (no external AI dependency)

def generate_lyrics(req: SongRequest) -> List[str]:
    name = req.name
    age_part = f" mit {req.age} Jahren" if req.age is not None else ""
    relation = f" mein/e {req.relation}" if req.relation else ""

    if req.language == "de":
        verse1 = [
            f"Hey {name}{relation}, heut' ist dein Tag!",
            "Kerzen brennen, jeder dich mag.",
            f"Wünsch dir Glück und Lachen{age_part}.",
            "Lass die Korken knallen, wir wollen's krachen!",
        ]
        hook = [
            f"Happy Birthday, {name}!",
            "Heute scheint die Welt nur für dich.",
            "Happy Birthday, {name} — bleib wunderbar!",
        ]
        verse2 = [
            "Fotos, Lichter, gute Vibes.",
            "Deine Story — beste Times!",
            "Freunde, Familie singen im Chor:",
            f"{name}, wir feiern dich so sehr!",
        ]
    else:
        verse1 = [
            f"Hey {name}{relation}, today is your day!",
            "Candles glow and cheers all the way.",
            f"Wishing you joy and laughter{age_part}.",
            "Pop the confetti, now and after!",
        ]
        hook = [
            f"Happy Birthday, {name}!",
            "Let the world shine bright for you.",
            f"Happy Birthday, {name} — stay amazing!",
        ]
        verse2 = [
            "Photos, lights, the vibe is right.",
            "Your story glows through the night.",
            "Friends and family sing along:",
            f"{name}, this is your birthday song!",
        ]

    # Style/tempo influence simple tweaks
    if req.style in ("hiphop", "rock"):
        verse1.append("Yeah!")
        verse2.append("Let's go!")
    if req.tempo == "fast":
        hook.append("Clap your hands, let's go, let's go!")
    elif req.tempo == "slow":
        hook.append("Take it slow, feel the glow.")

    lyrics = verse1 + [""] + hook + [""] + verse2 + [""] + hook
    return lyrics

@app.post("/api/songs", response_model=dict)
async def create_song(req: SongRequest):
    # Generate a title
    title = (
        ("Geburtstagssong für " if req.language == "de" else "Birthday Song for ") + req.name
    )

    lyrics = generate_lyrics(req)

    song_doc = Song(
        request=req,
        title=title,
        lyrics=lyrics,
        audio_seconds=30.0 if req.tempo != "slow" else 40.0,
        style=req.style,
        language=req.language,
        preview_note_count= len("".join(lyrics))
    )

    try:
        inserted_id = create_document("song", song_doc.model_dump())
    except Exception as e:
        # Database might be unavailable; still return the generated content
        inserted_id = None

    return {
        "id": inserted_id,
        "title": song_doc.title,
        "lyrics": song_doc.lyrics,
        "style": song_doc.style,
        "language": song_doc.language,
    }

@app.get("/api/songs", response_model=List[dict])
async def list_songs(limit: int = 20):
    try:
        docs = get_documents("song", limit=limit)
        # Normalize output
        results = []
        for d in docs:
            results.append({
                "id": str(d.get("_id")),
                "title": d.get("title"),
                "style": d.get("style"),
                "language": d.get("language"),
            })
        return results
    except Exception:
        # If DB not available, return empty list gracefully
        return []

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
