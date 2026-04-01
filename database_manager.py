import streamlit as st
import mysql.connector
import pandas as pd
import hashlib
from PIL import Image
import io
import base64

# --- 1. VERBINDUNG AUFBAUEN ---
def get_db_connection():
    """Stellt die Verbindung zur TiDB Cloud her."""
    try:
        conn = mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            port=st.secrets["DB_PORT"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            ssl_verify_cert=True  # TiDB Cloud erfordert meist eine SSL-Verbindung
        )
        return conn
    except Exception as e:
        st.error(f"❌ Datenbank-Verbindung fehlgeschlagen: {e}")
        return None

# --- 2. DATEN LADEN ---
def hole_df(tabelle="spielplaetze"):
    """Lädt Daten aus einer beliebigen Tabelle (Standard: spielplaetze)."""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        # Wir laden alle Spalten der gewünschten Tabelle
        query = f"SELECT * FROM {tabelle}"
        df = pd.read_sql(query, conn)
        
        # Spaltennamen für die App vereinheitlichen (Kleinschreibung zu Großschreibung bei Bedarf)
        if not df.empty:
            df.columns = [c.lower() for c in df.columns]
            if 'standort' in df.columns:
                df = df.rename(columns={'standort': 'Standort'})
        return df
    except Exception as e:
        st.error(f"⚠️ Fehler beim Laden von {tabelle}: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# --- 3. SPIELPLATZ SPEICHERN ---
def speichere_spielplatz(name, lat, lon, alter):
    """Speichert einen neuen Spielplatz in der MySQL-Datenbank."""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    sql = "INSERT INTO spielplaetze (standort, lat, lon, altersfreigabe) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(sql, (name, lat, lon, alter))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"❌ Fehler beim Speichern des Spielplatzes: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# --- 4. NUTZER REGISTRIEREN ---
def registriere_nutzer(name, pw):
    """Legt einen neuen Nutzer mit gehashtem Passwort an."""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    # Passwort sicher verschlüsseln
    pw_hash = hash_passwort(pw)
    
    sql = "INSERT INTO nutzer (benutzername, passwort, rolle) VALUES (%s, %s, %s)"
    try:
        cursor.execute(sql, (name, pw_hash, 'user'))
        conn.commit()
        return True
    except Exception as e:
        # Fehler tritt z.B. auf, wenn der Nutzername schon existiert (Unique Constraint)
        return False
    finally:
        cursor.close()
        conn.close()

# --- 5. HILFSFUNKTIONEN (Sicherheit & Bilder) ---
def hash_passwort(passwort):
    """Verschlüsselt ein Passwort per SHA256."""
    return hashlib.sha256(str.encode(passwort)).hexdigest()

def image_optimieren(bild_file):
    """Komprimiert Bilder für die Datenbank (optional für später)."""
    if bild_file is None:
        return None
    img = Image.open(bild_file)
    # Bild verkleinern
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    # Als JPEG speichern, um Platz zu sparen
    img.save(buffer, format="JPEG", quality=75)
    return base64.b64encode(buffer.getvalue()).decode()

# --- 6. PLATZHALTER FÜR LEGACY-CODE ---
def ausfuehren(query, params=None):
    """Wird für manuelle SQL-Befehle genutzt (falls benötigt)."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Fehler beim Ausführen: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
