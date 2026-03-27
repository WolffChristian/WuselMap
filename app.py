import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import requests

# Importe aus unseren neuen Dateien
from database_manager import hole_df, ausfuehren, hash_passwort
from auth_manager import login_bereich
from assets_helper import display_sidebar_logo, display_home_banner, display_page_header
from legal import show_legal_page

st.set_page_config(page_title="KletterKompass Varel", layout="wide")

# Hilfsfunktionen für Wetter und Distanz
def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        return requests.get(url, timeout=5).json()['current_weather']
    except: return None

# Session State
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# Sidebar
with st.sidebar:
    display_sidebar_logo()
    if st.button("📍 Suche", width='stretch'): st.session_state.wahl = "📍 Suche"
    if st.button("📄 Rechtliches", width='stretch'): st.session_state.wahl = "📄 Rechtliches"
    st.write("---")
    
    if st.session_state.logged_in:
        if st.button("👤 Profil"): st.session_state.wahl = "👤 Profil"
        if st.button("🏗️ Melden"): st.session_state.wahl = "🏗️ Vorschlag"
        if st.session_state.rolle == "admin":
            if st.button("🛠️ Admin"): st.session_state.wahl = "🛠️ Admin"
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()
    else:
        login_bereich()

# Seitenlogik
if st.session_state.wahl == "📍 Suche":
    display_home_banner()
    st.title("Spielplätze in Varel")
    adr = st.text_input("Adresse", "Varel")
    km = st.slider("Radius (km)", 1, 50, 15)
    if st.button("🔍 Suchen"):
        geocoder = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        res_g = geocoder.geocode(adr + ", Friesland")
        if res_g:
            lat, lon = res_g[0]['geometry']['lat'], res_g[0]['geometry']['lng']
            df = hole_df("SELECT * FROM spielplaetze")
            if not df.empty:
                df['distanz'] = df.apply(lambda r: distanz(lat, lon, r['lat'], r['lon']), axis=1)
                final = df[df['distanz'] <= km].sort_values('distanz')
                st.dataframe(final) # Hier käme wieder die Karte hin

elif st.session_state.wahl == "📄 Rechtliches":
    show_legal_page()

elif st.session_state.wahl == "🛠️ Admin":
    st.title("Admin-Bereich")
    st.write("Nutzer-Liste:")
    st.dataframe(hole_df("SELECT nutzer_id, benutzername, email, rolle FROM nutzer"))
