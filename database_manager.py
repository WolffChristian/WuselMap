import streamlit as st
import mysql.connector
import pandas as pd
import hashlib
from PIL import Image
import io
import base64

# 1. Verbindung zu TiDB Cloud herstellen
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            port=st.secrets["DB_PORT"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            ssl_verify_cert=True  # TiDB benötigt oft SSL
        )
        return conn
    except Exception as e:
        st.error(f"❌ Datenbank-Verbindung fehlgeschlagen: {e}")
        return None

# 2. Daten laden (für Karte, Login oder Vorschläge)
def hole_df(tabelle="spielplaetze"):
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    
    try:
        query = f"SELECT * FROM {tabelle}"
        df = pd.read_sql(query, conn)
        
        # Spaltennamen für die App vereinheitlichen
        if not df.empty:
            df.columns = [c.lower() for c in df.columns]
            if 'standort' in df.columns:
                df = df.rename(columns={'standort': 'Standort'})
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden von {tabelle}: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# 3. Neuen Spielplatz speichern
def speichere_spielplatz(name, lat, lon, alter):
    conn = get_db_connection()
    if conn is None: return False
    
    cursor = conn.cursor()
    sql = "INSERT INTO spielplaetze (standort, lat, lon, altersfreigabe) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(sql, (name, lat, lon, alter))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# 4. Hilfsfunktionen (Passwort & Bilder)
def hash_passwort(passwort):
    return hashlib.sha256(str.encode(passwort)).hexdigest()

def image_optimieren(bild_file):
    if bild_file is None: return None
    img = Image.open(bild_file)
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=75)
    return base64.b64encode(buffer.getvalue()).decode()
