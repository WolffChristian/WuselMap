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
    if bild_file is None: return None
    img = Image.open(bild_file)
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=75)
    return base64.b64encode(buffer.getvalue()).decode()

def hole_df(query, params=None):
    conn = get_conn()
    sheet_name = "spielplaetze"
    if "FROM nutzer" in query: sheet_name = "nutzer"
    elif "FROM vorschlaege" in query: sheet_name = "vorschlaege"
    
    try:
        df = conn.read(worksheet=sheet_name, ttl="0s")
        # Spaltennamen harmonisieren (Groß/Klein ignorieren)
        df.columns = [c.strip() for c in df.columns]
        if 'Lon' in df.columns: df = df.rename(columns={'Lon': 'lon'})
        if 'Lat' in df.columns: df = df.rename(columns={'Lat': 'lat'})
        return df
    except Exception as e:
        st.error(f"Daten-Fehler: {e}")
        return pd.DataFrame()

def ausfuehren(query, params=None):
    return True
