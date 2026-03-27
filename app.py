import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import requests

# Spezial-Importe
from database_manager import hole_df, ausfuehren, image_optimieren, get_db_connection, hash_passwort
from auth_manager import login_bereich
from assets_helper import display_sidebar_logo, display_home_banner, display_page_header
from legal import show_legal_page

BUNDESLAENDER = ["Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen", "Mecklenburg-Vorpommern", "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland", "Sachsen", "Sachsen-Anhalt", "Schleswig-Holstein", "Thüringen"]

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

# --- Konfiguration ---
st.set_page_config(page_title="KletterKompass Deutschland", layout="wide")
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# --- Sidebar mit GROSSEN Buttons ---
with st.sidebar:
    display_sidebar_logo()
    if st.button("📍 Spielplatz suchen", use_container_width=True): st.session_state.wahl = "📍 Suche"
    if st.button("📄 AGB & Rechtliches", use_container_width=True): st.session_state.wahl = "📄 Rechtliches"
    st.write("---")
    
    if st.session_state.logged_in:
        if st.button("👤 Mein Profil", use_container_width=True): st.session_state.wahl = "👤 Profil"
        if st.button("🏗️ Neuen Platz melden", use_container_width=True): st.session_state.wahl = "🏗️ Vorschlag"
        if st.button("💬 Feedback geben", use_container_width=True): st.session_state.wahl = "💬 Feedback"
        if st.session_state.rolle == "admin":
            st.markdown("### 🔐 Admin-Zone")
            if st.button("📊 Admin-Dashboard", use_container_width=True): st.session_state.wahl = "🛠️ Admin"
        st.write("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    else:
        login_bereich()

# --- Hauptseiten ---
if st.session_state.wahl == "📍 Suche":
    display_home_banner()
    st.title("Spielplätze & Parks")
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Ort oder Adresse", placeholder="z.B. Varel oder Berlin")
    with c2: km = st.slider("Radius (km)", 1, 100, 20)
    
    if st.button("🔍 Suchen", type="primary", use_container_width=True):
        geocoder = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        res_g = geocoder.geocode(adr + ", Deutschland")
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
                            st.write(f"**Baby/Kind:** {r['altersfreigabe']}")
                            w = get_weather(r['lat'], r['lon'])
                            if w: st.info(f"Wetter: {w['temperature']}°C")
                with cr:
                    fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="standort", color_discrete_sequence=["#FF0000"], zoom=10)
                    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.wahl == "🏗️ Vorschlag":
    display_page_header()
    st.title("🏗️ Neuen Ort melden")
    st.error("📸 **WICHTIG:** Keine Kinder oder Personen auf den Fotos! Fotografiere nur den Platz und die Geräte.")
    
    melde_art = st.radio("Meldungs-Typ:", ["Neu melden", "Update senden"], horizontal=True)
    
    with st.form("vorschlag_form_final"):
        exist_id = None
        if melde_art == "Update senden":
            df_exist = hole_df("SELECT spiel_id, standort FROM spielplaetze ORDER BY standort")
            if not df_exist.empty:
                auswahl = st.selectbox("Welchen Platz meinst du?", df_exist['standort'].tolist())
                exist_id = int(df_exist[df_exist['standort'] == auswahl]['spiel_id'].iloc[0])
                p_name = auswahl; p_adr = ""; p_bund = ""
            else: st.error("Keine Plätze vorhanden."); st.stop()
        else:
            p_name = st.text_input("Name des neuen Ortes")
            col_a, col_b = st.columns([2, 1])
            with col_a: p_adr = st.text_input("Genaue Adresse (falls bekannt)")
            with col_b: p_bund = st.selectbox("Bundesland", BUNDESLAENDER, index=8)

        p_bes = st.text_area("Beschreibung / Wegbeschreibung")
        p_kat = st.radio("Kategorie", ["Spielplatz", "Park"], horizontal=True)
        p_aus = st.multiselect("Ausstattung", ["Rutsche", "Schaukel", "Sandkasten", "Seilbahn", "Klettergerüst", "Wasserspiel"])
        p_bild = st.file_uploader("Bild hochladen", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("Vorschlag absenden", use_container_width=True):
            if p_name:
                b_data = image_optimieren(p_bild) if p_bild else None
                m_typ = "Update" if melde_art == "Update senden" else "Neu"
                sql = """INSERT INTO vorschlaege 
                         (nutzer_id, platz_name, adresse, bundesland, beschreibung, kategorie, ausstattung, bild, existierende_id, melde_typ) 
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                if ausfuehren(sql, (st.session_state.nutzer_id, p_name, p_adr, p_bund, p_bes, p_kat, ",".join(p_aus), b_data, exist_id, m_typ)):
                    st.success("Danke! Christian prüft deinen Vorschlag.")
                    st.balloons()
            else: st.error("Bitte gib einen Namen an.")

elif st.session_state.wahl == "🛠️ Admin":
    display_page_header()
    st.title("🛠️ Admin-Dashboard")
    t1, t2, t3 = st.tabs(["👥 Nutzer", "💬 Feedback", "📝 Vorschläge"])
    with t1: st.dataframe(hole_df("SELECT nutzer_id, benutzername, email, rolle FROM nutzer"), use_container_width=True)
    with t2: st.dataframe(hole_df("SELECT * FROM feedback ORDER BY zeitstempel DESC"), use_container_width=True)
    with t3:
        v_list = hole_df("SELECT * FROM vorschlaege ORDER BY zeitstempel DESC")
        for i, v in v_list.iterrows():
            with st.expander(f"{v['melde_typ']}: {v['platz_name']} ({v['bundesland']})"):
                st.write(f"Beschreibung: {v['beschreibung']}")
                if v['bild']: 
                    st.image(v['bild'], caption="Vom Nutzer gesendet", use_container_width=True)
                    st.info("Prüfe das Bild auf Personen, bevor du den Platz freischaltest!")
                if st.button("Erledigt / Löschen", key=f"del_{v['vorschlag_id']}", use_container_width=True):
                    if ausfuehren("DELETE FROM vorschlaege WHERE vorschlag_id=%s", (v['vorschlag_id'],)):
                        st.rerun()

elif st.session_state.wahl == "👤 Profil":
    display_page_header()
    st.title("👤 Mein Profil")
    df_p = hole_df("SELECT * FROM nutzer WHERE nutzer_id=%s", (st.session_state.nutzer_id,))
    if not df_p.empty:
        u = df_p.iloc[0]
        st.write(f"**Name:** {u['vorname']} {u['nachname']}")
        st.write(f"**E-Mail:** {u['email']}")

elif st.session_state.wahl == "💬 Feedback":
    display_page_header()
    msg = st.text_area("Wie gefällt dir die App?")
    if st.button("Feedback senden", use_container_width=True):
        if ausfuehren("INSERT INTO feedback (nutzer_id, nachricht) VALUES (%s,%s)", (st.session_state.nutzer_id, msg)):
            st.success("Danke!")

elif st.session_state.wahl == "📄 Rechtliches":
    show_legal_page()
