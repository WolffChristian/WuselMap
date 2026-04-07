import mysql.connector
import streamlit as st

def get_db_connection():
    # Wir nehmen die Namen, die bei dir funktioniert haben!
    # Wenn 'tidb' falsch war, ändere es hier zurück auf deinen alten Namen (z.B. 'mysql')
    db_info = st.secrets["tidb"] 
    return mysql.connector.connect(
        host=db_info["host"],
        port=db_info["port"],
        user=db_info["user"],
        password=db_info["password"],
        database=db_info["database"],
        autocommit=True
    )

def get_all_playgrounds():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM spielplaetze")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def sende_vorschlag(n, ad, al, us, img_b64):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Nur die Basis-Daten, die sicher funktionieren
    sql = "INSERT INTO vorschlaege (name, adresse, alter_empf, user_id, bild_data) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (n, ad, al, us, img_b64))
    conn.commit()
    cursor.close()
    conn.close()
    return True
