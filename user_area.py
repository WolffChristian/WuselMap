import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
from database_manager import hole_df, sende_vorschlag, sende_feedback, optimiere_bild, aktualisiere_profil

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

# --- DIE UNTER-BEREICHE ---
def show_user_area():
    st.markdown("### 📍 Kletter-Spots suchen")
    adr = st.text_input("Wo suchst du?", "Varel")
    if st.button("🔍 Suchen"):
        st.info(f"Suche läuft für {adr}...")
        # Hier deine Plotly-Karten-Logik einfügen

def show_proposal_area():
    st.markdown("### 💡 Spot vorschlagen")
    with st.form("v_form"):
        v_n = st.text_input("Name*")
        v_s = st.text_input("Straße*")
        v_p = st.text_input("PLZ*")
        v_st = st.text_input("Stadt*")
        v_img = st.file_uploader("Foto", type=["jpg", "png"])
        if st.form_submit_button("Einsenden"):
            if v_n and v_s:
                st.success("Vorschlag eingereicht!")

# --- DAS NEUE PROFIL-DASHBOARD ---
def show_profile_area():
    st.title("👤 Mein Bereich")
    
    # HIER SIND DIE UNTER-BALKEN (Genau wie du wolltest)
    unter_tabs = st.tabs(["⚙️ Meine Daten", "📍 Suche", "💡 Vorschlag"])
    
    with unter_tabs[0]:
        st.subheader("Persönliche Daten")
        df_u = hole_df("nutzer")
        if not df_u.empty and st.session_state.user in df_u['benutzername'].values:
            user_data = df_u[df_u['benutzername'] == st.session_state.user].iloc[0]
            with st.form("p_form"):
                ne = st.text_input("E-Mail", value=user_data['email'])
                nv = st.text_input("Vorname", value=user_data['vorname'])
                nn = st.text_input("Nachname", value=user_data['nachname'])
                if st.form_submit_button("Speichern"):
                    aktualisiere_profil(st.session_state.user, ne, nv, nn, user_data['alter_jahre'], "🧗")
                    st.success("Update!"); st.rerun()
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    with unter_tabs[1]:
        show_user_area()

    with unter_tabs[2]:
        show_proposal_area()

def show_feedback_area():
    st.title("💬 Feedback")
    msg = st.text_area("Deine Nachricht")
    if st.button("Senden"): st.success("Danke!")

def show_legal_area():
    st.title("📄 Rechtliches")
    st.write("Impressum & Datenschutz")
