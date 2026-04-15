import streamlit as st
import mysql.connector
import pandas as pd
import hashlib
from PIL import Image
import io
import base64

# --- GRUNDFUNKTIONEN ---

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
        st.error(f"Datenbank-Verbindung fehlgeschlagen: {e}")
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
    except Exception as e: 
        st.error(f"Bildoptimierung fehlgeschlagen: {e}")
        return None

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
    except Exception as e:
        st.error(f"Fehler beim Laden der Tabelle {tabelle}: {e}")
        return pd.DataFrame()
    finally: conn.close()

# --- NUTZER FUNKTIONEN ---

def registriere_nutzer(un, pw, em, vn, nn, al, agb):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    sql = "INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, alter_jahre, agb_akzeptiert, rolle) VALUES (%s,%s,%s,%s,%s,%s,%s,'user')"
    try:
        cursor.execute(sql, (un.strip().lower(), hash_passwort(pw), em.strip(), vn, nn, al, agb))
        conn.commit(); return True
    except Exception as e:
        st.error(f"Registrierung fehlgeschlagen: {e}")
        return False
    finally: cursor.close(); conn.close()

def aktualisiere_profil(un, em, vn, nn, al, emo):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    sql = "UPDATE nutzer SET email=%s, vorname=%s, nachname=%s, alter_jahre=%s, profil_emoji=%s WHERE benutzername=%s"
    try:
        cursor.execute(sql, (em.strip(), vn, nn, al, emo, un))
        conn.commit(); return True
    except Exception as e:
        st.error(f"Profil-Update fehlgeschlagen: {e}")
        return False
    finally: cursor.close(); conn.close()

# --- VORSCHLÄGE & FOTOS ---

def sende_vorschlag(n, ad, al, us, bund, plz, stadt, bild, ds, ausst="", sch=0, sitz=0, wc=0, lat=None, lon=None):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    sql = """INSERT INTO vorschlaege (standort, adresse, altersfreigabe, bundesland, plz, stadt, bild_data, foto_datenschutz, ausstattung, hat_schatten, hat_sitze, hat_wc, status, lat, lon) 
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, 'neu', %s, %s)"""
    try:
        # Falls lat/lon None sind, werden sie als NULL in SQL gespeichert
        cursor.execute(sql, (n, ad, al, bund, plz, stadt, bild, ds, ausst, sch, sitz, wc, lat, lon))
        conn.commit(); return True
    except Exception as e:
        st.error(f"SQL-Fehler beim Vorschlag: {e}")
        return False
    finally: cursor.close(); conn.close()

def aktualisiere_spielplatz_foto(spielplatz_id, bild_data):
    """Ermöglicht das Nachreichen eines Fotos für einen bestehenden Platz"""
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    # Wir setzen das Bild direkt in die spielplaetze Tabelle
    sql = "UPDATE spielplaetze SET bild_data = %s WHERE id = %s"
    try:
        cursor.execute(sql, (bild_data, spielplatz_id))
        conn.commit(); return True
    except Exception as e:
        st.error(f"Foto-Update fehlgeschlagen: {e}")
        return False
    finally: cursor.close(); conn.close()

def sende_feedback(us, ms):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    sql = "INSERT INTO feedback (nutzername, nachricht) VALUES (%s, %s)"
    try:
        cursor.execute(sql, (us, ms)); conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

# --- ADMIN & STATUS FUNKTIONEN ---

def speichere_spielplatz(n, lat, lon, al, bund, plz, stadt, bild, ds, ausst="", sch=0, sitz=0, wc=0):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = """INSERT INTO spielplaetze 
             (standort, lat, lon, altersfreigabe, bundesland, plz, stadt, bild_data, foto_datenschutz, ausstattung, hat_schatten, hat_sitze, hat_wc, status) 
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, 'aktiv')"""
    try:
        cursor.execute(sql, (n, lat, lon, al, bund, plz, stadt, bild, ds, ausst, sch, sitz, wc))
        conn.commit(); return True
    except Exception as e:
        st.error(f"Fehler beim Speichern des Spielplatzes: {e}")
        return False
    finally: cursor.close(); conn.close()

def loesche_spielplatz(s_id):
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM spielplaetze WHERE id = %s", (s_id,))
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

def loesche_oeffentliche_nachrichten():
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM nachrichten WHERE is_private = FALSE")
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def setze_spot_status(spot_id, neuer_status):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE spielplaetze SET status = %s WHERE id = %s", (neuer_status, spot_id))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

# --- MESSAGING & CREW LOGIK ---

def sende_nachricht(von, an, text, is_private=False, spot_name='Allgemein'):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO nachrichten (von_nutzer, recipient_id, nachricht, is_private, spot_name) VALUES (%s, %s, %s, %s, %s)"
    try:
        cursor.execute(sql, (von, an, text, is_private, spot_name))
        conn.commit(); return True
    except Exception as e:
        st.error(f"Fehler beim Senden: {e}")
        return False
    finally: cursor.close(); conn.close()

def hole_nachrichten(nutzername, nur_privat=False):
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        if nur_privat:
            sql = f"SELECT * FROM nachrichten WHERE is_private = TRUE AND (recipient_id = '{nutzername}' OR von_nutzer = '{nutzername}') ORDER BY zeitpunkt DESC"
        else:
            sql = "SELECT * FROM nachrichten WHERE is_private = FALSE ORDER BY zeitpunkt DESC"
        return pd.read_sql(sql, conn)
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
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("UPDATE freunde SET status = 'bestätigt' WHERE nutzer = %s AND freund = %s", (absender, ich))
        cursor.execute("INSERT IGNORE INTO freunde (nutzer, freund, status) VALUES (%s, %s, 'bestätigt')", (ich, absender))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def lehne_anfrage_ab(absender, ich):
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM freunde WHERE nutzer = %s AND freund = %s", (absender, ich))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()