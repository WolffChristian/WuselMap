import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from geopy.geocoders import Nominatim
import numpy as np
import time
from assets_helper import display_sidebar_logo, display_home_banner, display_page_header
import mysql.connector

# Verbindung zur Aiven-Datenbank herstellen
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            port=int(st.secrets["DB_PORT"]),
            database=st.secrets["DB_NAME"]
        )
        return conn
    except Exception as e:
        st.error(f"Datenbank-Fehler: {e}")
        return None


# --- 1. SETUP ---
BACKEND_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="KletterKompass BETA", layout="wide")

# --- 2. HILFSFUNKTIONEN ---
def hole_daten(endpoint):
    try:
        res = requests.get(f"{BACKEND_URL}{endpoint}", timeout=3)
        return pd.DataFrame(res.json()) if res.status_code == 200 else pd.DataFrame()
    except: return pd.DataFrame()

def get_weather(lat, lon):
    try:
        res = requests.get(f"{BACKEND_URL}/wetter/{lat}/{lon}", timeout=2).json()
        return f"{res['main']['temp']}°C, {res['weather'][0]['description']}", res['weather'][0]['icon']
    except: return "Wetter n.V.", None

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

def sende_bewertung(spiel_id, sterne):
    payload = {"sterne": sterne, "spiel_id": spiel_id, "nutzer_id": st.session_state.nutzer_id}
    res = requests.post(f"{BACKEND_URL}/bewertungen", json=payload)
    if res.status_code == 200:
        st.toast(f"Top! {sterne} Rutschen gespeichert! 🛝")
    else:
        st.error("Bewertung konnte nicht gespeichert werden.")

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'nutzer_id' not in st.session_state: st.session_state.nutzer_id = 1
if 'rolle' not in st.session_state: st.session_state.rolle = "gast"
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# --- 4. SIDEBAR ---
with st.sidebar:
    display_sidebar_logo()  
    st.info("✨ **BETA-PHASE**")
    
    # Navigation für alle
    if st.button("📍 Spielplatz suchen", width='stretch', key="nav_suche_global"):
        st.session_state.wahl = "📍 Suche"
    
    st.write("---")

    if st.session_state.logged_in:
        # Menü für eingeloggte User
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
            st.session_state.rolle = "gast"
            st.rerun()
    else:
        # LOGIN & REGISTER
        t1, t2 = st.tabs(["🔑 Login", "📝 Registrieren"])
        with t1:
            u = st.text_input("User", key="l_u")
            p = st.text_input("Passwort", type="password", key="l_p")
            if st.button("Anmelden", width='stretch', key="btn_login"):
                res = requests.post(f"{BACKEND_URL}/login", json={"username":u, "password":p}).json()
                if res.get("status") == "success":
                    st.session_state.logged_in = True
                    st.session_state.nutzer_id = res.get("nutzer_id")
                    st.session_state.rolle = res.get("rolle")
                    st.rerun()
                else: st.error("Login falsch.")
        
        with t2:
            # --- HIER SIND DIE FEHLENDEN FELDER ---
            reg_u = st.text_input("Nutzername", key="reg_u")
            reg_p = st.text_input("Passwort", type="password", key="reg_p")
            reg_v = st.text_input("Vorname", key="reg_v")
            reg_n = st.text_input("Nachname", key="reg_n")
            reg_m = st.text_input("E-Mail", key="reg_m")
            reg_a = st.number_input("Alter", 12, 99, 25, key="reg_a")
            reg_g = st.selectbox("Geschlecht", ["männlich", "weiblich", "divers"], key="reg_g")
            reg_agb = st.checkbox("AGB & Datenschutz akzeptieren", key="reg_agb")
            
            if st.button("Konto erstellen", width='stretch', key="btn_reg_submit"):
                if reg_agb and all([reg_u, reg_p, reg_v, reg_n, reg_m]):
                    payload = {
                        "benutzername": reg_u, "passwort": reg_p, "email": reg_m,
                        "vorname": reg_v, "nachname": reg_n, "alter_wert": reg_a,
                        "geschlecht": reg_g, "agb": reg_agb
                    }
                    r_res = requests.post(f"{BACKEND_URL}/register", json=payload)
                    if r_res.status_code == 200:
                        st.success("Erfolg! Bitte jetzt einloggen.")
                        st.balloons()
                    else: st.error("Fehler bei der Registrierung.")
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
        geo = Nominatim(user_agent="KletterKompass").geocode(adr + ", Friesland")
        df = hole_daten("/spielplaetze")
        
        if geo and not df.empty:
            df['distanz'] = df.apply(lambda r: distanz(geo.latitude, geo.longitude, r['lat'], r['lon']), axis=1)
            res = df[df['distanz'] <= km].sort_values('distanz')
            
            cl, cm = st.columns([1, 1])
            with cl:
                for i, r in res.iterrows():
                    with st.expander(f"📍 {r['standort']} ({round(r['distanz'], 1)} km)"):
                        wt, wi = get_weather(r['lat'], r['lon'])
                        if wi: st.image(f"http://openweathermap.org/img/wn/{wi}.png", width=50)
                        st.write(f"🌡️ {wt} | 👶 {r['altersfreigabe']}")
                        
                        ausl = int(r.get('auslastung', 0))
                        st.write(f"Auslastung: {ausl}%")
                        st.progress(ausl / 100)
                        
                        st.write("**Bewertung:**")
                        b_cols = st.columns(5)
                        for val in range(1, 6):
                            if b_cols[val-1].button(f"{val} 🛝", key=f"r_{r['spiel_id']}_{val}"):
                                sende_bewertung(r['spiel_id'], val)
            with cm:
                fig = px.scatter_mapbox(res, lat="lat", lon="lon", hover_name="standort", zoom=11)
                fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                st.plotly_chart(fig, use_container_width=True)

