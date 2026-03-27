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
st.set_page_config(page_title="KletterKompass BETA", layout="wide")

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
        st.error(f"Datenbank-Fehler: {e}")
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
            u = st.text_input("User", key="l_u")
            p = st.text_input("Passwort", type="password", key="l_p")
            if st.button("Anmelden", width='stretch'):
                df_u = hole_df_aus_db("SELECT nutzer_id, rolle FROM nutzer WHERE benutzername=%s AND passwort=%s", (u, p))
                if not df_u.empty:
                    st.session_state.logged_in = True
                    st.session_state.nutzer_id = int(df_u.iloc[0]['nutzer_id'])
                    st.session_state.rolle = df_u.iloc[0]['rolle']
                    st.rerun()
                else: st.error("Login falsch.")
        
        with t2:
            reg_u = st.text_input("Nutzername", key="reg_u")
            reg_p = st.text_input("Passwort", type="password", key="reg_p")
            reg_v = st.text_input("Vorname", key="reg_v")
            reg_n = st.text_input("Nachname", key="reg_n")
            reg_m = st.text_input("E-Mail", key="reg_m")
            reg_a = st.number_input("Dein Alter", min_value=0, max_value=120, step=1, key="reg_a")
            reg_agb = st.checkbox("Ich akzeptiere die AGB", key="reg_agb")
            
            if st.button("Konto erstellen", width='stretch'):
                if reg_agb and all([reg_u, reg_p, reg_v, reg_n, reg_m]):
                    conn = get_db_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            sql = "INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, alter_wert, rolle) VALUES (%s, %s, %s, %s, %s, %s, 'user')"
                            cursor.execute(sql, (reg_u, reg_p, reg_m, reg_v, reg_n, reg_a))
                            conn.commit()
                            st.success("Erfolg! Bitte jetzt einloggen.")
                            conn.close()
                        except Exception as e: st.error(f"Fehler: {e}")
                else: st.warning("Bitte alles ausfüllen & AGB bestätigen.")

# --- 4. SEITEN-LOGIK ---
if st.session_state.wahl == "📍 Suche":
    display_home_banner()
    st.title("Finde Spielplätze")
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Ort/Adresse", "Varel")
    with c2: km = st.slider("Radius (km)", 1, 50, 15)
    
    if st.button("🔍 Suchen", type="primary"):
        geocoder = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        results = geocoder.geocode(adr + ", Friesland")
        if results:
            lat, lon = results[0]['geometry']['lat'], results[0]['geometry']['lng']
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
    msg = st.text_area("Wie können wir uns verbessern?")
    if st.button("Senden"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO feedback (nutzer_id, nachricht) VALUES (%s, %s)", (st.session_state.nutzer_id, msg))
            conn.commit()
            conn.close()
            st.success("Danke für dein Feedback!")

elif st.session_state.wahl == "🏗️ Vorschlag":
    display_page_header()
    st.title("Einen neuen tollen Ort vorschlagen")
    st.write("Fülle das Formular aus, damit der Admin den Platz prüfen und hinzufügen kann.")

    with st.form("vorschlag_form_erweitert", clear_on_submit=True):
        # 1. Adresse
        name = st.text_input("Name des Spielplatzes/Parks", placeholder="z.B. Tulpengrund-Spielplatz")
        adresse = st.text_input("Genaue Adresse (Straße, Hausnummer, PLZ Varel)", placeholder="z.B. Im Tulpengrund 7, 26316 Varel")

        # 2. Kategorie (Spielplatz, Park, Freizeitpark)
        kategorie = st.radio("Was für eine Art Ort ist es?", ["Spielplatz", "Park", "Freizeitpark"], horizontal=True)

        # 3. Ausstattung (Was ist verfügbar?) multiselect
        verfuegbare_amenities = ["Rutsche", "Schaukel", "Sandkasten", "Seilbahn", "Klettergerüst", "Wasserspiel", "Wippe", "Karussell"]
        ausstattung = st.multiselect("Was gibt es dort vor Ort?", verfuegbare_amenities)

        # 4. Bild senden (st.file_uploader)
        bild_datei = st.file_uploader("Lade ein Bild des Platzes hoch (optional)", type=['jpg', 'jpeg', 'png'])

        ausstattung_str = ",".join(ausstattung)

        if st.form_submit_button("Vorschlag absenden"):
            if not name or not adresse or not kategorie:
                st.error("Bitte fülle mindestens Name, Adresse und Kategorie aus.")
            else:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    bild_daten = None
                    if bild_datei is not None:
                        bild_daten = bild_datei.read() # Wir lesen die binären Daten des Bildes

                    try:
                        sql = """INSERT INTO vorschlaege
                                 (nutzer_id, platz_name, adresse, kategorie, ausstattung, bild)
                                 VALUES (%s, %s, %s, %s, %s, %s)"""
                        cursor.execute(sql, (st.session_state.nutzer_id, name, adresse, kategorie, ausstattung_str, bild_daten))
                        conn.commit()
                        st.success(f"Danke! Dein Vorschlag für '{name}' wurde an den Admin gesendet.")
                        st.balloons()
                    except mysql.connector.Error as err:
                        st.error(f"Fehler beim Speichern: {err}")
                    finally:
                        conn.close()

elif st.session_state.wahl == "🛠️ Admin":
    if st.session_state.rolle == "admin":
        display_page_header()
        st.title("🛠️ Admin-Dashboard")
        tab1, tab2, tab3, tab4 = st.tabs(["👥 Nutzer", "💬 Feedback", "🏗️ Meldungen", "📝 Neue Vorschläge"])
        with tab1:
            st.dataframe(hole_df_aus_db("SELECT * FROM nutzer"))
        with tab2:
            st.dataframe(hole_df_aus_db("SELECT * FROM feedback"))
        with tab3:
            st.dataframe(hole_df_aus_db("SELECT * FROM meldungen"))
        with tab4:
            st.write("**Eingegangene Vorschläge mit Bildern:**")
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM vorschlaege ORDER BY zeitstempel DESC")
                vorschlaege = cursor.fetchall()
                conn.close()

                if vorschlaege:
                    for v in vorschlaege:
                        with st.expander(f"📝 Vorschlag: {v['platz_name']} ({v['kategorie']})"):
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(f"**Adresse:** {v['adresse']}")
                                st.write(f"**Ausstattung:** {v['ausstattung']}")
                                st.write(f"**Eingereicht am:** {v['zeitstempel']}")
                            with col2:
                                if v['bild']:
                                    # Binäre Daten in ein Bild umwandeln
                                    st.image(v['bild'], caption=v['platz_name'], use_container_width=True)
                                else:
                                    st.write("Kein Bild verfügbar.")
                else:
                    st.write("Noch keine neuen Vorschläge.")
