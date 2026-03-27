import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import requests

# Unsere Spezial-Importe
from database_manager import hole_df, ausfuehren, get_db_connection
from auth_manager import login_bereich
from assets_helper import display_sidebar_logo, display_home_banner, display_page_header
from legal import show_legal_page

# --- Hilfsfunktionen ---
def distanz(lat1, lon1, lat2, lon2):
    R = 6371 # Erdradius in km
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        return requests.get(url, timeout=5).json()['current_weather']
    except: return None

# --- App-Konfiguration & State ---
st.set_page_config(page_title="KletterKompass Varel", layout="wide")
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# --- Sidebar ---
with st.sidebar:
    display_sidebar_logo()
    if st.button("📍 Spielplatz suchen", width='stretch'): st.session_state.wahl = "📍 Suche"
    if st.button("📄 Rechtliches", width='stretch'): st.session_state.wahl = "📄 Rechtliches"
    st.write("---")
    
    if st.session_state.logged_in:
        if st.button("👤 Mein Profil", width='stretch'): st.session_state.wahl = "👤 Profil"
        if st.button("🏗️ Neuen Platz melden", width='stretch'): st.session_state.wahl = "🏗️ Vorschlag"
        if st.button("💬 Feedback geben", width='stretch'): st.session_state.wahl = "💬 Feedback"
        
        if st.session_state.rolle == "admin":
            st.markdown("### 🔐 Admin-Zone")
            if st.button("📊 Admin-Dashboard", width='stretch'): st.session_state.wahl = "🛠️ Admin"
        
        st.write("---")
        if st.button("🚪 Logout", width='stretch'):
            st.session_state.clear()
            st.rerun()
    else:
        login_bereich()

# --- Hauptseiten-Logik ---
if st.session_state.wahl == "📍 Suche":
    display_home_banner()
    st.title("Spielplätze & Parks entdecken")
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Wo bist du gerade?", "Varel")
    with c2: km = st.slider("Radius (km)", 1, 50, 15)
    
    if st.button("🔍 Suchen", type="primary"):
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
                            st.write(f"**👶 Altersfreigabe:** {r['altersfreigabe']}")
                            st.progress(int(r['auslastung'])/100)
                            w = get_weather(r['lat'], r['lon'])
                            if w: st.info(f"🌡️ Wetter vor Ort: {w['temperature']}°C")
                with cr:
                    fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="standort", color_discrete_sequence=["#FF0000"], zoom=11)
                    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.wahl == "👤 Profil":
    display_page_header()
    df_p = hole_df("SELECT * FROM nutzer WHERE nutzer_id=%s", (st.session_state.nutzer_id,))
    if not df_p.empty:
        u = df_p.iloc[0]
        st.write(f"**Name:** {u['vorname']} {u['nachname']}")
        st.write(f"**Status:** {u['rolle'].upper()}")

elif st.session_state.wahl == "🏗️ Vorschlag":
    display_page_header()
    st.title("Neuen Ort melden")
    with st.form("vorschlag_form"):
        p_name = st.text_input("Name")
        p_adr = st.text_input("Adresse")
        p_kat = st.radio("Kategorie", ["Spielplatz", "Park", "Freizeitpark"], horizontal=True)
        p_aus = st.multiselect("Ausstattung", ["Rutsche", "Schaukel", "Sandkasten", "Seilbahn", "Wasserspiel"])
        p_bild = st.file_uploader("Bild (optional)", type=['jpg', 'png'])
        if st.form_submit_button("Senden"):
            bild_data = p_bild.read() if p_bild else None
            sql = "INSERT INTO vorschlaege (nutzer_id, platz_name, adresse, kategorie, ausstattung, bild) VALUES (%s,%s,%s,%s,%s,%s)"
            if ausfuehren(sql, (st.session_state.nutzer_id, p_name, p_adr, p_kat, ",".join(p_aus), bild_data)):
                st.success("Danke! Wir prüfen deinen Vorschlag.")

elif st.session_state.wahl == "💬 Feedback":
    display_page_header()
    msg = st.text_area("Wie gefällt dir die App?")
    if st.button("Feedback senden"):
        if ausfuehren("INSERT INTO feedback (nutzer_id, nachricht) VALUES (%s,%s)", (st.session_state.nutzer_id, msg)):
            st.success("Vielen Dank für deine Meinung!")

elif st.session_state.wahl == "📄 Rechtliches":
    show_legal_page()

elif st.session_state.wahl == "🛠️ Admin":
    display_page_header()
    t1, t2, t3 = st.tabs(["👥 Nutzer", "💬 Feedback", "📝 Vorschläge"])
    with t1:
        st.dataframe(hole_df("SELECT nutzer_id, benutzername, email, rolle FROM nutzer"))
    with t2:
        st.dataframe(hole_df("SELECT * FROM feedback"))
    with t3:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM vorschlaege ORDER BY zeitstempel DESC")
            for v in cursor.fetchall():
                with st.expander(f"{v['platz_name']} ({v['kategorie']})"):
                    c1, c2 = st.columns(2)
                    with c1: st.write(f"Adresse: {v['adresse']}\nAusstattung: {v['ausstattung']}")
                    with c2: 
                        if v['bild']: st.image(v['bild'], width=200)
            conn.close()
