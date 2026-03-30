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

# NUTZER-PASSWORT HASHER
def hash_passwort(passwort):
    return hashlib.sha256(str.encode(passwort)).hexdigest()

# BILD-OPTIMIERUNG (für deine Uploads)
def image_optimieren(bild_file):
    img = Image.open(bild_file)
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=70)
    return base64.b64encode(buffer.getvalue()).decode()

# DER ÜBERSETZER FÜR DEINEN CODE
def hole_df(query, params=None):
    conn = get_conn()
    # Wir schauen, welcher Reiter in deinem Code angefragt wird
    sheet_name = "spielplaetze"
    if "FROM nutzer" in query: sheet_name = "nutzer"
    elif "FROM vorschlaege" in query: sheet_name = "vorschlaege"
    elif "FROM feedback" in query: sheet_name = "feedback"
    
    df = conn.read(worksheet=sheet_name, ttl="0s")
    
    # Falls du nach einem speziellen Nutzer suchst (Login)
    if params and "nutzer_id" in query:
        return df[df['nutzer_id'].astype(str) == str(params[0])]
    return df

def ausfuehren(query, params=None):
    # Diese Funktion sorgt dafür, dass deine Schreib-Befehle nicht crashen
    # Die echte Speicherlogik für GSheets bauen wir ein, wenn das Design steht!
    st.info("Daten-Operation erfolgreich simuliert.")
    return True
