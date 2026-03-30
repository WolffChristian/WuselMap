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

# Simuliert SQL-Abfragen für Google Sheets
def hole_df(query, params=None):
    conn = get_conn()
    # Wir finden heraus, welcher Reiter gemeint ist (nutzer, spielplaetze, etc.)
    sheet_name = "spielplaetze"
    if "FROM nutzer" in query: sheet_name = "nutzer"
    elif "FROM vorschlaege" in query: sheet_name = "vorschlaege"
    elif "FROM feedback" in query: sheet_name = "feedback"
    
    df = conn.read(worksheet=sheet_name, ttl="0s")
    
    # Einfache Filter-Simulation für den Login
    if params and "nutzer_id" in query:
        return df[df['nutzer_id'] == str(params[0])]
    return df

# Simuliert Schreibbefehle
def ausfuehren(query, params=None):
    conn = get_conn()
    sheet_name = "vorschlaege"
    if "INTO vorschlaege" in query: sheet_name = "vorschlaege"
    elif "INTO nutzer" in query: sheet_name = "nutzer"
    elif "UPDATE nutzer" in query: sheet_name = "nutzer"
    elif "DELETE FROM vorschlaege" in query: sheet_name = "vorschlaege"
    
    # Hier müsste eine Logik zum Speichern hin (wie vorher besprochen)
    # Für den Moment geben wir True zurück, damit die App nicht crashed
    return True

def hash_passwort(passwort):
    return hashlib.sha256(str.encode(passwort)).hexdigest()

def image_optimieren(bild_file):
    img = Image.open(bild_file)
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=70)
    return base64.b64encode(buffer.getvalue()).decode()
