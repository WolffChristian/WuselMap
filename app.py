import streamlit as st
import os
from database_manager import hole_df, hash_passwort, registriere_nutzer
from user_area import show_user_area, show_proposal_area, show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

APP_NAME = "KletterKompass"

# WICHTIG: Sidebar auf 'collapsed' setzen, damit sie am Handy einklappt
st.set_page_config(
    page_title=APP_NAME, 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Dein Styling beibehalten
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
    else:
        st.success(f"Moin {st.session_state.user}!")
        # Durch st.rerun() nach dem Klick schließt sich die Sidebar wegen 'initial_sidebar_state="collapsed"'
        if st.button("📍 Spot suchen"): st.session_state.wahl = "📍 Suche"; st.rerun()
        if st.button("💡 Spot vorschlagen"): st.session_state.wahl = "💡 Vorschlag"; st.rerun()
        if st.button("👤 Mein Profil"): st.session_state.wahl = "👤 Profil"; st.rerun()
        if st.button("💬 Feedback"): st.session_state.wahl = "💬 Feedback"; st.rerun()
        
        if st.session_state.user_role == 'admin':
            if st.button("🛠️ Admin-Bereich"): st.session_state.wahl = "🛠️ Admin"; st.rerun()
            
        if st.button("📄 Rechtliches"): st.session_state.wahl = "📄 Recht"; st.rerun()
        if st.button("🚪 Logout"): 
            st.session_state.logged_in = False
            st.session_state.wahl = "📍 Suche"
            st.rerun()

# Routing
if st.session_state.wahl == "📍 Suche": show_user_area()
elif st.session_state.wahl == "💡 Vorschlag": show_proposal_area()
elif st.session_state.wahl == "👤 Profil": show_profile_area()
elif st.session_state.wahl == "💬 Feedback": show_feedback_area()
elif st.session_state.wahl == "🛠️ Admin": show_admin_area()
elif st.session_state.wahl == "📄 Recht": show_legal_area()
