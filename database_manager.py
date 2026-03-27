import mysql.connector
import streamlit as st
import pandas as pd
import hashlib

def hash_passwort(passwort):
    """Verschlüsselt das Passwort sicher."""
    return hashlib.sha256(str.encode(passwort)).hexdigest()

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
        st.error(f"Datenbank-Verbindung fehlgeschlagen: {e}")
        return None

def hole_df(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Fehler beim Laden: {e}")
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
