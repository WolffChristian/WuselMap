import streamlit as st
import os
from database_manager import hole_df, hash_passwort, registriere_nutzer
from user_area import show_user_area, show_proposal_area, show_profile_area, show_feedback_area
from admin_area import show_admin_area

st.set_page_config(page_title="KletterKompass Deutschland", layout="wide")

st.markdown("""
    <style>
    h1, h2, h3, label { color: #2e7d32 !important; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    [data-testid="stSidebar"] { background-color: #000000 !important; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = 'guest'
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

with st.sidebar:
    if os.path.exists("assets/Kletterkompass_Logo.png"): st.image("assets/Kletterkompass_Logo.png", width=180)
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
    else:
        st.success(f"Moin {st.session_state.user}!")
        if st.button("👤 Mein Profil"): st.session_state.wahl = "👤 Profil"
        if st.button("💡 Spielplatz vorschlagen"): st.session_state.wahl = "💡 Vorschlag"
        if st.button("💬 Feedback geben"): st.session_state.wahl = "💬 Feedback"
        if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()

    st.write("---")
    if st.button("📍 Spielplatz suchen"): st.session_state.wahl = "📍 Suche"
    if st.session_state.logged_in and st.session_state.user_role == 'admin':
        if st.button("🛠️ Admin-Bereich"): st.session_state.wahl = "🛠️ Admin"
    if st.button("📄 Rechtliches"): st.session_state.wahl = "📄 Recht"

# Routing
if st.session_state.wahl == "📍 Suche":
    show_user_area()
elif st.session_state.wahl == "💡 Vorschlag":
    show_proposal_area()
elif st.session_state.wahl == "👤 Profil":
    show_profile_area()
elif st.session_state.wahl == "💬 Feedback":
    show_feedback_area()
elif st.session_state.wahl == "🛠️ Admin":
    show_admin_area()
elif st.session_state.wahl == "📄 Recht":
    st.title("Rechtliches")
    st.write("Impressum & Datenschutz")
