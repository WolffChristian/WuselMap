import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
import numpy as np
import mysql.connector
from assets_helper import display_sidebar_logo, display_home_banner, display_page_header

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
            ssl_mode="REQUIRED"
        )
    except Exception as e:
        st.error(f"Datenbank-Fehler: {e}")
        return None

# Hilfsfunktion für SQL-Abfragen direkt in DataFrames
def hole_df_aus_db(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Fehler bei Abfrage: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# --- 2. HILFSFUNKTIONEN ---
def get_weather(lat, lon):
    # Dummy-Wetter für die Beta-Phase
    return "20°C, Sonnig", "01d"

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

def sende_bewertung(spiel_id, sterne):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO bewertungen (spiel_id, nutzer_id, sterne) VALUES (%s, %s, %s)"
            cursor.execute(query, (spiel_id, st.session_state.nutzer_id, sterne))
            conn.commit()
            st.toast(f"Top! {sterne} Sterne gespeichert! 🛝")
            cursor.close()
            conn.close()
        except Exception as e:
            st.error(f"Bewertung konnte nicht gespeichert werden: {e}")

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'nutzer_id' not in st.session_state: st.session_state.nutzer_id = None
if 'rolle' not in st.session_state: st.session_state.rolle = "gast"
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# --- 4. SIDEBAR ---
with st.sidebar:
    display_sidebar_logo()  
    st.info("✨ **BETA-PHASE**")
    
    if st.button("📍 Spielplatz suchen", width='stretch', key="nav_suche_global"):
        st.session_state.wahl = "📍 Suche"
    
    st.write("---")

    if st.session_state.logged_in:
        if st.button("👤 Mein Profil", width='stretch', key="nav_profil"): 
            st.session_state.wahl = "👤 Profil"
        if st.button("💬 Feedback geben", width='stretch', key="nav_feedback"): 
            st.session_state.wahl = "💬 Feedback"
        if st.button("🏗️ Neuen Platz melden", width='stretch', key="nav_vorschlag"): 
            st.session_state.wahl = "🏗️ Vorschlag"
        
        if st.session_state.rolle == "admin":
            st.markdown("---")
            if st.button("📊 Admin-Dashboard", width='stretch', key="nav_admin"): 
                st.session_state.wahl = "🛠️ Admin"
        
        st.write("---")
        st.markdown(f"Eingeloggt als: **{st.session_state.rolle}**")
        if st.button("🚪 Logout", width='stretch', key="nav_logout"):
            st.session_state.logged_in = False
            st.session_state.nutzer_id = None
            st.session_state.rolle = "gast"
            st.rerun()
    else:
        t1, t2 = st.tabs(["🔑 Login", "📝 Registrieren"])
        with t1:
            u = st.text_input("User", key="l_u")
            p = st.text_input("Passwort", type="password", key="l_p")
            if st.button("Anmelden", width='stretch', key="btn_login"):
                df_user = hole_df_aus_db("SELECT nutzer_id, rolle FROM nutzer WHERE benutzername=%s AND passwort=%s", (u, p))
                if not df_user.empty:
                    st.session_state.logged_in = True
                    st.session_state.nutzer_id = int(df_user.iloc[0]['nutzer_id'])
                    st.session_state.rolle = df_user.iloc[0]['rolle']
                    st.rerun()
                else: st.error("Login falsch.")
        
        with t2:
            reg_u = st.text_input("Nutzername", key="reg_u")
            reg_p = st.text_input("Passwort", type="password", key="reg_p")
            reg_v = st.text_input("Vorname", key="reg_v")
            reg_n = st.text_input("Nachname", key="reg_n")
            reg_m = st.text_input("E-Mail", key="reg_m")
            reg_agb = st.checkbox("AGB akzeptieren", key="reg_agb")
            
            if st.button("Konto erstellen", width='stretch', key="btn_reg_submit"):
                if reg_agb and all([reg_u, reg_p, reg_v, reg_n, reg_m]):
                    conn = get_db_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, rolle) VALUES (%s, %s, %s, %s, %s, 'user')", 
                                           (reg_u, reg_p, reg_m, reg_v, reg_n))
                            conn.commit()
                            st.success("Erfolg! Bitte jetzt einloggen.")
                            st.balloons()
                            conn.close()
                        except: st.error("Nutzername oder E-Mail bereits vergeben.")
                else: st.warning("Bitte alles ausfüllen & AGB bestätigen.")

