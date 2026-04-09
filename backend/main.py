from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import os
import shutil
import requests
import hashlib # Neu: Für Passwort-Sicherheit
from dotenv import load_dotenv

# --- SETUP ---
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datenbank-Konfiguration komplett über .env (WICHTIG!)
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "kletter_kompass"),
    "ssl_verify_cert": False # Falls du TiDB Cloud nutzt
}

# Hilfsfunktion für Passwort-Hashing
def hash_pw(pw):
    return hashlib.sha256(str.encode(pw)).hexdigest()

# --- DATEN-MODELLE ---
# (Deine Modelle bleiben gleich, wir ergänzen nur eines für die Crew)
class FeedbackData(BaseModel):
    nutzer_id: int
    nachricht: str

# --- ROUTEN ---

@app.post("/login")
def login(data: LoginData):
    # Admin-Check (Sicher über .env)
    if data.username == os.getenv("ADMIN_USER") and data.password == os.getenv("ADMIN_PASSWORD"):
        return {"status": "success", "rolle": "admin", "nutzer_id": 0}
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Sicherheit: Wir hashen das eingegebene Passwort zum Vergleich
        hashed = hash_pw(data.password)
        query = "SELECT * FROM nutzer WHERE benutzername = %s AND passwort = %s"
        cursor.execute(query, (data.username, hashed))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {"status": "success", "rolle": user['rolle'], "nutzer_id": user['nutzer_id']}
        return {"status": "error", "message": "Zugriff verweigert"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/wetter/{lat}/{lon}")
def get_weather(lat: float, lon: float):
    # API KEY GEHEIMHALTEN: Niemals hart in den Code schreiben!
    api_key = os.getenv("OPENWEATHER_KEY") 
    if not api_key:
        return {"error": "API Key fehlt im Backend"}
        
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=de"
    return requests.get(url).json()

# --- NEU: ADMIN-LÖSCHFUNKTIONEN ---
@app.delete("/admin/feedback/{f_id}")
def delete_feedback(f_id: int):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM feedback WHERE id = %s", (f_id,))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/admin/vorschlag/{p_id}")
def delete_vorschlag(p_id: int):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vorschlaege WHERE id = %s", (p_id,))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# (Rest deiner Routen für Profil und Spielplätze...)
