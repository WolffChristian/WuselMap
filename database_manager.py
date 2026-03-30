import streamlit as st
from supabase import create_client, Client
import pandas as pd
import hashlib
from PIL import Image
import io
import base64

# 1. Verbindung zu Supabase
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# 2. Passwort-Verschlüsselung (für den Login)
def hash_passwort(passwort):
    return hashlib.sha256(str.encode(passwort)).hexdigest()

# 3. Bild-Optimierung (für spätere Uploads)
def image_optimieren(bild_file):
    if bild_file is None: return None
    img = Image.open(bild_file)
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=75)
    return base64.b64encode(buffer.getvalue()).decode()

# 4. Daten laden (Der neue Supabase-Motor)
def hole_df(query_or_table):
    supabase = get_supabase()
    # Wir prüfen, ob eine SQL-ähnliche Query oder nur der Tabellenname kommt
    tabelle = "spielplaetze"
    if "nutzer" in query_or_table.lower(): tabelle = "nutzer"
    elif "vorschlaege" in query_or_table.lower(): tabelle = "vorschlaege"
    
    try:
        response = supabase.table(tabelle).select("*").execute()
        df = pd.DataFrame(response.data)
        
        # Spaltennamen für die Karte vorbereiten
        if not df.empty:
            df.columns = [c.lower() for c in df.columns]
            if 'standort' in df.columns: df = df.rename(columns={'standort': 'Standort'})
        return df
    except Exception as e:
        st.error(f"Supabase Fehler: {e}")
        return pd.DataFrame()

# 5. Daten ausführen/schreiben (Platzhalter für später)
def ausfuehren(query, params=None):
    # Hier bauen wir später die Schreib-Logik für Supabase ein
    return True