# --- 5. HAUPTSEITE ---
st.warning("🚧 Beta-Modus aktiv.")

if st.session_state.wahl == "📍 Suche":
    display_home_banner()
    st.title("Finde Spielplätze")
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Ort/Adresse", "Varel")
    with c2: km = st.slider("Radius (km)", 1, 50, 15)
    
    if st.button("🔍 Suchen", type="primary", key="btn_search"):
        with st.spinner("Suche läuft..."):
            geo = Nominatim(user_agent="KletterKompass").geocode(adr + ", Friesland")
            df = hole_df_aus_db("SELECT * FROM spielplaetze")
            
            if geo and not df.empty:
                df['distanz'] = df.apply(lambda r: distanz(geo.latitude, geo.longitude, r['lat'], r['lon']), axis=1)
                res = df[df['distanz'] <= km].sort_values('distanz')
                
                if res.empty:
                    st.warning(f"Keine Ergebnisse für '{adr}' im Umkreis gefunden.")
                else:
                    cl, cm = st.columns([1, 1])
                    with cl:
                        for i, r in res.iterrows():
                            with st.expander(f"📍 {r['standort']} ({round(r['distanz'], 1)} km)"):
                                wt, wi = get_weather(r['lat'], r['lon'])
                                st.write(f"🌡️ {wt} | 👶 {r.get('altersfreigabe', 'n.V.')}")
                                ausl = int(r.get('auslastung', 0))
                                st.progress(ausl / 100, text=f"Auslastung: {ausl}%")
                                
                                if st.session_state.logged_in:
                                    st.write("**Bewertung:**")
                                    b_cols = st.columns(5)
                                    for val in range(1, 6):
                                        if b_cols[val-1].button(f"{val} 🛝", key=f"r_{r['spiel_id']}_{val}"):
                                            sende_bewertung(r['spiel_id'], val)
                    with cm:
                        fig = px.scatter_mapbox(res, lat="lat", lon="lon", hover_name="standort", zoom=11)
                        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                        st.plotly_chart(fig, width='stretch')
            else: st.error("Ort nicht gefunden oder Datenbank leer.")

elif st.session_state.wahl == "👤 Profil":
    display_page_header()
    st.title("Mein Profil")
    user_df = hole_df_aus_db("SELECT * FROM nutzer WHERE nutzer_id=%s", (st.session_state.nutzer_id,))
    if not user_df.empty:
        u = user_df.iloc[0]
        with st.form("edit_profil"):
            v = st.text_input("Vorname", value=u.get('vorname', ''))
            n = st.text_input("Nachname", value=u.get('nachname', ''))
            m = st.text_input("E-Mail", value=u.get('email', ''))
            if st.form_submit_button("Speichern"):
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE nutzer SET vorname=%s, nachname=%s, email=%s WHERE nutzer_id=%s", (v, n, m, st.session_state.nutzer_id))
                    conn.commit()
                    conn.close()
                    st.success("Profil aktualisiert!")
    else: st.error("Bitte logge dich erst ein.")

elif st.session_state.wahl == "💬 Feedback":
    display_page_header()
    st.title("Feedback & Hilfe")
    msg = st.text_area("Nachricht")
    if st.button("Absenden"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO feedback (nutzer_id, nachricht) VALUES (%s, %s)", (st.session_state.nutzer_id or 0, msg))
            conn.commit()
            conn.close()
            st.success("Gesendet!")

elif st.session_state.wahl == "🏗️ Vorschlag":
    display_page_header()
    st.title("Neuen Platz melden")
    with st.form("vorschlag"):
        name = st.text_input("Name des Platzes")
        adr_v = st.text_input("Genaue Adresse")
        if st.form_submit_button("Vorschlag senden"):
            st.success("Vielen Dank! Wir prüfen den Vorschlag.")

elif st.session_state.wahl == "🛠️ Admin":
    display_page_header()
    st.title("Admin Dashboard")
    df_v = hole_df_aus_db("SELECT * FROM spielplaetze WHERE status='ausstehend'")
    if df_v.empty: st.info("Keine neuen Vorschläge zur Prüfung.")
    else:
        for i, v in df_v.iterrows():
            st.write(f"Prüfung: {v['standort']}")
            if st.button(f"✅ Freigeben {v['spiel_id']}"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE spielplaetze SET status='aktiv' WHERE spiel_id=%s", (v['spiel_id'],))
                conn.commit()
                conn.close()
                st.rerun()
