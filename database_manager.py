import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import hashlib
from PIL import Image
import io
import base64

def get_conn():
    return st.connection("gsheets", type=GSheetsConnection)

def hash_passwort(passwort):
    return hashlib.sha256(str.encode(passwort)).hexdigest()

def image_optimieren(bild_file):
    img = Image.open(bild_file)
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=70)
    return base64.b64encode(buffer.getvalue()).decode()

def hole_df(query, params=None):
    conn = get_conn()
    
    # Welchen Reiter suchen wir?
    sheet_name = "spielplaetze"
    if "FROM nutzer" in query: sheet_name = "nutzer"
    elif "FROM vorschlaege" in query: sheet_name = "vorschlaege"
    elif "FROM feedback" in query: sheet_name = "feedback"
    
    try:
        # Versuch den Reiter zu laden
        df = conn.read(worksheet=sheet_name, ttl="0s")
        if 'Lon' in df.columns:
            df = df.rename(columns={'Lon': 'lon'})
        return df
    except Exception as e:
        st.error(f"❌ Google Sheets Fehler (400): Der Reiter '{sheet_name}' wurde nicht erkannt.")
        st.info("💡 Tipp: Prüfe, ob der Reiter in Google Sheets exakt so heißt (keine Leerzeichen!).")
        
        # Diagnose: Was sieht die App überhaupt?
        try:
            test_df = conn.read(ttl="0s")
            st.warning(f"Gefundene Spalten im ersten Reiter: {test_df.columns.tolist()}")
        except:
            st.error("Die Verbindung zur Tabelle ist komplett unterbrochen. Prüfe den Link in den Secrets.")
        
        return pd.DataFrame()

def ausfuehren(query, params=None):
    st.info("Daten-Operation wird verarbeitet...")
    return True
