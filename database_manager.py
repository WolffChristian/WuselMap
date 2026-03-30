import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import hashlib
from PIL import Image
import io
import base64

# Verbindung aufbauen (Der neue GSheets Motor)
def get_conn():
    return st.connection("gsheets", type=GSheetsConnection)

# Passwort-Verschlüsselung (Dein Original)
def hash_passwort(passwort):
    return hashlib.sha256(str.encode(passwort)).hexdigest()

# Bilder für den Upload verkleinern (Dein Original)
def image_optimieren(bild_file):
    img = Image.open(bild_file)
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=70)
    return base64.b64encode(buffer.getvalue()).decode()

# DATEN LADEN (Dein Original-Befehl)
def hole_df(query, params=None):
    conn = get_conn()
    # Wir finden heraus, welcher Reiter gemeint ist
    sheet_name = "spielplaetze"
    if "FROM nutzer" in query: sheet_name = "nutzer"
    elif "FROM vorschlaege" in query: sheet_name = "vorschlaege"
    elif "FROM feedback" in query: sheet_name = "feedback"
    
    try:
        # Versuch den Reiter zu laden
        df = conn.read(worksheet=sheet_name, ttl="0s")
        # Falls die Tabelle 'Lon' (groß) hat, machen wir es für Plotly klein
        if 'Lon' in df.columns:
            df = df.rename(columns={'Lon': 'lon'})
        return df
    except Exception as e:
        # Fallback falls Reiter nicht gefunden wird (damit Design nicht crashed)
        return pd.DataFrame()

# DATEN SCHREIBEN (Simuliert SQL INSERT/UPDATE)
def ausfuehren(query, params=None):
    # Die echte Speicherlogik für GSheets kommt, sobald die Karte läuft
    return True
