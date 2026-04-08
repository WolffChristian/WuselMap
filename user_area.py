import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from database_manager import hole_df, sende_vorschlag, sende_feedback, optimiere_bild, aktualisiere_profil

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

def show_user_area():
    st.markdown("### 📍 Spots finden")
    adr = st.text_input("Ort", "Varel")
    if st.button("🔍 Karte laden"):
        st.info("Suche läuft...")

def show_proposal_area():
    st.markdown("### 💡 Spot melden")
    with st.form("v_form", clear_on_submit=True):
        v_n = st.text_input("Name*")
        v_s = st.text_input("Straße*")
        v_img = st.file_uploader("Foto", type=["jpg", "png", "jpeg"])
        if st.form_submit_button("Einsenden"):
            if v_n and v_s:
                sende_vorschlag(v_n, v_s, "Alle", st.session_state.user, "Niedersachsen", "26316", "Varel", optimiere_bild(v_img), True)
                st.success("Erfolg!")

def show_profile_area():
    st.title("👤 Mein Bereich")
    # UNTER-KATEGORIEN (Slider)
    sub_tabs = st.tabs(["⚙️ Daten", "📍 Suche", "💡 Vorschlag"])
    
    with sub_tabs[0]:
        df_u = hole_df("nutzer")
        if not df_u.empty:
            user_data = df_u[df_u['benutzername'] == st.session_state.user].iloc[0]
            with st.form("p_data"):
                nv = st.text_input("Vorname", value=user_data.get('vorname', ''))
                nn = st.text_input("Nachname", value=user_data.get('nachname', ''))
                if st.form_submit_button("Speichern"):
                    aktualisiere_profil(st.session_state.user, user_data['email'], nv, nn, user_data['alter_jahre'], "🧗")
                    st.success("Update!"); st.rerun()
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False; st.rerun()

    with sub_tabs[1]: show_user_area()
    with sub_tabs[2]: show_proposal_area()

def show_feedback_area():
    st.title("💬 Feedback")
    msg = st.text_area("Nachricht")
    if st.button("Senden"):
        if sende_feedback(st.session_state.user, msg): st.success("Danke!")

def show_legal_area():
    st.title("📄 Recht")
    st.write("Impressum Christian Wolff")
