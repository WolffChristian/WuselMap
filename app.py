import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import requests

# Unsere Spezial-Importe
from database_manager import hole_df, ausfuehren, get_db_connection, hash_passwort
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

# --- Hauptseiten-Inhalte ---
if st.session_state.wahl == "📍 Suche":
    display_home_banner()
    st.title("Finde Spielplätze & Parks")
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Ort oder Adresse", placeholder="z.B. Varel oder Berlin")
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
                
                if not final.empty:
                    cl, cr = st.columns([1, 1])
                    with cl:
                        for i, r in final.iterrows():
                            with st.expander(f"📍 {r['standort']} - {round(r['distanz'], 1)} km"):
                                st.write(f"**👶 Altersfreigabe:** {r['altersfreigabe']}")
                                st.progress(int(r['auslastung'])/100)
                                w = get_weather(r['lat'], r['lon'])
                                if w: st.info(f"🌡️ Wetter: {w['temperature']}°C")
                    with cr:
                        fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="standort", color_discrete_sequence=["#FF0000"], zoom=10)
                        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                        st.plotly_chart(fig, use_container_width=True)
                else: st.warning("Hier gibt es noch keine Einträge.")
        else: st.error("Ort nicht gefunden.")

elif st.session_state.wahl == "🏗️ Vorschlag":
    display_page_header()
    st.title("🏗️ Ort melden oder aktualisieren")
    
    # 1. Auswahl: Neu oder Bestehend?
    melde_art = st.radio("Was möchtest du tun?", ["Einen ganz neuen Ort melden", "Infos zu einem bestehenden Ort ergänzen"], horizontal=True)
    
    with st.form("v_form_final", clear_on_submit=True):
        exist_id = None
        
        if melde_art == "Infos zu einem bestehenden Ort ergänzen":
            # Liste aller existierenden Plätze laden
            df_exist = hole_df("SELECT spiel_id, standort FROM spielplaetze ORDER BY standort")
            auswahl = st.selectbox("Welchen Platz meinst du?", df_exist['standort'].tolist())
            exist_id = int(df_exist[df_exist['standort'] == auswahl]['spiel_id'].iloc[0])
            st.info(f"Du sendest ein Update für: **{auswahl}**")
            p_name = auswahl
            p_adr = ""
            p_bund = ""
        else:
            p_name = st.text_input("Name des neuen Ortes")
            col1, col2 = st.columns([2, 1])
            with col1: p_adr = st.text_input("Genaue Adresse")
            with col2: p_bund = st.selectbox("Bundesland", BUNDESLAENDER, index=8)

        p_bes = st.text_area("Beschreibung / Was hat sich geändert?")
        p_kat = st.radio("Kategorie", ["Spielplatz", "Park", "Freizeitpark"], horizontal=True)
        p_aus = st.multiselect("Ausstattung", ["Rutsche", "Schaukel", "Sandkasten", "Seilbahn", "Klettergerüst", "Wasserspiel", "Picknick"])
        p_bild = st.file_uploader("Neues Bild hochladen", type=['jpg', 'png'])
        
        if st.form_submit_button("Vorschlag absenden"):
            if p_name:
                b_data = p_bild.read() if p_bild else None
                m_typ = "Update" if melde_art == "Infos zu einem bestehenden Ort ergänzen" else "Neu"
                sql = """INSERT INTO vorschlaege 
                         (nutzer_id, platz_name, adresse, bundesland, beschreibung, kategorie, ausstattung, bild, existierende_id, melde_typ) 
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                if ausfuehren(sql, (st.session_state.nutzer_id, p_name, p_adr, p_bund, p_bes, p_kat, ",".join(p_aus), b_data, exist_id, m_typ)):
                    st.success("Danke! Dein Vorschlag wurde zur Prüfung an Christian gesendet.")
                    st.balloons()
            else: st.warning("Bitte gib einen Namen an.")

elif st.session_state.wahl == "🛠️ Admin":
    display_page_header()
    st.title("🛠️ Admin-Dashboard")
    t1, t2, t3 = st.tabs(["👥 Nutzer", "💬 Feedback", "📝 Neue Vorschläge"])
    
    with t3:
        # Hier zeigen wir jetzt auch an, ob es ein Update oder ein neuer Platz ist
        v_list = hole_df("SELECT * FROM vorschlaege ORDER BY zeitstempel DESC")
        for i, v in v_list.iterrows():
            farbe = "🔵 UPDATE" if v['melde_typ'] == "Update" else "🟢 NEU"
            with st.expander(f"{farbe}: {v['platz_name']} ({v['bundesland']})"):
                if v['melde_typ'] == "Update":
                    st.warning(f"Dieses Update bezieht sich auf Spielplatz-ID: {v['existierende_id']}")
                st.write(f"**Beschreibung:** {v['beschreibung']}")
                st.write(f"**Ausstattung:** {v['ausstattung']}")
                if v['bild']: st.image(v['bild'], width=300)
                if st.button("Löschen / Erledigt", key=f"del_{v['vorschlag_id']}"):
                    if ausfuehren("DELETE FROM vorschlaege WHERE vorschlag_id=%s", (v['vorschlag_id'],)):
                        st.rerun()

# ... (Profil, Feedback, Rechtliches wie gehabt)
