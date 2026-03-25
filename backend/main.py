from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import os
import shutil
import requests
from dotenv import load_dotenv

# --- SETUP ---
load_dotenv()
app = FastAPI()

# CORS für die Verbindung zum Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ordner für Bilder
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Datenbank-Verbindung (Passwort kommt aus der .env)
db_config = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("DB_PASSWORD"),
    "database": "kletter_kompass"
}

# --- DATEN-MODELLE ---
class LoginData(BaseModel):
    username: str
    password: str

class RegisterData(BaseModel):
    benutzername: str
    passwort: str
    email: str
    vorname: str
    nachname: str
    alter_wert: int
    geschlecht: str
    agb: bool

class RatingData(BaseModel):
    sterne: int
    spiel_id: int
    kommentar: str = "Beta-User"
    nutzer_id: int = 1

# --- ROUTEN ---

@app.get("/")
def home():
    return {"msg": "KletterKompass API läuft!"}

@app.post("/login")
def login(data: LoginData):
    # 1. Admin-Check über .env
    if data.username == os.getenv("ADMIN_USER") and data.password == os.getenv("ADMIN_PASSWORD"):
        return {"status": "success", "rolle": "admin", "nutzer_id": 0}
    
    # 2. User-Check über Datenbank
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM nutzer WHERE benutzername = %s AND passwort = %s"
        cursor.execute(query, (data.username, data.password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {"status": "success", "rolle": user['rolle'], "nutzer_id": user['nutzer_id']}
        return {"status": "error", "message": "Zugriff verweigert"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/register")
def register(data: RegisterData):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """
            INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, alter_wert, geschlecht, akzeptiert_agb, rolle) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'partner')
        """
        werte = (data.benutzername, data.passwort, data.email, data.vorname, data.nachname, data.alter_wert, data.geschlecht, data.agb)
        cursor.execute(query, werte)
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/spielplaetze")
def get_spielplaetze():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM spielplaetze WHERE status = 'freigegeben'")
    res = cursor.fetchall()
    conn.close()
    return res

@app.get("/admin/vorschlaege")
def get_vorschlaege():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM spielplaetze WHERE status = 'vorschlag'")
    res = cursor.fetchall()
    conn.close()
    return res

@app.post("/upload-foto")
async def upload_foto(file: UploadFile = File(...)):
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "success", "filename": file.filename}

@app.post("/bewertungen")
def save_rating(data: RatingData):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO bewertungen (sterne, kommentar, nutzer_id, spiel_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (data.sterne, data.kommentar, data.nutzer_id, data.spiel_id))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.put("/admin/freigeben/{p_id}")
def freigeben_platz(p_id: int):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE spielplaetze SET status = 'freigegeben' WHERE spiel_id = %s", (p_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/wetter/{lat}/{lon}")
def get_weather(lat: float, lon: float):
    api_key = "3b2ece3cd1c30a9e495211df12ffc662"
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=de"
    return requests.get(url).json()
# --- NEU: PROFIL-DATEN HOLEN ---
@app.get("/profil/{n_id}")
def get_profil(n_id: int):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT vorname, nachname, email, alter_wert, geschlecht FROM nutzer WHERE nutzer_id = %s", (n_id,))
    user = cursor.fetchone() # Gibt Dictionary oder None zurück
    conn.close()
    return user

# --- NEU: PROFIL AKTUALISIEREN ---
@app.put("/profil/update/{n_id}")
def update_profil(n_id: int, data: RegisterData):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = """
        UPDATE nutzer SET vorname=%s, nachname=%s, email=%s, alter_wert=%s, geschlecht=%s 
        WHERE nutzer_id=%s
    """
    cursor.execute(query, (data.vorname, data.nachname, data.email, data.alter_wert, data.geschlecht, n_id))
    conn.commit()
    conn.close()
    return {"status": "success"}

# --- NEU: FEEDBACK SENDEN ---
class FeedbackData(BaseModel):
    nutzer_id: int
    nachricht: str

@app.post("/feedback")
def send_feedback(data: FeedbackData):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO feedback (nutzer_id, nachricht) VALUES (%s, %s)", (data.nutzer_id, data.nachricht))
    conn.commit()
    conn.close()
    return {"status": "success"}