elif st.session_state.wahl == "👤 Profil":
    display_page_header()
    st.title("Mein Profil")
    res = requests.get(f"{BACKEND_URL}/profil/{st.session_state.nutzer_id}")
    if res.status_code == 200 and res.json() is not None:
        user = res.json()
        with st.form("edit_profil"):
            v = st.text_input("Vorname", value=user.get('vorname', ''))
            n = st.text_input("Nachname", value=user.get('nachname', ''))
            m = st.text_input("E-Mail", value=user.get('email', ''))
            a = st.number_input("Alter", 12, 99, value=user.get('alter_wert', 25))
            if st.form_submit_button("Speichern"):
                payload = {"benutzername":"", "passwort":"", "vorname":v, "nachname":n, "email":m, "alter_wert":a, "geschlecht":user.get('geschlecht','divers'), "agb":True}
                requests.put(f"{BACKEND_URL}/profil/update/{st.session_state.nutzer_id}", json=payload)
                st.success("Profil aktualisiert!")
    else: st.error("Profil nicht gefunden.")

elif st.session_state.wahl == "💬 Feedback":
    display_page_header()
    st.title("Feedback & Hilfe")
    msg = st.text_area("Nachricht oder Fehlermeldung")
    if st.button("Absenden", key="btn_feedback"):
        requests.post(f"{BACKEND_URL}/feedback", json={"nutzer_id": st.session_state.nutzer_id, "nachricht": msg})
        st.success("Gesendet!")

elif st.session_state.wahl == "🏗️ Vorschlag":
    display_page_header()
    st.title("Neuen Platz melden")
    with st.form("vorschlag"):
        name = st.text_input("Name")
        adr_v = st.text_input("Adresse")
        if st.form_submit_button("Vorschlag senden"):
            st.success("Vielen Dank!")

elif st.session_state.wahl == "🛠️ Admin":
    display_page_header()
    st.title("Admin Dashboard")
    df_v = hole_daten("/admin/vorschlaege")
    if df_v.empty: st.info("Keine Vorschläge.")
    else:
        for i, v in df_v.iterrows():
            st.write(f"Vorschlag: {v['standort']}")
            if st.button(f"✅ Freigeben {v['spiel_id']}", key=f"f_{v['spiel_id']}"):
                requests.put(f"{BACKEND_URL}/admin/freigeben/{v['spiel_id']}")
                st.rerun()
