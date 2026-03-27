import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import requests

# Unsere Spezial-Importe (mit der neuen Bild-Optimierung)
from database_manager import hole_df, ausfuehren, image_optimieren
from auth_manager import login_bereich
from assets_helper import display_sidebar_logo, display_home_banner, display_page_header
from legal import show_legal_page

# --- Hilfsfunktionen ---
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

BUNDESLAENDER = ["Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen", "Mecklenburg-Vorpommern", "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland", "Sachsen", "Sachsen-Anhalt", "Schleswig-Holstein", "Thüringen"]

# --- Konfiguration ---
st.set_page_config(page_title="KletterKompass Deutschland", layout="wide")
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# --- Sidebar ---
with st.sidebar:
    display_sidebar_logo()
    if st.button("📍 Suche", width='stretch'): st.session_state.wahl = "📍 Suche"
    if st.button("📄 Rechtliches", width='stretch'): st.session_state.wahl = "📄 Rechtliches"
    st.write("---")
    
    if st.session_state.logged_in:
        if st.button("👤 Profil"): st.session_state.wahl = "👤 Profil"
        if st.button("🏗️ Melden"): st.session_state.wahl = "🏗️ Vorschlag"
        if st.button("💬 Feedback"): st.session_state.wahl = "💬 Feedback"
        if st.session_state.rolle == "admin":
            if st.button("🛠️ Admin"): st.session_state.wahl = "🛠️ Admin"
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()
    else:
        login_bereich()

# --- Hauptseiten-Logik (Suche & Melden mit Bild-Optimierung) ---
if st.session_state.wahl == "📍 Suche":
    display_home_banner()
    st.title("Spielplätze in ganz Deutschland")
    col1, col2 = st.columns([3, 1])
    with col1: adr = st.text_input("Suchen nach (z.B. Varel, Berlin oder Hamburg)", "Varel")
    with col2: km = st.slider("Radius (km)", 1, 100, 20)
    if st.button("🔍 Suchen", type="primary"):
        geocoder = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        res_g = geocoder.geocode(adr + ", Deutschland")
        if res_g:
            lat, lon = res_g[0]['geometry']['lat'], res_g[0]['geometry']['lng']
            df = hole_df("SELECT * FROM spielplaetze")
            if not df.empty:
                df['distanz'] = df.apply(lambda r: distanz(lat, lon, r['lat'], r['lon']), axis=1)
                final = df[df['distanz'] <= km].sort_values('distanz')
                
                if not final.empty:
                    cl, cr = st.columns([1, 1])
                    with cl:
                        for i, r in final.iterrows():
                            with st.expander(f"📍 {r['standort']} ({round(r['distanz'], 1)} km)"):
                                st.write(f"Altersfreigabe: {r['altersfreigabe']}")
                                w = get_weather(r['lat'], r['lon'])
                                if w: st.info(f"Wetter: {w['temperature']}°C")
                    with cr:
                        fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="standort", zoom=11)
                        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                        st.plotly_chart(fig, use_container_width=True)
                else: st.warning("Leider keine Spielplätze gefunden.")
        else: st.error("Dieser Ort wurde leider nicht gefunden.")

elif st.session_state.wahl == "🏗️ Vorschlag":
    display_page_header()
    st.title("🏗️ Neuen Platz melden")
    melde_art = st.radio("Was möchtest du tun?", ["Neu melden", "Ergänzen"], horizontal=True)
    
    with st.form("vorschlag_erweitert", clear_on_submit=True):
        exist_id = None
        if melde_art == "Ergänzen":
            df_exist = hole_df("SELECT spiel_id, standort FROM spielplaetze ORDER BY standort")
            auswahl = st.selectbox("Welchen Platz meinst du?", df_exist['standort'].tolist())
            exist_id = int(df_exist[df_exist['standort'] == auswahl]['spiel_id'].iloc[0])
            st.info(f"Update für: **{auswahl}**")
            p_name = auswahl; p_adr = ""; p_bund = ""
        else:
            p_name = st.text_input("Name")
            col1, col2 = st.columns([2, 1])
            with col1: p_adr = st.text_input("Adresse")
            with col2: p_bund = st.selectbox("Bundesland", BUNDESLAENDER, index=8)

        p_bes = st.text_area("Beschreibung / Wegbeschreibung")
        p_aus = st.multiselect("Ausstattung", ["Rutsche", "Schaukel", "Sandkasten", "Seilbahn", "Klettergerüst", "Wasserspiel"])
        p_bild_datei = st.file_uploader("Bild hochladen (optional)", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("Vorschlag absenden"):
            if p_name:
                # FIX: Das Bild wird jetzt automatisch optimiert!
                optimized_bild_data = None
                if p_bild_datei is not None:
                    optimized_bild_data = image_optimieren(p_bild_datei, max_width=1000, quality=80)
                
                m_typ = "Update" if melde_art == "Ergänzen" else "Neu"
                sql = """INSERT INTO vorschlaege 
                         (nutzer_id, platz_name, adresse, bundesland, beschreibung, ausstattung, bild, existierende_id, melde_typ) 
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                if ausfuehren(sql, (st.session_state.nutzer_id, p_name, p_adr, p_bund, p_bes, ",".join(p_aus), optimized_bild_data, exist_id, m_typ)):
                    st.success("Erfolgreich gesendet! Wir prüfen deinen Vorschlag.")
                    st.balloons()
            else: st.warning("Bitte gib einen Namen an.")

elif st.session_state.wahl == "🛠️ Admin":
    display_page_header()
    st.title("Admin-Dashboard")
    t1, t2 = st.tabs(["Benutzer", "Vorschläge"])
    with t1: st.dataframe(hole_df("SELECT nutzer_id, benutzername, email, rolle FROM nutzer"))
    with t2:
        v_list = hole_df("SELECT * FROM vorschlaege ORDER BY zeitstempel DESC")
        for i, v in v_list.iterrows():
            with st.expander(f"{v['platz_name']} ({v['melde_typ']})"):
                st.write(f"Ausstattung: {v['ausstattung']}\nBeschreibung: {v['beschreibung']}")
                if v['bild']:
                    # Das optimierte WebP-Bild wird hier angezeigt
                    st.image(v['bild'], width=300, caption="Optimiertes WebP")

# ... (Rest bleibt wie gehabt: Profil, Feedback, Rechtliches)
elif st.session_state.wahl == "👤 Profil":
    display_page_header()
    st.dataframe(hole_df("SELECT * FROM nutzer WHERE nutzer_id=%s", (st.session_state.nutzer_id,)))

elif st.session_state.wahl == "💬 Feedback":
    display_page_header()
    msg = st.text_area("Wie gefällt dir die App?")
    if st.button("Feedback senden"):
        if ausfuehren("INSERT INTO feedback (nutzer_id, nachricht) VALUES (%s,%s)", (st.session_state.nutzer_id, msg)):
            st.success("Danke!")

elif st.session_state.wahl == "📄 Rechtliches":
    show_legal_page()
