import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import requests

from database_manager import hole_df, ausfuehren, get_db_connection
from auth_manager import login_bereich
from assets_helper import display_sidebar_logo, display_home_banner, display_page_header
from legal import show_legal_page

# --- Konfiguration ---
st.set_page_config(page_title="KletterKompass Varel", layout="wide")

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

# --- Sidebar Navigation ---
with st.sidebar:
    display_sidebar_logo()
    if st.button("📍 Suche", width='stretch'): st.session_state.wahl = "📍 Suche"
    if st.button("📄 Rechtliches", width='stretch'): st.session_state.wahl = "📄 Rechtliches"
    st.write("---")
    
    if st.session_state.logged_in:
        if st.button("👤 Profil", width='stretch'): st.session_state.wahl = "👤 Profil"
        if st.button("🏗️ Melden", width='stretch'): st.session_state.wahl = "🏗️ Vorschlag"
        if st.button("💬 Feedback", width='stretch'): st.session_state.wahl = "💬 Feedback"
        if st.session_state.rolle == "admin":
            st.markdown("### 🔐 Admin-Zone")
            if st.button("📊 Dashboard", width='stretch'): st.session_state.wahl = "🛠️ Admin"
        st.write("---")
        if st.button("🚪 Logout", width='stretch'):
            st.session_state.clear()
            st.rerun()
    else:
        login_bereich()

# --- Seiteninhalte ---
if st.session_state.wahl == "📍 Suche":
    display_home_banner()
    st.title("Spielplätze & Parks")
    col_a, col_b = st.columns([3, 1])
    with col_a: adr = st.text_input("Adresse", "Varel")
    with col_b: km = st.slider("Radius (km)", 1, 50, 15)
    
    if st.button("🔍 Ergebnisse anzeigen", type="primary"):
        geocoder = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        res_g = geocoder.geocode(adr + ", Friesland")
        if res_g:
            slat, slon = res_g[0]['geometry']['lat'], res_g[0]['geometry']['lng']
            df = hole_df("SELECT * FROM spielplaetze")
            if not df.empty:
                df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                final = df[df['distanz'] <= km].sort_values('distanz')
                
                cl, cr = st.columns([1, 1])
                with cl:
                    for i, r in final.iterrows():
                        with st.expander(f"📍 {r['standort']} ({round(r['distanz'], 1)} km)"):
                            st.write(f"Altersfreigabe: {r['altersfreigabe']}")
                            w = get_weather(r['lat'], r['lon'])
                            if w: st.info(f"Wetter: {w['temperature']}°C")
                with cr:
                    fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="standort", color_discrete_sequence=["#FF0000"], zoom=11)
                    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.wahl == "🛠️ Admin" and st.session_state.rolle == "admin":
    display_page_header()
    st.title("Admin-Dashboard")
    t_u, t_v = st.tabs(["Benutzer", "Vorschläge"])
    with t_u:
        st.dataframe(hole_df("SELECT nutzer_id, benutzername, email, rolle FROM nutzer"))
    with t_v:
        # Hier werden die eingereichten Orte mit Bildern geladen
        vorschlaege = hole_df("SELECT * FROM vorschlaege ORDER BY zeitstempel DESC")
        st.dataframe(vorschlaege)

elif st.session_state.wahl == "📄 Rechtliches":
    show_legal_page()
