import streamlit as st
import os
from database_manager import hole_df, hash_passwort, registriere_nutzer
from user_area import show_user_area, show_proposal_area, show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

APP_NAME = "KletterKompass"
st.set_page_config(page_title=APP_NAME, layout="wide")

# Styling
st.markdown("""
    <style>
    h1, h2, h3, label { color: #2e7d32 !important; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; width: 100%; border: none; }
    [data-testid="stSidebar"] { background-color: #000000 !important; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = 'guest'
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

with st.sidebar:
    if os.path.exists("assets/Kletterkompass_Logo.png"):
        st.image("assets/Kletterkompass_Logo.png", use_container_width=True)
    else:
        st.title(f"🧗 {APP_NAME}")
    
    st.write("---")

    if not st.session_state.logged_in:
        t_log, t_reg = st.tabs(["🔐 Login", "📝 Registrieren"])
        
        with t_log:
            u_in = st.text_input("Nutzername", key="l_u").strip()
            p_in = st.text_input("Passwort", type="password", key="l_p").strip()
            if st.button("Anmelden"):
                df_n = hole_df("nutzer")
                if not df_n.empty:
                    match = df_n[(df_n['benutzername'] == u_in) & (df_n['passwort'] == hash_passwort(p_in))]
                    if not match.empty:
                        st.session_state.logged_in = True
                        st.session_state.user = u_in
                        st.session_state.user_role = match.iloc[0]['rolle']
                        st.rerun()
                    else: st.error("Login falsch.")
        
        with t_reg:
            st.subheader("Neu hier?")
            r_u = st.text_input("Nutzername*", key="reg_u").strip()
            r_e = st.text_input("E-Mail*", key="reg_e").strip()
            r_p = st.text_input("Passwort*", type="password", key="reg_p").strip()
            r_v = st.text_input("Vorname", key="reg_v").strip()
            r_n = st.text_input("Nachname", key="reg_n").strip()
            r_a = st.number_input("Alter", 0, 100, 25, key="reg_a")
            r_agb = st.checkbox("AGB & Datenschutz akzeptieren*", key="reg_agb")
            
            if st.button("Konto erstellen"):
                if r_u and r_p and r_e and r_agb:
                    if registriere_nutzer(r_u, r_p, r_e, r_v, r_n, r_a, r_agb):
                        st.success("Erfolg! Bitte logge dich jetzt ein.")
                    else: st.error("Nutzername oder E-Mail bereits vergeben.")
                else: st.warning("Pflichtfelder (*) ausfüllen!")
    else:
        st.success(f"Moin {st.session_state.user}!")
        if st.button("👤 Mein Profil"): st.session_state.wahl = "👤 Profil"
        if st.button("💡 Spot vorschlagen"): st.session_state.wahl = "💡 Vorschlag"
        if st.button("💬 Feedback"): st.session_state.wahl = "💬 Feedback"
        if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()

    st.write("---")
    if st.button("📍 Spot suchen"): st.session_state.wahl = "📍 Suche"
    if st.session_state.logged_in and st.session_state.user_role == 'admin':
        if st.button("🛠️ Admin-Bereich"): st.session_state.wahl = "🛠️ Admin"
    if st.button("📄 Rechtliches"): st.session_state.wahl = "📄 Recht"

# Routing
if st.session_state.wahl == "📍 Suche": show_user_area()
elif st.session_state.wahl == "💡 Vorschlag": show_proposal_area()
elif st.session_state.wahl == "👤 Profil": show_profile_area()
elif st.session_state.wahl == "💬 Feedback": show_feedback_area()
elif st.session_state.wahl == "🛠️ Admin": show_admin_area()
elif st.session_state.wahl == "📄 Recht": show_legal_area()
