import streamlit as st
import mysql.connector
import pandas as pd
import hashlib

def get_db_connection():
    """Stellt die Verbindung zu TiDB Cloud her."""
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
        st.error(f"Datenbank-Verbindung fehlgeschlagen: {e}")
        return None

def hash_passwort(passwort):
    """Verschlüsselt Passwörter sicher per SHA-256."""
    return hashlib.sha256(str.encode(passwort)).hexdigest()

def hole_df(tabelle="spielplaetze"):
    """Lädt Daten aus der MySQL-Datenbank."""
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        df = pd.read_sql(f"SELECT * FROM {tabelle}", conn)
        if not df.empty:
            df.columns = [c.lower() for c in df.columns]
            if 'standort' in df.columns:
                df = df.rename(columns={'standort': 'Standort'})
        return df
    finally:
        conn.close()

def registriere_nutzer(username, pw, email, vorname, nachname, alter, agb):
    """Speichert einen neuen Nutzer inkl. AGB-Status."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    sql = """INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, alter_jahre, agb_akzeptiert) 
             VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    try:
        cursor.execute(sql, (username, hash_passwort(pw), email, vorname, nachname, alter, agb))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Registrierungsfehler: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def speichere_spielplatz(name, lat, lon, alter):
    """Speichert einen neuen Spot in der Datenbank."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    sql = "INSERT INTO spielplaetze (standort, lat, lon, altersfreigabe) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(sql, (name, lat, lon, alter))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Speicherfehler: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
