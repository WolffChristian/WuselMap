import streamlit as st
import pandas as pd
from database_manager import hole_df, sende_vorschlag, sende_feedback, optimiere_bild, aktualisiere_profil

def show_user_area():
    st.subheader("📍 Spots finden")
    st.info("Kartensuche ist aktiv.")
    # Hier kommt dein originaler Karten-Code wieder rein

def show_proposal_area():
    st.subheader("💡 Spot vorschlagen")
    with st.form("v_form", clear_on_submit=True):
        v_n = st.text_input("Name des Spots*")
        v_s = st.text_input("Straße & Hausnr.*")
        v_p = st.text_input("PLZ*")
        v_st = st.text_input("Stadt*", value="Varel")
        v_alt = st.selectbox("Altersgruppe", ["0-3", "3-12", "Alle"])
        v_img = st.file_uploader("Foto hochladen", type=["jpg", "png", "jpeg"])
        ds = st.checkbox("Ich bestätige: Keine Personen auf dem Foto erkennbar*")
        
        if st.form_submit_button("Einsenden"):
            if v_n and v_s and v_p and v_st and ds:
                bild_data = optimiere_bild(v_img)
                if sende_vorschlag(v_n, v_s, v_alt, st.session_state.user, "Niedersachsen", v_p, v_st, bild_data, ds):
                    st.success("Danke! Spot wird geprüft.")
            else: st.warning("Pflichtfelder (*) fehlen!")

def show_profile_area():
    st.title("👤 Mein Bereich")
    sub_tabs = st.tabs(["⚙️ Profil-Daten", "📍 Suche", "💡 Vorschlag"])
    
    with sub_tabs[0]:
        df_u = hole_df("nutzer")
        user_data = df_u[df_u['benutzername'] == st.session_state.user].iloc[0]
        with st.form("p_data"):
            ne = st.text_input("E-Mail", value=user_data['email'])
            nv = st.text_input("Vorname", value=user_data['vorname'])
            nn = st.text_input("Nachname", value=user_data['nachname'])
            na = st.number_input("Alter", value=int(user_data['alter_jahre']))
            emo = st.selectbox("Profil-Emoji", ["🧗", "🤸", "🦁", "🚀"])
            if st.form_submit_button("Speichern"):
                aktualisiere_profil(st.session_state.user, ne, nv, nn, na, emo)
                st.success("Daten aktualisiert!"); st.rerun()
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.query_params.clear() # Löscht den "Dauer-Login"
            st.session_state.logged_in = False
            st.rerun()

    with sub_tabs[1]: show_user_area()
    with sub_tabs[2]: show_proposal_area()

def show_feedback_area():
    st.title("💬 Feedback")
    with st.form("f_form"):
        msg = st.text_area("Deine Nachricht")
        if st.form_submit_button("Absenden"):
            if msg and sende_feedback(st.session_state.user, msg):
                st.success("Vielen Dank!"); st.rerun()

def show_legal_area():
    st.title("📄 Rechtliches")
    st.write("Impressum & Datenschutz Christian Wolff, Varel")
