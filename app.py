import streamlit as st
from database_manager import hole_df, hash_passwort, registriere_nutzer
from user_area import show_user_area, show_proposal_area, show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

APP_NAME = "KletterKompass"

# 1. Konfiguration
st.set_page_config(page_title=APP_NAME, layout="wide")

# 2. Styling: Sidebar verstecken & Tabs aufpeppen
st.markdown("""
    <style>
    /* Sidebar komplett weg */
    [data-testid="stSidebar"] { display: none; }
    
    /* Tabs zentrieren und Schrift lesbar machen */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 10px 15px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2e7d32 !important;
        color: white !important;
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
            st.subheader("Konto erstellen")
            r_u = st.text_input("Nutzername*", key="reg_u")
            r_e = st.text_input("E-Mail*", key="reg_e")
            r_p = st.text_input("Passwort*", type="password", key="reg_p")
            if st.button("Registrieren", use_container_width=True):
                if r_u and r_p and r_e:
                    if registriere_nutzer(r_u, r_p, r_e, "", "", 25, True):
                        st.success("Erfolg! Bitte einloggen.")
                else: st.warning("Pflichtfelder fehlen.")

    # --- DIE TAB-NAVIGATION (WENN EINGELOGGT) ---
    else:
        # Hier definieren wir die Reiter
        tab_titles = ["📍 Suche", "💡 Vorschlag", "👤 Profil", "💬 Feedback", "📄 Recht"]
        
        # Admin bekommt einen extra Tab
        if st.session_state.user_role == 'admin':
            tab_titles.append("🛠️ Admin")
        
        # Wir starten direkt im Profil (Index 2 in der Liste)
        # Wenn wir aber schon etwas ausgewählt haben, merkt Streamlit sich das
        tabs = st.tabs(tab_titles)

        with tabs[0]: # Suche
            show_user_area()
            
        with tabs[1]: # Vorschlag
            show_proposal_area()
            
        with tabs[2]: # Profil
            show_profile_area()
            # Logout-Button platzieren wir im Profil, um Platz zu sparen
            st.divider()
            if st.button("🚪 Logout / Abmelden", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()
            
        with tabs[3]: # Feedback
            show_feedback_area()
            
        with tabs[4]: # Recht
            show_legal_area()

        # Admin-Tab nur füllen, wenn er existiert
        if st.session_state.user_role == 'admin':
            with tabs[5]:
                show_admin_area()

if __name__ == "__main__":
    main()
