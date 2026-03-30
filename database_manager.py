import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import hashlib
from PIL import Image
import io
import base64

# Verbindung aufbauen
def get_conn():
    return st.connection("gsheets", type=GSheetsConnection)

# Passwort-Verschlüsselung
def hash_passwort(passwort):
    return hashlib.sha256(str.encode(passwort)).hexdigest()

# Bilder für den Upload verkleinern
def image_optimieren(bild_file):
    img = Image.open(bild_file)
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=70)
    return base64.b64encode(buffer.getvalue()).decode()

# DATEN LADEN (Dein gewohnter Befehl)
def hole_df(query, params=None):
    conn = get_conn()
    # Wir finden heraus, welcher Reiter gemeint ist
    sheet_name = "spielplaetze"
    if "FROM nutzer" in query: sheet_name = "nutzer"
    elif "FROM vorschlaege" in query: sheet_name = "vorschlaege"
    elif "FROM feedback" in query: sheet_name = "feedback"
    
    try:
        df = conn.read(worksheet=sheet_name, ttl="0s")
        # Falls die Tabelle 'Lon' (groß) hat, machen wir es für Plotly klein
        if 'Lon' in df.columns:
            df = df.rename(columns={'Lon': 'lon'})
        return df
    except Exception as e:
        st.error(f"Fehler beim Zugriff auf Reiter '{sheet_name}': {e}")
        return pd.DataFrame()

# DATEN SCHREIBEN (Simuliert SQL INSERT/UPDATE)
def ausfuehren(query, params=None):
    conn = get_conn()
    sheet_name = "vorschlaege"
    if "INTO vorschlaege" in query: sheet_name = "vorschlaege"
    elif "INTO nutzer" in query: sheet_name = "nutzer"
    elif "UPDATE nutzer" in query: sheet_name = "nutzer"
    
    try:
        # Bestehende Daten holen
        df_alt = conn.read(worksheet=sheet_name, ttl="0s")
        
        # Hier müsste eine Logik hin, die die params in ein dict umwandelt 
        # und mit pd.concat an df_alt anhängt. 
        # Da wir erst mal das Design fixen wollen, lassen wir die App hier 'True' melden.
        st.success("Daten wurden (simuliert) gespeichert!")
        return True
    except:
        return False
