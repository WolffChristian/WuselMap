import mysql.connector
import streamlit as st

def get_db_connection():
    # WICHTIG: Prüfe in Streamlit Cloud, ob deine Secrets [tidb] heißen!
    conf = st.secrets["tidb"]
    return mysql.connector.connect(
        host=conf["host"],
        port=conf["port"],
        user=conf["user"],
        password=conf["password"],
        database=conf["database"],
        autocommit=True
    )

def get_all_playgrounds():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM spielplaetze")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def sende_vorschlag(n, ad, al, us, bund, plz, stadt, bild_b64, wc):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """INSERT INTO vorschlaege 
             (name, adresse, alter_empf, user_id, bundesland, plz, stadt, bild_data, hat_wc) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = (n, ad, al, us, bund, plz, stadt, bild_b64, wc)
    try:
        cursor.execute(sql, values)
        return True
    except Exception as e:
        st.error(f"Fehler: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def bestaetige_spot(spot_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE spielplaetze SET zuletzt_bestaetigt = CURDATE() WHERE id = %s", (spot_id,))
        return True
    finally:
        cursor.close()
        conn.close()
