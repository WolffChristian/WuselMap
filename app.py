import streamlit as st
import os
from database_manager import hole_df, hash_passwort, registriere_nutzer
from user_area import show_user_area
from admin_area import show_admin_area

st.set_page_config(page_title="KletterKompass Deutschland", layout="wide")

st.markdown("""
    <style>
    h1, h2, h3, label { color: #2e7d32 !important; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #ffffff !important; border: 2px solid #2e7d32 !important; color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #000000 !important; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label { color: #ffffff !important; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; color: white; border-radius: 5px; }
    .stTabs [aria-selected="true"] { background-color: #2e7d32 !important; }
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
        with t_reg:
            nu, npw, ne = st.text_input("Nutzer*").strip(), st.text_input("PW*", type="password").strip(), st.text_input("Mail*").strip()
            nv, nn, na = st.text_input("Vorname"), st.text_input("Nachname"), st.number_input("Alter", 0, 100, 25)
            agb = st.checkbox("AGB akzeptieren*")
            if st.button("Erstellen"):
                if nu and npw and ne and agb:
                    if registriere_nutzer(nu, npw, ne, nv, nn, na, agb): st.success("Konto bereit!")
                    else: st.error("Name/Mail vergeben.")
    else:
        st.success(f"Moin {st.session_state.user}!")
        if st.button("👤 Mein Profil"): st.session_state.wahl = "👤 Profil"
        if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()

    st.write("---")
    if st.button("📍 Suche"): st.session_state.wahl = "📍 Suche"
    if st.session_state.logged_in and st.session_state.user_role == 'admin':
        if st.button("🛠️ Admin-Bereich"): st.session_state.wahl = "🛠️ Admin"
    if st.button("📄 Rechtliches"): st.session_state.wahl = "📄 Recht"

if st.session_state.wahl == "📍 Suche":
    show_user_area()
elif st.session_state.wahl == "🛠️ Admin":
    show_admin_area()
elif st.session_state.wahl == "👤 Profil":
    st.title("Dein Profil")
    st.info("Hier kannst du bald deine Daten ändern.") # Platzhalter für die Profil-Logik
elif st.session_state.wahl == "📄 Recht":
    st.write("Impressum & Datenschutz")
