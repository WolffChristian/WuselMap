import streamlit as st
from database_manager import hole_df, hash_passwort, registriere_nutzer
from user_area import show_user_area, show_proposal_area, show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

APP_NAME = "KletterKompass"

# 1. Konfiguration
st.set_page_config(page_title=APP_NAME, layout="wide")

# 2. DAS FARB-UPDATE: Kontrastreiche Tabs
st.markdown("""
    <style>
    /* Sidebar verstecken */
    [data-testid="stSidebar"] { display: none; }
    
    /* Hintergrund der Tab-Leiste */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
        background-color: transparent;
    }

    /* Standard-Zustand (Inaktiv) */
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #f0f2f6; /* Hellgrau */
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        border: 1px solid #d1d5db;
    }
    
    /* Textfarbe der inaktiven Tabs (Schwarz/Dunkelgrau) */
    .stTabs [data-baseweb="tab"] p {
        color: #31333f !important;
        font-weight: 600;
        font-size: 14px;
    }

    /* Aktiver Tab (Grün) */
    .stTabs [aria-selected="true"] {
        background-color: #2e7d32 !important;
        border-color: #2e7d32 !important;
    }
    
    /* Textfarbe des aktiven Tabs (Weiß) */
    .stTabs [aria-selected="true"] p {
        color: white !important;
    }

    /* Hover-Effekt (Wenn man mit dem Finger/Maus drübergeht) */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e2e8f0;
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
                    else: st.error("Daten falsch.")
        with t_reg:
            # (Registrierungs-Formular hier einfügen...)
            st.subheader("Konto erstellen")
            r_u = st.text_input("Nutzername*", key="reg_u")
            r_e = st.text_input("E-Mail*", key="reg_e")
            r_p = st.text_input("Passwort*", type="password", key="reg_p")
            if st.button("Registrieren", use_container_width=True):
                if r_u and r_p and r_e:
                    if registriere_nutzer(r_u, r_p, r_e, "", "", 25, True):
                        st.success("Erfolg!")

    # --- TAB-NAVIGATION (EINGELOGGT) ---
    else:
        # Wir definieren die Reiter-Namen
        tab_labels = ["📍 Suche", "💡 Vorschlag", "👤 Profil", "💬 Feedback", "📄 Recht"]
        if st.session_state.user_role == 'admin':
            tab_labels.append("🛠️ Admin")
        
        # Erstellt die Tabs
        tabs = st.tabs(tab_labels)

        with tabs[0]: show_user_area()
        with tabs[1]: show_proposal_area()
        with tabs[2]:
            show_profile_area()
            st.divider()
            if st.button("🚪 Abmelden", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()
        with tabs[3]: show_feedback_area()
        with tabs[4]: show_legal_area()
        
        if st.session_state.user_role == 'admin':
            with tabs[5]: show_admin_area()

if __name__ == "__main__":
    main()
