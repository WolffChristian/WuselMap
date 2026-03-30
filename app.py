import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import requests

# Deine Helfer (database_manager ist jetzt repariert)
from database_manager import hole_df, ausfuehren, image_optimieren, hash_passwort

# Versuche deine Original Zusatz-Dateien zu laden
try:
    from auth_manager import login_bereich
    # Wir benutzen asset_helper nicht mehr, wir laden die Bilder direkt!
    # from assets_helper import display_sidebar_logo, display_home_banner, display_page_header
    from legal import show_legal_page
except:
    # Fallback für die Entwicklung
    def login_bereich(): st.sidebar.write("Login")
    def show_legal_page(): st.title("Rechtliches")

# --- 1. SETUP & DEIN ORIGINAL CSS DESIGN ---
st.set_page_config(page_title="KletterKompass Deutschland", layout="wide")

# HIER IST DEINE GRÜNE SCHRIFT UND DEIN STYLING ZURÜCK!
st.markdown("""
    <style>
    /* Deine grüne Kletterkompass-Schrift */
    h1, h2, h3, .stSubheader, label {
        color: #2e7d32 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Buttons in deiner Farbe */
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
        width: 100%;
    }
    
    /* Eingabefelder */
    .stTextInput>div>div>input {
        border-color: #2e7d32;
    }
    </style>
    """, unsafe_allow_html=True)

# Hilfsfunktionen
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

# Status-Check
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# --- 2. SIDEBAR ---
with st.sidebar:
    # DEIN LOGO WIRD GELADEN (Dateiname prüfen!)
    try:
        st.image("logo.png", width=150)
    except:
        st.title("🧗 Kletterkompass")
    
    st.write("---")
    if st.button("📍 Spielplatz suchen", key="btn_suche"): st.session_state.wahl = "📍 Suche"
    if st.button("📄 Rechtliches", key="btn_legal"): st.session_state.wahl = "📄 Rechtliches"
    
    if st.session_state.logged_in:
        st.write("---")
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()
    else:
        st.write("---")
        login_bereich()

# --- 3. SEITEN-LOGIK ---
if st.session_state.wahl == "📍 Suche":
    # DEIN BANNER WIRD GELADEN (Dateiname prüfen!)
    try:
        st.image("banner.jpg", use_column_width=True)
    except:
        st.write("---")
    
    st.title("Spielplätze & Parks")
    
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Ort / Adresse", "Varel")
    with c2: km = st.slider("Radius (km)", 1, 100, 20)
    
    if st.button("🔍 Suchen", type="primary", use_container_width=True):
        try:
            geocoder = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
            res_g = geocoder.geocode(adr + ", Deutschland")
            if res_g:
                slat, slon = res_g[0]['geometry']['lat'], res_g[0]['geometry']['lng']
                df = hole_df("SELECT * FROM spielplaetze")
                
                if not df.empty:
                    df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                    final = df[df['distanz'] <= km].sort_values('distanz')
                    
                    cl, cr = st.columns(2)
                    with cl:
                        for i, r in final.iterrows():
                            with st.expander(f"📍 {r['Standort']} ({round(r['distanz'], 1)} km)"):
                                st.write(f"Altersfreigabe: {r['altersfreigabe']}")
                                w = get_weather(r['lat'], r['lon'])
                                if w: st.info(f"Wetter: {w['temperature']}°C")
                    with cr:
                        fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10)
                        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                        st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Suche fehlgeschlagen: {e}")

elif st.session_state.wahl == "📄 Rechtliches":
    show_legal_page()
