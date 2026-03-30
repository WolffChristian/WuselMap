import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import requests

# HIER WAR DER FEHLER: Jetzt passen die Namen wieder zusammen!
from database_manager import hole_df, ausfuehren, image_optimieren, hash_passwort

# Falls diese Dateien in deinem GitHub sind:
try:
    from auth_manager import login_bereich
    from assets_helper import display_sidebar_logo, display_home_banner, display_page_header
    from legal import show_legal_page
except:
    # Fallback für die Entwicklung
    def login_bereich(): st.sidebar.warning("Login-Modul fehlt auf GitHub")
    def display_sidebar_logo(): st.sidebar.title("🧗 Kletterkompass")
    def display_home_banner(): st.image("https://via.placeholder.com/1200x300?text=Kletterkompass+Banner")
    def display_page_header(): st.write("---")
    def show_legal_page(): st.write("Impressum & Datenschutz")

# --- DESIGN-RETTUNG (DEIN GRÜN!) ---
st.markdown("""
    <style>
    h1, h2, h3, .stSubheader { color: #2e7d32 !important; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

BUNDESLAENDER = ["Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen", "Mecklenburg-Vorpommern", "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland", "Sachsen", "Sachsen-Anhalt", "Schleswig-Holstein", "Thüringen"]
AVATAR_OPTIONS = ['👤', '👩‍💻', '👨‍💻', '🧑‍🚀', '🧗‍♀️', '🧗‍♂️', '🦸‍♀️', '🦸‍♂️', '☀️', '⛺']

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

st.set_page_config(page_title="KletterKompass Deutschland", layout="wide")
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# Nutzerdaten laden
nutzer_daten = None
if st.session_state.logged_in:
    df_n = hole_df("SELECT * FROM nutzer WHERE nutzer_id=%s", (st.session_state.get('nutzer_id'),))
    if not df_n.empty: nutzer_daten = df_n.iloc[0]

with st.sidebar:
    display_sidebar_logo()
    if nutzer_daten is not None:
        st.markdown(f"### Moin, {nutzer_daten['avatar_emoji']} {nutzer_daten['vorname']}")
    
    if st.button("📍 Spielplatz suchen", use_container_width=True): st.session_state.wahl = "📍 Suche"
    if st.button("📄 Rechtliches", use_container_width=True): st.session_state.wahl = "📄 Rechtliches"
    st.write("---")
    
    if st.session_state.logged_in:
        if st.button("👤 Mein Profil", use_container_width=True): st.session_state.wahl = "👤 Profil"
        if st.button("🏗️ Neuen Platz melden", use_container_width=True): st.session_state.wahl = "🏗️ Vorschlag"
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    else: login_bereich()

# SEITENLOGIK
if st.session_state.wahl == "📍 Suche":
    display_home_banner()
    st.title("Spielplätze & Parks")
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Ort / Adresse", "Varel")
    with c2: km = st.slider("Radius (km)", 1, 100, 20)
    
    if st.button("🔍 Suchen", type="primary", use_container_width=True):
        geocoder = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        res_g = geocoder.geocode(adr + ", Deutschland")
        if res_g:
            slat, slon = res_g[0]['geometry']['lat'], res_g[0]['geometry']['lng']
            df = hole_df("SELECT * FROM spielplaetze")
            if not df.empty:
                # Wir stellen sicher, dass die Karte 'lat' und 'lon' findet
                if 'Lon' in df.columns: df = df.rename(columns={'Lon': 'lon'})
                
                df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                final = df[df['distanz'] <= km].sort_values('distanz')
                
                cl, cr = st.columns(2)
                with cl:
                    for i, r in final.iterrows():
                        with st.expander(f"📍 {r['Standort']} ({round(r['distanz'], 1)} km)"):
                            w = get_weather(r['lat'], r['lon'])
                            if w: st.info(f"Wetter: {w['temperature']}°C")
                with cr:
                    fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10)
                    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.wahl == "📄 Rechtliches":
    show_legal_page()
