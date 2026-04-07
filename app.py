import streamlit as st
import os
from database_manager import hole_df, hash_passwort, registriere_nutzer
from user_area import show_user_area
from admin_area import show_admin_area

# --- SETUP & DESIGN ---
st.set_page_config(page_title="KletterKompass Deutschland", layout="wide")

st.markdown("""
    <style>
    h1, h2, h3, label { color: #2e7d32 !important; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; font-weight: bold; width: 100%; border: none; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input { background-color: #ffffff !important; border: 2px solid #2e7d32 !important; color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #000000 !important; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label { color: #ffffff !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; color: white; border-radius: 5px; margin-right: 5px; }
    .stTabs [aria-selected="true"] { background-color: #2e7d32 !important; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = 'guest'
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"
if 'forgot_pw' not in st.session_state: st.session_state.forgot_pw = False

# --- SIDEBAR ---
with st.sidebar:
    logo_path = "assets/Kletterkompass_Logo.png"
    if os.path.exists(logo_path): st.image(logo_path, width=180)
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
            nu = st.text_input("Nutzer*", key="r_u").strip()
            npw = st.text_input("PW*", type="password", key="r_p").strip()
            ne = st.text_input("Mail*", key="r_e").strip()
            nv, nn, na = st.text_input("Vorname"), st.text_input("Nachname"), st.number_input("Alter", 0, 100, 25)
            agb = st.checkbox("AGB akzeptieren*")
            if st.button("Erstellen"):
                if nu and npw and ne and agb:
                    if registriere_nutzer(nu, npw, ne, nv, nn, na, agb): st.success("Konto bereit!")
                    else: st.error("Fehler.")
    else:
        st.success(f"Moin {st.session_state.user}!")
        if st.button("🚪 Logout"): 
            st.session_state.logged_in = False
            st.rerun()

    st.write("---")
    if st.button("📍 Spielplatz suchen"): st.session_state.wahl = "📍 Suche"
    
    # ADMIN BUTTON (Prüfung der Rolle)
    if st.session_state.logged_in and st.session_state.user_role == 'admin':
        if st.button("🛠️ Admin-Bereich"): st.session_state.wahl = "🛠️ Admin"
    
    if st.button("📄 Rechtliches"): st.session_state.wahl = "📄 Recht"

# --- LOGIK: WELCHE DATEI ANZEIGEN? ---
if st.session_state.wahl == "📍 Suche":
    show_user_area()
elif st.session_state.wahl == "🛠️ Admin":
    show_admin_area()
elif st.session_state.wahl == "📄 Recht":
    st.title("Rechtliches")
    st.write("Impressum & Datenschutz")
