import streamlit as st
import mysql.connector
import pandas as pd
import hashlib

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            port=st.secrets["DB_PORT"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            ssl_verify_cert=True
        )
    except Exception as e:
        st.error(f"Datenbank-Fehler: {e}")
        return None

def hash_passwort(passwort):
    return hashlib.sha256(str.encode(passwort)).hexdigest()

def hole_df(tabelle="spielplaetze"):
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        df = pd.read_sql(f"SELECT * FROM {tabelle}", conn)
        if not df.empty:
            df.columns = [c.lower() for c in df.columns]
            if 'standort' in df.columns: df = df.rename(columns={'standort': 'Standort'})
        return df
    finally:
        conn.close()

def registriere_nutzer(username, pw, email, vorname, nachname, alter, agb):
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    sql = """INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, alter_jahre, agb_akzeptiert, rolle) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, 'user')"""
    try:
        cursor.execute(sql, (username, hash_passwort(pw), email, vorname, nachname, alter, agb))
        conn.commit()
        return True
    except: return False
    finally:
        cursor.close(); conn.close()

def speichere_spielplatz(name, lat, lon, alter):
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    sql = "INSERT INTO spielplaetze (standort, lat, lon, altersfreigabe) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(sql, (name, lat, lon, alter))
        conn.commit()
        return True
    finally:
        cursor.close(); conn.close()

def sende_vorschlag(name, adr, alter, user):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO vorschlaege (name, adresse, alter_gruppe, eingereicht_von) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (name, adr, alter, user))
    conn.commit()
    conn.close()

def sende_feedback(user, msg):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO feedback (nutzername, nachricht) VALUES (%s, %s)"
    cursor.execute(sql, (user, msg))
    conn.commit()
    conn.close()

# --- NEU: PASSWORT VERGESSEN FUNKTIONEN ---
def check_user_mail_match(u, m):
    """Prüft ob Nutzername und E-Mail in der DB zusammengehören."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM nutzer WHERE benutzername = %s AND email = %s", (u, m))
    res = cursor.fetchone()
    conn.close()
    return res is not None

def update_passwort(u, neu_pw):
    """Speichert das neue gehashte Passwort."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    sql = "UPDATE nutzer SET passwort = %s WHERE benutzername = %s"
    cursor.execute(sql, (hash_passwort(neu_pw), u))
    conn.commit()
    conn.close()
    return True
