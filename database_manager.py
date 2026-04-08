import streamlit as st
import mysql.connector
import pandas as pd
import hashlib
from PIL import Image
import io
import base64

def get_db_connection():
    try:
        # Nutzt deine Secrets: DB_HOST, DB_PORT, etc.
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            port=st.secrets["DB_PORT"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            ssl_verify_cert=False, 
            use_pure=True
        )
    except Exception as e:
        st.error(f"Datenbank-Fehler: {e}")
        return None

def hash_passwort(pw):
    return hashlib.sha256(str.encode(pw.strip())).hexdigest()

def optimiere_bild(bild_file):
    if bild_file is None: return None
    try:
        img = Image.open(bild_file)
        # Konvertiert zu RGB (falls es PNG mit Transparenz ist)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail((800, 800))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=70)
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        st.error(f"Bildfehler: {e}")
        return None

def hole_df(tabelle="spielplaetze"):
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        df = pd.read_sql(f"SELECT * FROM {tabelle}", conn)
        if not df.empty:
            df.columns = [c.lower() for c in df.columns]
            if 'standort' in df.columns: df = df.rename(columns={'standort': 'Standort'})
        return df
    finally: conn.close()

def registriere_nutzer(un, pw, em, vn, nn, al, agb):
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    sql = "INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, alter_jahre, agb_akzeptiert, rolle) VALUES (%s,%s,%s,%s,%s,%s,%s,'user')"
    try:
        cursor.execute(sql, (un.strip(), hash_passwort(pw), em.strip(), vn, nn, al, agb))
        conn.commit()
        return True
    except: return False
    finally: cursor.close(); conn.close()

def speichere_spielplatz(n, lat, lon, al, bund, plz, stadt, bild, ds):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO spielplaetze (standort, lat, lon, altersfreigabe, bundesland, plz, stadt, bild_data, foto_datenschutz) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        cursor.execute(sql, (n, lat, lon, al, bund, plz, stadt, bild, ds))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def sende_vorschlag(n, ad, al, us, bund, plz, stadt, bild, ds):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO vorschlaege (name, adresse, alter_gruppe, eingereicht_von, bundesland, plz, stadt, bild_data, foto_datenschutz) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        cursor.execute(sql, (n, ad, al, us, bund, plz, stadt, bild, ds))
        conn.commit()
        return True
    except: return False
    finally: cursor.close(); conn.close()
