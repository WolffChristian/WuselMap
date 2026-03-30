import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import requests
import os

from database_manager import hole_df, ausfuehren, image_optimieren, hash_passwort

# --- 1. SETUP & ORIGINAL LOOK ---
st.set_page_config(page_title="KletterKompass Deutschland", layout="wide")

# DEIN ORIGINAL GRÜN (Heller & Freundlicher)
st.markdown("""
    <style>
    /* Das Kletterkompass-Grün für Titel */
    h1, h2, h3, .stSubheader, label { 
        color: #2e7d32 !important; 
        font-family: 'Helvetica Neue', sans-serif; 
        font-weight: 700;
    }
    /* Die Buttons */
    .stButton>button { 
        background-color: #2e7d32; 
        color: white; 
        border-radius: 8px; 
        border: none;
    }
    .stButton>button:hover {
        background-color: #1b5e20;
        color: white;
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

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# --- 2. SIDEBAR ---
with st.sidebar:
    # LOGO-FIX: Wir nutzen jetzt deinen echten Pfad
    logo_path = "assets/Kletterkompass_Logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    else:
        st.title("🧗 Kletterkompass")
    
    st.write("---")
    if st.button("📍 Spielplatz suchen", use_container_width=True): st.session_state.wahl = "📍 Suche"
    if st.button("📄 Rechtliches", use_container_width=True): st.session_state.wahl = "📄 Rechtliches"
    
    if not st.session_state.logged_in:
        st.write("---")
        st.subheader("🔐 Anmeldung")
        u = st.text_input("Nutzername")
        p = st.text_input("Passwort", type="password")
        if st.button("Einloggen", use_container_width=True):
            df_n = hole_df("SELECT * FROM nutzer")
            if not df_n.empty:
                user = df_n[(df_n['benutzername'] == u) & (df_n['passwort'] == hash_passwort(p))]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Login falsch")
    else:
        st.write("---")
        st.success(f"Moin, {st.session_state.user}!")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

# --- 3. HAUPTBEREICH ---
if st.session_state.wahl == "📍 Suche":
    # BANNER-FIX: Wir nutzen dein Hauptbild
    banner_path = "assets/Kletterkompass.png"
    if os.path.exists(banner_path):
        st.image(banner_path, use_container_width=True)
    
    st.title("Spielplätze & Parks")
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Ort / Adresse", "Varel")
    with c2: km = st.slider("Radius (km)", 1, 100, 20)
    
    if st.button("🔍 Suchen", type="primary"):
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
                            w = get_weather(r['lat'], r['lon'])
                            if w: st.info(f"Wetter: {w['temperature']}°C")
                with cr:
                    fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10)
                    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.wahl == "📄 Rechtliches":
    # Schriftzug als Header nutzen
    header_path = "assets/Kletterkompass_Schriftzug.png"
    if os.path.exists(header_path):
        st.image(header_path, width=400)
    st.title("Impressum & Datenschutz")
    st.write("Rechtliche Texte hier einfügen...")
