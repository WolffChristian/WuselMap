import mysql.connector
import streamlit as st
from datetime import date

# 1. Verbindung zur Datenbank herstellen
def get_db_connection():
    return mysql.connector.connect(
        host=st.secrets["tidb"]["host"],
        port=st.secrets["tidb"]["port"],
        user=st.secrets["tidb"]["user"],
        password=st.secrets["tidb"]["password"],
        database=st.secrets["tidb"]["database"],
        autocommit=True
    )

# 2. Einen neuen Vorschlag einsenden (Sabrinas Bereich)
def sende_vorschlag(n, ad, al, us, bund, plz, stadt, bild_base64, hat_wc):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Der SQL-Befehl muss exakt so viele Spalten haben wie Werte (%s)
    sql = """INSERT INTO vorschlaege 
             (name, adresse, alter_empf, user_id, bundesland, plz, stadt, bild_data, hat_wc) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    values = (n, ad, al, us, bund, plz, stadt, bild_base64, hat_wc)
    
    try:
        cursor.execute(sql, values)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Datenbank-Fehler beim Senden: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# 3. Alle Spielplätze für die Karte/Liste laden
def get_all_playgrounds():
    conn = get_db_connection()
    # dictionary=True sorgt dafür, dass wir auf Spalten per Namen r['hat_wc'] zugreifen können
    cursor = conn.cursor(dictionary=True)
    
    sql = "SELECT * FROM spielplaetze"
    
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# 4. Den "Ich bin hier"-Button verarbeiten (Datum aktualisieren)
def bestaetige_spot(spot_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Setzt das Feld zuletzt_bestaetigt auf das heutige Datum
    sql = "UPDATE spielplaetze SET zuletzt_bestaetigt = CURDATE() WHERE id = %s"
    
    try:
        cursor.execute(sql, (spot_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Fehler bei der Bestätigung: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# 5. (Optional für später) Einen Vorschlag vom Admin freischalten
def vorschlag_freischalten(vorschlag_id):
    # Hier würde die Logik rein, um Daten von 'vorschlaege' nach 'spielplaetze' zu kopieren
    pass
