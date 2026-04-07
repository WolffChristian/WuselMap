import streamlit as st
import mysql.connector
import pandas as pd
import hashlib

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

def speichere_spielplatz(n, lat, lon, al):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO spielplaetze (standort, lat, lon, altersfreigabe) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(sql, (n, lat, lon, al)); conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def sende_vorschlag(n, ad, al, us):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO vorschlaege (name, adresse, alter_gruppe, eingereicht_von) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (n, ad, al, us)); conn.commit(); conn.close()

def sende_feedback(us, ms):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO feedback (nutzername, nachricht) VALUES (%s, %s)"
    cursor.execute(sql, (us, ms)); conn.commit(); conn.close()
