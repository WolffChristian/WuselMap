import streamlit as st
import mysql.connector
import pandas as pd
import hashlib
from PIL import Image
import io
import base64

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"], port=st.secrets["DB_PORT"],
            user=st.secrets["DB_USER"], password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"], ssl_verify_cert=True
        )
    except Exception as e:
        st.error(f"Datenbank-Fehler: {e}"); return None

def hash_passwort(pw):
    return hashlib.sha256(str.encode(pw.strip())).hexdigest()

# --- NEU: BILD-OPTIMIERUNG ---
def optimiere_bild(bild_file):
    """Verkleinert das Bild und wandelt es in Base64-Text um."""
    if bild_file is None: return None
    img = Image.open(bild_file)
    img.thumbnail((800, 800)) # Maximal 800px Breite/Höhe
    
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=70) # 70% Qualität reicht völlig aus
    return base64.b64encode(buffer.getvalue()).decode()

# --- NEU: DUPLIKAT-CHECK ---
def check_duplikat(tabelle, name, plz):
    """Prüft, ob ein Eintrag mit gleichem Namen und PLZ schon existiert."""
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = f"SELECT id FROM {tabelle} WHERE standort = %s AND plz = %s" if tabelle == "spielplaetze" else f"SELECT id FROM {tabelle} WHERE name = %s AND plz = %s"
    cursor.execute(sql, (name, plz))
    res = cursor.fetchone()
    conn.close()
    return res is not None

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
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, alter_jahre, agb_akzeptiert, rolle) VALUES (%s,%s,%s,%s,%s,%s,%s,'user')"
    try:
        cursor.execute(sql, (un.strip(), hash_passwort(pw), em.strip(), vn, nn, al, agb))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def speichere_spielplatz(n, lat, lon, al, bund, plz, stadt, bild):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO spielplaetze (standort, lat, lon, altersfreigabe, bundesland, plz, stadt, bild_data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    try:
        cursor.execute(sql, (n, lat, lon, al, bund, plz, stadt, bild))
        conn.commit(); return True
    except Exception as e: print(e); return False
    finally: cursor.close(); conn.close()

def sende_vorschlag(n, ad, al, us, bund, plz, stadt, bild):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO vorschlaege (name, adresse, alter_gruppe, eingereicht_von, bundesland, plz, stadt, bild_data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (n, ad, al, us, bund, plz, stadt, bild))
    conn.commit(); conn.close()

def sende_feedback(us, ms):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO feedback (nutzername, nachricht) VALUES (%s, %s)"
    cursor.execute(sql, (us, ms)); conn.commit(); conn.close()
