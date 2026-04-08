import streamlit as st
import os
from database_manager import hole_df, hash_passwort, registriere_nutzer
from user_area import show_user_area, show_proposal_area, show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

APP_NAME = "KletterKompass"

# 1. Konfiguration (Sidebar wird durch CSS versteckt)
st.set_page_config(page_title=APP_NAME, layout="wide")

# 2. CSS: Sidebar verstecken & Buttons schick machen
st.markdown("""
    <style>
    /* Sidebar komplett ausblenden */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    
    /* Haupt-Design */
    h1, h2, h3 { color: #2e7d32 !important; text-align: center; }
    
    /* Die Navigations-Buttons oben */
    .stButton>button { 
        background-color: #2e7d32; 
        color: white; 
        border-radius: 8px; 
        padding: 10px;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_role' not in st.session_state: st.session_state.user_role = 'guest'
    if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

    # --- LOGIN / REGISTRIERUNG ---
    if not st.session_state.logged_in:
        st.title(f"🧗 {APP_NAME}")
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
                    else: st.error("Daten falsch.")

        with t_reg:
            st.subheader("Neues Konto erstellen")
            r_u = st.text_input("Nutzername*", key="reg_u")
            r_e = st.text_input("E-Mail*", key="reg_e")
            r_p = st.text_input("Passwort*", type="password", key="reg_p")
            r_v = st.text_input("Vorname", key="reg_v")
            r_n = st.text_input("Nachname", key="reg_n")
            r_a = st.number_input("Alter", 0, 100, 25)
            r_agb = st.checkbox("AGB akzeptieren*")
            if st.button("Registrieren"):
                if r_u and r_p and r_e and r_agb:
                    if registriere_nutzer(r_u, r_p, r_e, r_v, r_n, r_a, r_agb):
                        st.success("Erfolg! Bitte einloggen.")
                else: st.warning("Pflichtfelder fehlen.")

    # --- HAUPT-NAVIGATION (OBEN STATT SIDEBAR) ---
    else:
        st.write(f"Moin **{st.session_state.user}**! 👋")
        
        # Erste Reihe Buttons
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("📍 Suche"): st.session_state.wahl = "📍 Suche"; st.rerun()
        with c2:
            if st.button("💡 Vorschlag"): st.session_state.wahl = "💡 Vorschlag"; st.rerun()
        with c3:
            if st.button("👤 Profil"): st.session_state.wahl = "👤 Profil"; st.rerun()

        # Zweite Reihe Buttons
        c4, c5, c6 = st.columns(3)
        with c4:
            if st.button("💬 Feedback"): st.session_state.wahl = "💬 Feedback"; st.rerun()
        with c5:
            if st.button("📄 Recht"): st.session_state.wahl = "📄 Recht"; st.rerun()
        with c6:
            if st.button("🚪 Logout"): 
                st.session_state.logged_in = False
                st.rerun()
        
        # Admin-Button (nur wenn Admin)
        if st.session_state.user_role == 'admin':
            if st.button("🛠️ Admin-Bereich"): st.session_state.wahl = "🛠️ Admin"; st.rerun()

        st.divider()

        # Routing (Anzeige der Inhalte)
        if st.session_state.wahl == "📍 Suche": show_user_area()
        elif st.session_state.wahl == "💡 Vorschlag": show_proposal_area()
        elif st.session_state.wahl == "👤 Profil": show_profile_area()
        elif st.session_state.wahl == "💬 Feedback": show_feedback_area()
        elif st.session_state.wahl == "🛠️ Admin": show_admin_area()
        elif st.session_state.wahl == "📄 Recht": show_legal_area()

if __name__ == "__main__":
    main()
