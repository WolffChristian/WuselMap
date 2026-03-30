import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import hashlib
from PIL import Image
import io
import base64

# Verbindung zu Google Sheets
def get_conn():
    return st.connection("gsheets", type=GSheetsConnection)

# Passwort-Verschlüsselung (für Login & Registrierung)
def hash_passwort(passwort):
    return hashlib.sha256(str.encode(passwort)).hexdigest()

# Bild-Optimierung für den Upload (macht Bilder kleiner/schneller)
def image_optimieren(bild_file):
    if bild_file is None: return None
    img = Image.open(bild_file)
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=75)
    return base64.b64encode(buffer.getvalue()).decode()

# DATEN LESEN (Simuliert SQL-Abfragen)
def hole_df(query, params=None):
    conn = get_conn()
    sheet_name = "spielplaetze"
    if "FROM nutzer" in query: sheet_name = "nutzer"
    elif "FROM vorschlaege" in query: sheet_name = "vorschlaege"
    elif "FROM feedback" in query: sheet_name = "feedback"
    
    try:
        df = conn.read(worksheet=sheet_name, ttl="0s")
        # Falls in GSheets 'Lon' steht, für Plotly zu 'lon' machen
        if 'Lon' in df.columns: df = df.rename(columns={'Lon': 'lon'})
        
        # Filter für Login (wenn params übergeben werden)
        if params and "nutzer_id" in query:
             return df[df['nutzer_id'].astype(str) == str(params[0])]
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden von {sheet_name}: {e}")
        return pd.DataFrame()

# DATEN SCHREIBEN (Simuliert SQL-Befehle)
def ausfuehren(query, params=None):
    # Diese Funktion wird aktiv, wenn wir Daten zurückschreiben (z.B. Profil ändern)
    st.info("Speichervorgang gestartet...")
    return True
