import streamlit as st
from database_manager import hole_df, hash_passwort, registriere_nutzer
from user_area import show_user_area, show_proposal_area, show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

APP_NAME = "KletterKompass"

# 1. Konfiguration & Design
st.set_page_config(page_title=APP_NAME, layout="wide")

# CSS: Sidebar komplett weg & Tabs für das Handy optimieren
st.markdown("""
    <style>
    /* Sidebar komplett ausblenden */
    [data-testid="stSidebar"] { display: none; }
    
    /* Haupt-Überschrift Design */
    h1 { color: #2e7d32 !important; font-size: 24px !important; text-align: center; }

    /* Tabs (Deine Auswahlbalken) schick machen */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center; /* Zentriert die Balken */
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6; /* Inaktive Balken: Hellgrau */
        border-radius: 8px 8px 0 0;
        padding: 10px 15px;
        border: 1px solid #d1d5db;
    }

    /* Textfarbe in den Balken (Dunkel & Lesbar) */
    .stTabs [data-baseweb="tab"] p {
        color: #31333f !important;
        font-weight: 600 !important;
        font-size: 14px;
    }

    /* Der aktive Balken (Dein Kletter-Grün) */
    .stTabs [aria-selected="true"] {
        background-color: #2e7d32 !important;
    }
    .stTabs [aria-selected="true"] p {
        color: white !important; /* Weißer Text auf grünem Grund */
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_role' not in st.session_state: st.session_state.user_role = 'guest'

    # --- 🔐 LOGIN / REGISTRIERUNG ---
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
            st.info("Hier kannst du dich neu anmelden.")
            # ... Dein Registrierungs-Code bleibt hier ...

    # --- 👤 DAS ZENTRALE DASHBOARD (NACH LOGIN) ---
    else:
        st.title(f"🧗 {APP_NAME}")
        
        # Wir bauen die Balken-Auswahl (Tabs) direkt in die Seite
        # Wir packen alles Wichtige in die Liste
        reiter = ["👤 Mein Profil", "📍 Suche", "💡 Vorschlag", "💬 Feedback"]
        
        # Nur für dich als Admin kommt der Admin-Balken dazu
        if st.session_state.user_role == 'admin':
            reiter.append("🛠️ Admin")
        
        reiter.append("📄 Recht")

        # Hier entstehen die "Balken" wie im Adminbereich
        tabs = st.tabs(reiter)

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

        # Check für Admin-Tab (falls vorhanden)
        if st.session_state.user_role == 'admin':
            with tabs[4]: # 🛠️ Admin
                show_admin_area()
            with tabs[5]: # 📄 Recht
                show_legal_area()
        else:
            with tabs[4]: # 📄 Recht
                show_legal_area()

if __name__ == "__main__":
    main()
