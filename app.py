import streamlit as st
from database_manager import hole_df, hash_passwort, registriere_nutzer
from user_area import show_user_area, show_proposal_area, show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

APP_NAME = "KletterKompass"

# 1. Konfiguration
st.set_page_config(page_title=APP_NAME, layout="wide")

# 2. CSS: Alles für den Admin-Look (Balken-Design)
st.markdown("""
    <style>
    /* Sidebar komplett weg */
    [data-testid="stSidebar"] { display: none; }
    
    /* Die Tabs (deine Balken) stylen */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6; /* Inaktiv: hellgrau */
        border-radius: 8px 8px 0 0;
        padding: 8px 12px;
        border: 1px solid #d1d5db;
    }

    /* Text in den Balken */
    .stTabs [data-baseweb="tab"] p {
        font-size: 14px;
        font-weight: 600;
        color: #31333f !important;
    }

    /* Aktiver Balken (Kletter-Grün) */
    .stTabs [aria-selected="true"] {
        background-color: #2e7d32 !important;
        border-color: #2e7d32 !important;
    }
    .stTabs [aria-selected="true"] p {
        color: white !important;
    }

    /* Buttons innerhalb der Bereiche */
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_role' not in st.session_state: st.session_state.user_role = 'guest'

    # --- LOGIN / REGISTRIERUNG ---
    if not st.session_state.logged_in:
        st.title(f"🧗 {APP_NAME} Login")
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
            st.subheader("Konto erstellen")
            # ... (Dein Registrierungs-Code hier)

    # --- DAS DASHBOARD (LANDING PAGE) ---
    else:
        st.title(f"🧗 {APP_NAME}")
        
        # Die Auswahlbalken wie in deinem Admin-Bild
        # "Mein Profil" ist an Stelle 1 -> also landet man automatisch dort!
        reiter_namen = ["👤 Mein Profil", "📍 Suche", "💡 Vorschlag", "💬 Feedback"]
        
        # Admin-Zusatz
        if st.session_state.user_role == 'admin':
            reiter_namen.append("🛠️ Admin-Bereich")
            
        reiter_namen.append("📄 Recht")

        # Hier werden die Tabs (Balken) erstellt
        tabs = st.tabs(reiter_namen)

        with tabs[0]: # 👤 Mein Profil
            show_profile_area()
            st.divider()
            if st.button("🚪 Logout / Abmelden", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

        with tabs[1]: # 📍 Suche
            show_user_area()

        with tabs[2]: # 💡 Vorschlag
            show_proposal_area()

        with tabs[3]: # 💬 Feedback
            show_feedback_area()

        if st.session_state.user_role == 'admin':
            with tabs[4]: # 🛠️ Admin-Bereich
                show_admin_area()
            with tabs[5]: # 📄 Recht
                show_legal_area()
        else:
            with tabs[4]: # 📄 Recht
                show_legal_area()

if __name__ == "__main__":
    main()
