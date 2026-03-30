import streamlit as st
import pandas as pd
from database_manager import hole_daten, neue_zeile_schreiben, hash_passwort
import uuid
from datetime import datetime

# 1. Konfiguration & Design
st.set_page_config(page_title="Kletterkompass", page_icon="🧗", layout="wide")

# Eigenes CSS für den Look
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e7d32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. Session State (Wer ist eingeloggt?)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""

# --- SIDEBAR: LOGIN & REGISTRIERUNG ---
st.sidebar.title("🧗 Kletterkompass")

if not st.session_state.logged_in:
    menu = ["Login", "Registrieren"]
    choice = st.sidebar.selectbox("Menü", menu)

    if choice == "Login":
        u = st.sidebar.text_input("Nutzername")
        p = st.sidebar.text_input("Passwort", type="password")
        if st.sidebar.button("Einloggen"):
            df_nutzer = hole_daten("nutzer")
            if not df_nutzer.empty:
                user = df_nutzer[(df_nutzer['benutzername'] == u) & (df_nutzer['passwort'] == hash_passwort(p))]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = u
                    st.rerun()
                else:
                    st.sidebar.error("Falsche Daten.")

    else:
        new_u = st.sidebar.text_input("Wunsch-Nutzername")
        new_p = st.sidebar.text_input("Wunsch-Passwort", type="password")
        new_e = st.sidebar.text_input("E-Mail")
        if st.sidebar.button("Konto erstellen"):
            neuer_nutzer = {
                "nutzer_id": str(uuid.uuid4())[:8],
                "benutzername": new_u,
                "passwort": hash_passwort(new_p),
                "email": new_e,
                "rolle": "user",
                "avatar_emoji": "🧗"
            }
            neue_zeile_schreiben("nutzer", neuer_nutzer)
            st.sidebar.success("Konto erstellt! Bitte einloggen.")
else:
    st.sidebar.success(f"Eingeloggt als: {st.session_state.user_name}")
    if st.sidebar.button("Abmelden"):
        st.session_state.logged_in = False
        st.rerun()

# --- HAUPTBEREICH ---
st.title("Finde deinen nächsten Spot")

# Karte anzeigen
try:
    df_plaetze = hole_daten("spielplaetze")
    if not df_plaetze.empty:
        # Wir benennen 'lad' und 'Lohn' intern für Streamlit um
        map_df = df_plaetze.rename(columns={'lad': 'lat', 'Lohn': 'lon'})
        st.map(map_df)
        
        # Liste anzeigen
        with st.expander("Alle Standorte anzeigen"):
            st.table(df_plaetze[['Standort', 'Spiel ID']])
except:
    st.info("Noch keine Standorte auf der Karte.")

# --- NEUEN SPOT VORSCHLAGEN (Nur wenn eingeloggt) ---
if st.session_state.logged_in:
    st.divider()
    st.subheader("Neuen Spot vorschlagen")
    with st.form("vorschlag_form"):
        name = st.text_input("Name des Spielplatzes / Parks")
        adr = st.text_input("Adresse")
        beschr = st.text_area("Was ist dort besonders? (Toben, Kraxeln...)")
        submitted = st.form_submit_button("Vorschlag abschicken")
        
        if submitted:
            neuer_v = {
                "v_id": str(uuid.uuid4())[:8],
                "platz_name": name,
                "adresse": adr,
                "beschreibung": beschr,
                "status": "offen"
            }
            neue_zeile_schreiben("vorschlaege", neuer_v)
            st.balloons()
            st.success("Danke! Wir prüfen deinen Vorschlag.")
else:
    st.info("Logge dich ein, um neue Orte vorzuschlagen und die Community zu unterstützen.")
