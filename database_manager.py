import mysql.connector
import streamlit as st
import pandas as pd
import hashlib
from PIL import Image # Pillow für Bildverarbeitung
import io

def hash_passwort(passwort):
    """Verschlüsselt das Passwort unwiderruflich."""
    return hashlib.sha256(str.encode(passwort)).hexdigest()

def image_optimieren(original_bild_datei, max_width=1000, quality=80):
    """
    Nimmt ein Bild, ändert die Größe (falls nötig) und speichert es
    als optimiertes WebP-Format.
    """
    # 1. Bild mit Pillow öffnen
    img = Image.open(original_bild_datei)
    
    # 2. Transparente PNGs für WebP vorbereiten (falls nötig)
    if img.mode == 'RGBA':
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background

    # 3. Größe anpassen (falls Bild breiter als max_width ist)
    if img.width > max_width:
        height = int((max_width / img.width) * img.height)
        img = img.resize((max_width, height), Image.Resampling.LANCZOS)
    
    # 4. Bild als binäre Daten im WebP-Format speichern
    byte_io = io.BytesIO()
    # WebP ist sehr effizient und klein
    img.save(byte_io, format='WEBP', quality=quality)
    optimized_bild_data = byte_io.getvalue()
    
    return optimized_bild_data

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            port=int(st.secrets["DB_PORT"]),
            database=st.secrets["DB_NAME"],
            ssl_disabled=False 
        )
    except Exception as e:
        st.error(f"Datenbank-Verbindungsfehler: {e}")
        return None

def hole_df(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Abfragefehler: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def ausfuehren(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Fehler beim Speichern: {e}")
            return False
    return False
