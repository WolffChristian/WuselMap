import streamlit as st
from supabase import create_client, Client
import pandas as pd

def get_supabase() -> Client:
    # Holt sich die Daten direkt aus den Streamlit Secrets
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def hole_df(tabelle_name="spielplaetze"):
    supabase = get_supabase()
    try:
        # Die Abfrage an den Supabase-Tresor
        response = supabase.table(tabelle_name).select("*").execute()
        df = pd.DataFrame(response.data)
        
        # Falls die Tabelle leer ist, geben wir ein leeres Gerüst zurück
        if df.empty:
            return pd.DataFrame(columns=['standort', 'lat', 'lon', 'altersfreigabe'])
            
        return df
    except Exception as e:
        st.error(f"⚠️ Verbindung zu Supabase fehlgeschlagen: {e}")
        return pd.DataFrame()
