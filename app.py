import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import mysql.connector
import requests
from assets_helper import display_sidebar_logo, display_home_banner, display_page_header
from legal import show_legal_page

# --- 1. SETUP & DATENBANK ---
st.set_page_config(page_title="KletterKompass Varel", layout="wide")

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            port=int(st.secrets["DB_PORT"]),
            database=st.secrets["DB_NAME"],
            ssl_disabled=False 
        )
    except Exception as e:
        st.error(f"Datenbank-Verbindungsfehler: {e}")
        return None

def hole_df_aus_db(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Abfragefehler: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=5).json()
        return response['current_weather']
    except:
        return None

# --- 2. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'nutzer_id' not in st.session_state: st.session_state.nutzer_id = None
if 'rolle' not in st.session_state: st.session_state.rolle = "gast"
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    display_sidebar_logo()  
    st.info("✨ **BETA-PHASE**")
    
    if st.button("📍 Spielplatz suchen", width='stretch', key="nav_suche"):
        st.session_state.wahl = "📍 Suche"
    
    if st.button("📄 AGB & Datenschutz", width='stretch', key="nav_legal"):
        st.session_state.wahl = "📄 Rechtliches"
    
    st.write("---")

    if st.session_state.logged_in:
        if st.button("👤 Mein Profil", width='stretch'): st.session_state.wahl = "👤 Profil"
        if st.button("💬 Feedback geben", width='stretch'): st.session_state.wahl = "💬 Feedback"
        if st.button("🏗️ Neuen Platz melden", width='stretch'): st.session_state.wahl = "🏗️ Vorschlag"
        
        if st.session_state.rolle == "admin":
            st.markdown("### 🔐 Admin-Zone")
            if st.button("📊 Admin-Dashboard", width='stretch'): 
                st.session_state.wahl = "🛠️ Admin"
        
        st.write("---")
        if st.button("🚪 Logout", width='stretch'):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
    else:
        t1, t2 = st.tabs(["🔑 Login", "📝 Registrierung"])
        with t1:
            u = st.text_input("User", key="login_u")
            p = st.text_input("Passwort", type="password", key="login_p")
            if st.button("Anmelden", width='stretch'):
                df_u = hole_df_aus_db("SELECT nutzer_id, rolle FROM nutzer WHERE benutzername=%s AND passwort=%s", (u, p))
                if not df_u.empty:
                    st.session_state.logged_in = True
                    st.session_state.nutzer_id = int(df_u.iloc[0]['nutzer_id'])
                    st.session_state.rolle = df_u.iloc[0]['rolle']
                    st.rerun()
                else: st.error("Login fehlgeschlagen.")
        
        with t2:
            # FIX: Formular für Sabrina für stabilere Registrierung
            with st.form("reg_form", clear_on_submit=True):
                reg_u = st.text_input("Nutzername")
                reg_p = st.text_input("Passwort", type="password")
                reg_v = st.text_input("Vorname")
                reg_n = st.text_input("Nachname")
                reg_m = st.text_input("E-Mail")
                reg_a = st.number_input("Dein Alter", 0, 120, 30)
                reg_agb = st.checkbox("Ich akzeptiere die AGB")
                
                if st.form_submit_button("Konto erstellen", width='stretch'):
                    if reg_agb and all([reg_u, reg_p, reg_v, reg_n, reg_m]):
                        conn = get_db_connection()
                        if conn:
                            try:
                                cursor = conn.cursor()
                                sql = "INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, alter_wert, rolle) VALUES (%s, %s, %s, %s, %s, %s, 'user')"
                                cursor.execute(sql, (reg_u, reg_p, reg_m, reg_v, reg_n, reg_a))
                                conn.commit()
                                st.success("Registrierung erfolgreich! Bitte jetzt einloggen.")
                                st.balloons()
                                conn.close()
                            except Exception as e: st.error(f"Fehler: {e}")
                    else: st.warning("Bitte alle Felder ausfüllen & AGB bestätigen.")

