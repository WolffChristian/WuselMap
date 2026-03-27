import mysql.connector
import streamlit as st
import pandas as pd
import hashlib
from PIL import Image
import io

def hash_passwort(passwort):
    return hashlib.sha256(str.encode(passwort)).hexdigest()

def image_optimieren(original_bild_datei, max_width=1000, quality=80):
    """Verkleinert Bilder und wandelt sie in das platzsparende WebP-Format um."""
    try:
        img = Image.open(original_bild_datei)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * float(ratio))
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        byte_io = io.BytesIO()
        img.save(byte_io, format='WEBP', quality=quality)
        return byte_io.getvalue()
    except Exception as e:
        st.error(f"Fehler bei der Bildverarbeitung: {e}")
        return None

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"], user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"], port=int(st.secrets["DB_PORT"]),
            database=st.secrets["DB_NAME"], ssl_disabled=False 
        )
    except Exception as e:
        st.error(f"Datenbank-Fehler: {e}")
        return None

def hole_df(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Ladefehler: {e}")
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
            st.error(f"Speicherfehler: {e}")
            return False
    return False
