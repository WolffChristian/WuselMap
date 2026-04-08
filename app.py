import streamlit as st
import os
from database_manager import hole_df, hash_passwort, registriere_nutzer
from user_area import show_user_area, show_proposal_area, show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

APP_NAME = "KletterKompass"

# 1. Konfiguration
st.set_page_config(page_title=APP_NAME, layout="wide")

# 2. DAS DESIGN-UPGRADE: Menü oben fixieren & Buttons stylen
st.markdown("""
    <style>
    /* Sidebar verstecken */
    [data-testid="stSidebar"] { display: none; }
    
    /* Haupt-Container Abstände anpassen */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    /* Das Menü oben fixieren (Sticky) */
    .stHeader {
        background-color: rgba(14, 17, 23, 0.95);
    }
    
    /* Buttons kompakter machen */
    .stButton > button {
        width: 100% !important;
        background-color: #2e7d32;
        color: white;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 13px;
        border: none;
        height: auto;
        min-height: 35px;
    }
    
    .stButton > button:hover {
        background-color: #1b5e20;
        border: none;
    }

    /* Trennlinie unter dem Menü */
    .nav-divider {
        margin: 10px 0;
        border-bottom: 1px solid #2e7d32;
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
            # (Dein Registrierungs-Code bleibt hier gleich...)
            st.subheader("Konto erstellen")
            r_u = st.text_input("Nutzername*", key="reg_u")
            r_e = st.text_input("E-Mail*", key="reg_e")
            r_p = st.text_input("Passwort*", type="password", key="reg_p")
            if st.button("Registrieren"):
                if r_u and r_p and r_e:
                    if registriere_nutzer(r_u, r_p, r_e, "", "", 25, True):
                        st.success("Erfolg!")
                else: st.warning("Pflichtfelder fehlen.")

    # --- DIE NEUE APP-BAR (OBEN FIXIERT) ---
    else:
        # Ein kompakter Container für die Navigation
        nav_container = st.container()
        with nav_container:
            # Reihe 1: Hauptfunktionen
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("📍 Suche"): st.session_state.wahl = "📍 Suche"; st.rerun()
            with col2:
                if st.button("💡 Vorschlag"): st.session_state.wahl = "💡 Vorschlag"; st.rerun()
            with col3:
                if st.button("👤 Profil"): st.session_state.wahl = "👤 Profil"; st.rerun()
            with col4:
                if st.button("💬 Feedback"): st.session_state.wahl = "💬 Feedback"; st.rerun()

            # Reihe 2: Admin & Logout (Schmaler)
            cols = [1, 1, 1, 1]
            if st.session_state.user_role == 'admin':
                c5, c6, c7, c8 = st.columns(4)
                with c5:
                    if st.button("🛠️ Admin"): st.session_state.wahl = "🛠️ Admin"; st.rerun()
                with c6:
                    if st.button("📄 Recht"): st.session_state.wahl = "📄 Recht"; st.rerun()
                with c7:
                    if st.button("🚪 Logout"): 
                        st.session_state.logged_in = False
                        st.rerun()
            else:
                c5, c6, c7 = st.columns([1, 1, 2])
                with c5:
                    if st.button("📄 Recht"): st.session_state.wahl = "📄 Recht"; st.rerun()
                with c6:
                    if st.button("🚪 Logout"): 
                        st.session_state.logged_in = False
                        st.rerun()
        
        st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

        # --- CONTENT BEREICH ---
        if st.session_state.wahl == "📍 Suche": show_user_area()
        elif st.session_state.wahl == "💡 Vorschlag": show_proposal_area()
        elif st.session_state.wahl == "👤 Profil": show_profile_area()
        elif st.session_state.wahl == "💬 Feedback": show_feedback_area()
        elif st.session_state.wahl == "🛠️ Admin": show_admin_area()
        elif st.session_state.wahl == "📄 Recht": show_legal_area()

if __name__ == "__main__":
    main()