# --- 4. SEITEN-LOGIK ---
if st.session_state.wahl == "📍 Suche":
    display_home_banner()
    st.title("Spielplätze & Parks in Varel")
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Wo suchst du?", "Varel")
    with c2: km = st.slider("Radius (km)", 1, 50, 15)
    
    if st.button("🔍 Suchen", type="primary"):
        geocoder = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        res_g = geocoder.geocode(adr + ", Friesland")
        if res_g:
            lat, lon = res_g[0]['geometry']['lat'], res_g[0]['geometry']['lng']
            df = hole_df_aus_db("SELECT * FROM spielplaetze")
            if not df.empty:
                df['distanz'] = df.apply(lambda r: distanz(lat, lon, r['lat'], r['lon']), axis=1)
                res = df[df['distanz'] <= km].sort_values('distanz')
                
                cl, cm = st.columns([1, 1])
                with cl:
                    for i, r in res.iterrows():
                        with st.expander(f"📍 {r['standort']} ({round(r['distanz'], 1)} km)"):
                            st.write(f"**👶 Altersfreigabe:** {r.get('altersfreigabe', 'n.V.')}")
                            st.progress(int(r.get('auslastung', 0)) / 100)
                            w = get_weather(r['lat'], r['lon'])
                            if w: st.info(f"🌡️ {w['temperature']} °C")
                with cm:
                    fig = px.scatter_mapbox(res, lat="lat", lon="lon", hover_name="standort", color_discrete_sequence=["#FF0000"], zoom=11)
                    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.wahl == "📄 Rechtliches":
    show_legal_page()

elif st.session_state.wahl == "👤 Profil":
    display_page_header()
    st.title("Mein Profil")
    df_p = hole_df_aus_db("SELECT * FROM nutzer WHERE nutzer_id=%s", (st.session_state.nutzer_id,))
    if not df_p.empty:
        u = df_p.iloc[0]
        st.write(f"**Name:** {u['vorname']} {u['nachname']}")
        st.write(f"**E-Mail:** {u['email']}")
        st.write(f"**Alter:** {u['alter_wert']} Jahre")

elif st.session_state.wahl == "💬 Feedback":
    display_page_header()
    st.title("Feedback")
    msg = st.text_area("Was können wir verbessern?")
    if st.button("Feedback senden"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO feedback (nutzer_id, nachricht) VALUES (%s, %s)", (st.session_state.nutzer_id, msg))
            conn.commit()
            conn.close()
            st.success("Danke!")

elif st.session_state.wahl == "🏗️ Vorschlag":
    display_page_header()
    st.title("Neuen Platz melden")
    with st.form("vorschlag_erweitert", clear_on_submit=True):
        p_name = st.text_input("Name des Ortes")
        p_adr = st.text_input("Genaue Adresse")
        p_kat = st.radio("Kategorie", ["Spielplatz", "Park", "Freizeitpark"], horizontal=True)
        p_aus = st.multiselect("Ausstattung", ["Rutsche", "Schaukel", "Sandkasten", "Seilbahn", "Klettergerüst", "Wasserspiel"])
        p_bild = st.file_uploader("Bild hochladen", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("Vorschlag absenden"):
            if p_name and p_adr:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    bild_data = p_bild.read() if p_bild else None
                    sql = "INSERT INTO vorschlaege (nutzer_id, platz_name, adresse, kategorie, ausstattung, bild) VALUES (%s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (st.session_state.nutzer_id, p_name, p_adr, p_kat, ",".join(p_aus), bild_data))
                    conn.commit()
                    conn.close()
                    st.success("Erfolgreich gesendet!")
                    st.balloons()
            else: st.warning("Name und Adresse sind Pflichtfelder.")

elif st.session_state.wahl == "🛠️ Admin":
    if st.session_state.rolle == "admin":
        display_page_header()
        st.title("🛠️ Admin-Dashboard")
        t_u, t_f, t_v = st.tabs(["👥 Nutzer", "💬 Feedback", "📝 Vorschläge"])
        with t_u:
            st.dataframe(hole_df_aus_db("SELECT * FROM nutzer"))
        with t_f:
            # Zeigt Feedback mit Namen des Nutzers an
            sql_f = """SELECT n.benutzername, f.nachricht, f.zeitstempel 
                       FROM feedback f JOIN nutzer n ON f.nutzer_id = n.nutzer_id 
                       ORDER BY f.zeitstempel DESC"""
            st.dataframe(hole_df_aus_db(sql_f))
        with t_v:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM vorschlaege ORDER BY zeitstempel DESC")
                for v in cursor.fetchall():
                    with st.expander(f"{v['platz_name']} ({v['kategorie']})"):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.write(f"**Adresse:** {v['adresse']}")
                            st.write(f"**Ausstattung:** {v['ausstattung']}")
                        with c2:
                            if v['bild']: st.image(v['bild'], width=200)
                conn.close()
