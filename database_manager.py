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
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        img.thumbnail((800, 800))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=70)
        return base64.b64encode(buffer.getvalue()).decode()
    except: return None

def hole_df(tabelle="spielplaetze"):
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        df = pd.read_sql(f"SELECT * FROM {tabelle}", conn)
        if not df.empty:
            df.columns = [c.lower() for c in df.columns]
            if 'standort' in df.columns: 
                df = df.rename(columns={'standort': 'Standort'})
        return df
    finally: conn.close()

# --- NUTZER FUNKTIONEN ---

def registriere_nutzer(un, pw, em, vn, nn, al, agb):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, alter_jahre, agb_akzeptiert, rolle) VALUES (%s,%s,%s,%s,%s,%s,%s,'user')"
    try:
        cursor.execute(sql, (un.strip().lower(), hash_passwort(pw), em.strip(), vn, nn, al, agb))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def aktualisiere_profil(un, em, vn, nn, al, emo):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "UPDATE nutzer SET email=%s, vorname=%s, nachname=%s, alter_jahre=%s, profil_emoji=%s WHERE benutzername=%s"
    try:
        cursor.execute(sql, (em.strip(), vn, nn, al, emo, un))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def sende_vorschlag(n, ad, al, us, bund, plz, stadt, bild, ds):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO vorschlaege (standort, adresse, altersfreigabe, bundesland, plz, stadt, bild_data, foto_datenschutz) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        cursor.execute(sql, (n, ad, al, bund, plz, stadt, bild, ds))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def sende_feedback(us, ms):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO feedback (nutzername, nachricht) VALUES (%s, %s)"
    try:
        cursor.execute(sql, (us, ms)); conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

# --- ADMIN FUNKTIONEN (Wieder hergestellt) ---

def speichere_spielplatz(n, lat, lon, al, bund, plz, stadt, bild, ds):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = """INSERT INTO spielplaetze 
             (standort, lat, lon, altersfreigabe, bundesland, plz, stadt, bild_data, foto_datenschutz) 
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    try:
        cursor.execute(sql, (n, lat, lon, al, bund, plz, stadt, bild, ds))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def loesche_vorschlag(v_id):
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM vorschlaege WHERE id = %s", (v_id,))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def loesche_feedback(f_id):
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM feedback WHERE id = %s", (f_id,))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

# --- MESSAGING & CREW LOGIK ---

def sende_nachricht(von, an, text):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO nachrichten (von_nutzer, an_nutzer, nachricht) VALUES (%s, %s, %s)"
    try:
        cursor.execute(sql, (von, an, text))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def hole_nachrichten(nutzername):
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        return pd.read_sql(f"SELECT * FROM nachrichten WHERE an_nutzer = '{nutzername}' ORDER BY zeitpunkt DESC", conn)
    finally: conn.close()

def fuege_freund_hinzu(nutzer, freund_name):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT IGNORE INTO freunde (nutzer, freund, status) VALUES (%s, %s, 'offen')"
    try:
        cursor.execute(sql, (nutzer, freund_name))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def hole_freundesliste(nutzer):
    conn = get_db_connection()
    if conn is None: return []
    try:
        df = pd.read_sql(f"SELECT freund FROM freunde WHERE nutzer = '{nutzer}' AND status = 'bestätigt'", conn)
        return df['freund'].tolist() if not df.empty else []
    finally: conn.close()

def hole_crew_anfragen(nutzername):
    conn = get_db_connection()
    if conn is None: return []
    try:
        df = pd.read_sql(f"SELECT nutzer FROM freunde WHERE freund = '{nutzername}' AND status = 'offen'", conn)
        return df['nutzer'].tolist() if not df.empty else []
    finally: conn.close()

def bestaetige_anfrage(absender, ich):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        # 1. Den Eintrag, den der andere erstellt hat, auf bestätigt setzen
        cursor.execute("UPDATE freunde SET status = 'bestätigt' WHERE nutzer = %s AND freund = %s", (absender, ich))
        # 2. Den Gegeneintrag für dich erstellen
        cursor.execute("INSERT IGNORE INTO freunde (nutzer, freund, status) VALUES (%s, %s, 'bestätigt')", (ich, absender))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"SQL-Fehler beim Bestätigen: {e}") # Das zeigt uns jetzt genau, was fehlt!
        return False
    finally: cursor.close(); conn.close()

def lehne_anfrage_ab(absender, ich):
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM freunde WHERE nutzer = %s AND freund = %s", (absender, ich))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()
