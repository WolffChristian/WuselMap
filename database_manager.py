import mysql.connector
import streamlit as st

def get_db_connection():
    return mysql.connector.connect(
        host=st.secrets["tidb"]["host"],
        port=st.secrets["tidb"]["port"],
        user=st.secrets["tidb"]["user"],
        password=st.secrets["tidb"]["password"],
        database=st.secrets["tidb"]["database"],
        autocommit=True
    )

def sende_vorschlag(n, ad, al, us, bund, plz, stadt, bild_base64, hat_wc):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Wir listen die Spalten EXAKT auf
    sql = """INSERT INTO vorschlaege 
             (name, adresse, alter_empf, user_id, bundesland, plz, stadt, bild_data, hat_wc) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    # Wir bauen das Tuple EXAKT mit 9 Werten
    values = (str(n), str(ad), str(al), str(us), str(bund), str(plz), str(stadt), bild_base64, bool(hat_wc))
    
    try:
        cursor.execute(sql, values)
        return True
    except Exception as e:
        # Das gibt uns die ECHTE Fehlermeldung im Streamlit aus
        st.error(f"🚨 SQL-Fehler: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_all_playgrounds():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM spielplaetze")
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def bestaetige_spot(spot_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE spielplaetze SET zuletzt_bestaetigt = CURDATE() WHERE id = %s", (spot_id,))
        return True
    except Exception as e:
        st.error(f"Fehler beim Bestätigen: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
