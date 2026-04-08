import streamlit as st
from database_manager import hole_df, hash_passwort, registriere_nutzer
from user_area import show_user_area, show_proposal_area, show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

APP_NAME = "KletterKompass"

# 1. Konfiguration
st.set_page_config(page_title=APP_NAME, layout="wide")

# 2. CSS-FIX: Damit am Handy nichts abgeschnitten wird
st.markdown("""
    <style>
    /* Sidebar komplett ausblenden */
    [data-testid="stSidebar"] { display: none; }
    
    /* Tabs für das Handy optimieren */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        justify-content: flex-start; /* Erlaubt horizontales Scrollen am Handy */
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 5px 10px;
        border: 1px solid #d1d5db;
    }

    /* Text in den Tabs - Kleiner für Handy */
    .stTabs [data-baseweb="tab"] p {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #31333f !important;
    }

    /* Aktiver Tab */
    .stTabs [aria-selected="true"] {
        background-color: #2e7d32 !important;
    }
    .stTabs [aria-selected="true"] p {
        color: white !important;
    }
    
    /* Logout Button Styling */
    .logout-btn {
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_role' not in st.session_state: st.session_state.user_role = 'guest'

    # --- LOGIN / REGISTRIERUNG ---
    if not st.session_state.logged_in:
        st.title(f"🧗 {APP_NAME}")
        t_log, t_reg = st.tabs(["🔐 Login", "📝 Registrieren"])
        
        with t_log:
            u_in = st.text_input("Nutzername", key="l_u").strip()
            p_in = st.text_input("Passwort", type="password", key="l_p").strip()
            if st.button("Anmelden", use_container_width=True):
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
            # Hier dein Registrierungs-Code (gekürzt für Übersicht)
            st.info("Bitte fülle alle Felder aus.")
            # ... (Rest wie gehabt)

    # --- HAUPTBEREICH (TAB-SYSTEM) ---
    else:
        # Wir setzen "Profil" an die erste Stelle, damit man dort landet!
        tab_list = ["👤 Profil", "📍 Suche", "💡 Vorschlag", "💬 Feedback", "📄 Recht"]
        
        if st.session_state.user_role == 'admin':
            tab_list.append("🛠️ Admin")
            
        # Erstellt die Tabs (Slider)
        tabs = st.tabs(tab_list)

        # TAB 0: PROFIL (LANDING PAGE)
        with tabs[0]:
            st.subheader(f"Moin {st.session_state.user}!")
            show_profile_area()
            st.divider()
            if st.button("🚪 Abmelden", use_container_width=True, key="logout_top"):
                st.session_state.logged_in = False
                st.rerun()

        # TAB 1: SUCHE
        with tabs[1]:
            show_user_area()

        # TAB 2: VORSCHLAG
        with tabs[2]:
            show_proposal_area()

        # TAB 3: FEEDBACK
        with tabs[3]:
            show_feedback_area()

        # TAB 4: RECHT
        with tabs[4]:
            show_legal_area()

        # TAB 5: ADMIN (NUR WENN ADMIN)
        if st.session_state.user_role == 'admin':
            with tabs[5]:
                show_admin_area()

if __name__ == "__main__":
    main()
