import streamlit as st
from database_manager import hole_df, hash_passwort
from user_area import show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

# 1. Konfiguration
st.set_page_config(page_title="KletterKompass", layout="wide")

# 2. SLIM-DESIGN CSS
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    h1 { color: #2e7d32 !important; font-size: 22px !important; text-align: center; }

    /* BALKEN SCHMALER MACHEN */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        height: 35px;
        background-color: #eeeeee; 
        border-radius: 6px 6px 0 0;
        padding: 4px 12px;
        border: 1px solid #cccccc;
    }
    .stTabs [data-baseweb="tab"] p {
        color: #333333 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    .stTabs [aria-selected="true"] { background-color: #2e7d32 !important; }
    .stTabs [aria-selected="true"] p { color: #ffffff !important; }

    /* Buttons grün */
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

def main():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_role' not in st.session_state: st.session_state.user_role = 'guest'

    # --- LOGIN BEREICH ---
    if not st.session_state.logged_in:
        st.title("🧗 KletterKompass Login")
        u_in = st.text_input("Nutzername", key="l_u").strip().lower()
        p_in = st.text_input("Passwort", type="password", key="l_p")
        
        if st.button("Anmelden", use_container_width=True):
            df_n = hole_df("nutzer")
            if not df_n.empty:
                match = df_n[
                    (df_n['benutzername'].str.lower() == u_in) & 
                    (df_n['passwort'] == hash_passwort(p_in))
                ]
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user = match.iloc[0]['benutzername']
                    st.session_state.user_role = match.iloc[0]['rolle']
                    st.rerun()
                else:
                    st.error("Login falsch.")
    
    # --- HAUPTMENÜ (NACH LOGIN) ---
    else:
        # Nur noch 3-4 Haupt-Balken oben
        menu = ["👤 Mein Bereich", "💬 Feedback"]
        if st.session_state.user_role == 'admin':
            menu.append("🛠️ Admin")
        menu.append("📄 Recht")
        
        main_tabs = st.tabs(menu)

        with main_tabs[0]:
            # Hier landen User -> zeigt Profil + Suche + Vorschlag
            show_profile_area()

        with main_tabs[1]:
            show_feedback_area()

        if st.session_state.user_role == 'admin':
            with main_tabs[2]: show_admin_area()
            with main_tabs[3]: show_legal_area()
        else:
            with main_tabs[2]: show_legal_area()

if __name__ == "__main__":
    main()
