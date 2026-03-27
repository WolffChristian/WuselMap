import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import requests

# Spezial-Importe
from database_manager import hole_df, ausfuehren, image_optimieren, hash_passwort, get_db_connection
from auth_manager import login_bereich
from assets_helper import display_sidebar_logo, display_home_banner, display_page_header
from legal import show_legal_page

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

# --- App Setup ---
st.set_page_config(page_title="KletterKompass Deutschland", layout="wide")
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# Nutzerdaten laden
nutzer_daten = None
if st.session_state.logged_in:
    df_n = hole_df("SELECT * FROM nutzer WHERE nutzer_id=%s", (st.session_state.nutzer_id,))
    if not df_n.empty: nutzer_daten = df_n.iloc[0]

# --- Sidebar ---
with st.sidebar:
    display_sidebar_logo()
    if nutzer_daten is not None:
        st.markdown(f"### Moin, {nutzer_daten['avatar_emoji']} {nutzer_daten['vorname']}")
        st.write("---")
    if st.button("📍 Spielplatz suchen", use_container_width=True): st.session_state.wahl = "📍 Suche"
    if st.button("📄 Rechtliches", use_container_width=True): st.session_state.wahl = "📄 Rechtliches"
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

# --- Hauptlogik ---
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
                df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                final = df[df['distanz'] <= km].sort_values('distanz')
                cl, cr = st.columns(2)
                with cl:
                    for i, r in final.iterrows():
                        with st.expander(f"📍 {r['standort']} ({round(r['distanz'], 1)} km)"):
                            st.write(f"Altersfreigabe: {r['altersfreigabe']}")
                            w = get_weather(r['lat'], r['lon'])
                            if w: st.info(f"Wetter: {w['temperature']}°C")
                with cr:
                    fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="standort", color_discrete_sequence=["#FF0000"], zoom=10)
                    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.wahl == "👤 Profil" and nutzer_daten is not None:
    display_page_header()
    st.title("👤 Mein Profil")
    c_info, c_pref = st.columns(2)
    with c_info:
        st.write(f"**Name:** {nutzer_daten['vorname']} {nutzer_daten['nachname']}")
        st.write(f"**E-Mail:** {nutzer_daten['email']}")
        with st.expander("🔐 Passwort ändern"):
            p1 = st.text_input("Neues Passwort", type="password")
            if st.button("Aktualisieren", use_container_width=True):
                if len(p1) > 3:
                    ausfuehren("UPDATE nutzer SET passwort=%s WHERE nutzer_id=%s", (hash_passwort(p1), st.session_state.nutzer_id))
                    st.success("Erledigt!")
    with c_pref:
        st.write(f"**Dein Avatar:** {nutzer_daten['avatar_emoji']}")
        with st.expander("🖼️ Avatar ändern"):
            cols = st.columns(5)
            for i, emo in enumerate(AVATAR_OPTIONS):
                if cols[i % 5].button(emo, key=f"av_{i}"):
                    ausfuehren("UPDATE nutzer SET avatar_emoji=%s WHERE nutzer_id=%s", (emo, st.session_state.nutzer_id))
                    st.rerun()

elif st.session_state.wahl == "🏗️ Vorschlag":
    display_page_header()
    st.title("🏗️ Ort melden")
    st.error("📸 **WICHTIG:** Keine Personen oder Kinder auf den Fotos!")
    m_art = st.radio("Typ:", ["Neu", "Update"], horizontal=True)
    with st.form("v_form"):
        p_name = st.text_input("Name")
        p_adr = st.text_input("Adresse / Wegbeschreibung")
        p_bund = st.selectbox("Bundesland", BUNDESLAENDER, index=8)
        p_bild = st.file_uploader("Bild", type=['jpg', 'jpeg', 'png'])
        if st.form_submit_button("Absenden", use_container_width=True):
            b_data = image_optimieren(p_bild) if p_bild else None
            sql = "INSERT INTO vorschlaege (nutzer_id, platz_name, adresse, bundesland, bild, melde_typ) VALUES (%s,%s,%s,%s,%s,%s)"
            if ausfuehren(sql, (st.session_state.nutzer_id, p_name, p_adr, p_bund, b_data, m_art)):
                st.success("Gesendet! Danke."); st.balloons()

elif st.session_state.wahl == "💬 Feedback":
    display_page_header()
    st.title("💬 Feedback geben")
    st.write("Hilf uns, den KletterKompass besser zu machen!")
    msg = st.text_area("Deine Nachricht an uns:", height=150)
    if st.button("Feedback senden", use_container_width=True):
        if msg:
            if ausfuehren("INSERT INTO feedback (nutzer_id, nachricht) VALUES (%s,%s)", (st.session_state.nutzer_id, msg)):
                st.success("Vielen Dank! Dein Feedback ist angekommen.")
                st.balloons()
        else:
            st.warning("Bitte schreibe erst etwas in das Textfeld.")

elif st.session_state.wahl == "🛠️ Admin" and st.session_state.rolle == "admin":
    display_page_header()
    st.title("🛠️ Admin-Dashboard")
    t1, t2, t3 = st.tabs(["👥 Nutzer", "💬 Feedback", "📝 Vorschläge"])
    with t1:
        st.dataframe(hole_df("SELECT nutzer_id, benutzername, email, vorname, nachname, rolle, avatar_emoji FROM nutzer"), use_container_width=True)
    with t2:
        st.dataframe(hole_df("SELECT * FROM feedback ORDER BY zeitstempel DESC"), use_container_width=True)
    with t3:
        v_list = hole_df("SELECT * FROM vorschlaege ORDER BY zeitstempel DESC")
        for i, v in v_list.iterrows():
            with st.expander(f"{v['melde_typ']}: {v['platz_name']}"):
                if v['bild']: st.image(v['bild'], use_container_width=True)
                if st.button("Löschen", key=f"del_{v['vorschlag_id']}", use_container_width=True):
                    ausfuehren("DELETE FROM vorschlaege WHERE vorschlag_id=%s", (v['vorschlag_id'],))
                    st.rerun()

elif st.session_state.wahl == "📄 Rechtliches":
    show_legal_page()
