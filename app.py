import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
import numpy as np
import mysql.connector
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
            ssl_disabled=False # Dieser Befehl hat bei dir funktioniert
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
            st.markdown("---")
            if st.button("📊 Admin-Dashboard", width='stretch'): st.session_state.wahl = "🛠️ Admin"
        
        st.write("---")
        st.markdown(f"Eingeloggt als: **{st.session_state.rolle}**")
        if st.button("🚪 Logout", width='stretch'):
            st.session_state.logged_in = False
            st.session_state.nutzer_id = None
            st.session_state.rolle = "gast"
            st.rerun()
    else:
        t1, t2 = st.tabs(["🔑 Login", "📝 Registrieren"])
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
            reg_a = st.number_input("Alter des Kindes", min_value=0, max_value=18, step=1, key="reg_a")
            reg_agb = st.checkbox("Ich akzeptiere die AGB", key="reg_agb")
            
            if st.button("AGB lesen", key="btn_read_agb_reg"):
                st.session_state.wahl = "📄 Rechtliches"
                st.rerun()

            if st.button("Konto erstellen", width='stretch'):
                if reg_agb and all([reg_u, reg_p, reg_v, reg_n, reg_m]):
                    conn = get_db_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            sql = "INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, alter_kind, rolle) VALUES (%s, %s, %s, %s, %s, %s, 'user')"
                            cursor.execute(sql, (reg_u, reg_p, reg_m, reg_v, reg_n, reg_a))
                            conn.commit()
                            st.success("Erfolg! Bitte jetzt einloggen.")
                            st.balloons()
                            conn.close()
                        except Exception as e: st.error(f"Fehler bei Registrierung: {e}")
                else: st.warning("Bitte alles ausfüllen & AGB bestätigen.")

# --- 4. SEITEN-LOGIK ---
st.warning("🚧 Beta-Modus aktiv.")

if st.session_state.wahl == "📍 Suche":
    display_home_banner()
    st.title("Finde Spielplätze")
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Ort/Adresse", "Varel")
    with c2: km = st.slider("Radius (km)", 1, 50, 15)
    
    if st.button("🔍 Suchen", type="primary"):
        with st.spinner("Suche läuft..."):
            geo = Nominatim(user_agent="KletterKompass").geocode(adr + ", Friesland")
            df = hole_df_aus_db("SELECT * FROM spielplaetze")
            if geo and not df.empty:
                df['distanz'] = df.apply(lambda r: distanz(geo.latitude, geo.longitude, r['lat'], r['lon']), axis=1)
                res = df[df['distanz'] <= km].sort_values('distanz')
                if not res.empty:
                    cl, cm = st.columns([1, 1])
                    with cl:
                        for i, r in res.iterrows():
                            with st.expander(f"📍 {r['standort']} ({round(r['distanz'], 1)} km)"):
                                st.write(f"👶 Alter: {r.get('altersfreigabe', 'n.V.')}")
                                ausl = int(r.get('auslastung', 0))
                                st.progress(ausl / 100, text=f"Auslastung: {ausl}%")
                    with cm:
                        fig = px.scatter_mapbox(res, lat="lat", lon="lon", hover_name="standort", zoom=11)
                        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                        st.plotly_chart(fig, width='stretch')
                else: st.warning("Keine Spielplätze gefunden.")
            else: st.error("Ort nicht gefunden oder Datenbank leer.")

elif st.session_state.wahl == "📄 Rechtliches":
    show_legal_page()

elif st.session_state.wahl == "👤 Profil":
    display_page_header()
    st.title("Mein Profil")
    df_p = hole_df_aus_db("SELECT * FROM nutzer WHERE nutzer_id=%s", (st.session_state.nutzer_id,))
    if not df_p.empty:
        u = df_p.iloc[0]
        st.write(f"**Name:** {u.get('vorname', '')} {u.get('nachname', '')}")
        st.write(f"**E-Mail:** {u.get('email', '')}")
        st.write(f"**Alter des Kindes:** {u.get('alter_kind', 0)} Jahre")
    else: st.error("Bitte logge dich erst ein.")

elif st.session_state.wahl == "💬 Feedback":
    display_page_header()
    st.title("Feedback & Hilfe")
    msg = st.text_area("Wie können wir uns verbessern?")
    if st.button("Absenden"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO feedback (nutzer_id, nachricht) VALUES (%s, %s)", (st.session_state.nutzer_id, msg))
            conn.commit()
            conn.close()
            st.success("Vielen Dank für dein Feedback!")

elif st.session_state.wahl == "🏗️ Vorschlag":
    display_page_header()
    st.title("Neuen Platz melden")
    with st.form("vorschlag_form"):
        p_name = st.text_input("Name des Spielplatzes")
        p_adr = st.text_input("Genaue Adresse oder Koordinaten")
        p_info = st.text_area("Besonderheiten (z.B. Seilbahn, Schatten)")
        if st.form_submit_button("Vorschlag einreichen"):
            st.success("Danke! Wir prüfen deinen Vorschlag und schalten ihn bald frei.")

elif st.session_state.wahl == "🛠️ Admin":
    display_page_header()
    st.title("Admin-Dashboard")
    st.write("Hier kannst du bald gemeldete Plätze freigeben.")
    df_all = hole_df_aus_db("SELECT * FROM nutzer")
    st.write("**Registrierte Nutzer:**")
    st.dataframe(df_all)
