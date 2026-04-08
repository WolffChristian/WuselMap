import streamlit as st
from database_manager import hole_df, hash_passwort
from user_area import show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

# 1. Konfiguration
st.set_page_config(page_title="KletterKompass", layout="wide")

# 2. DAS DESIGN-PAKET (Slim-Balken & Lesbarkeit)
st.markdown("""
    <style>
    /* Sidebar komplett ausblenden */
    [data-testid="stSidebar"] { display: none; }
    
    /* Haupt-Überschrift kompakt */
    h1 { color: #2e7d32 !important; font-size: 22px !important; text-align: center; margin-bottom: 10px; }

    /* --- TABS / BALKEN DESIGN (SLIM) --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        justify-content: center;
    }

    /* Inaktive Balken: Schmaler und flacher für Handy */
    .stTabs [data-baseweb="tab"] {
        height: 35px; /* Flaches Design */
        background-color: #eeeeee; 
        border-radius: 6px 6px 0 0;
        padding: 4px 12px; /* Weniger Fleisch um den Text */
        border: 1px solid #cccccc;
    }
    
    /* Text in den Balken: Klar und deutlich */
    .stTabs [data-baseweb="tab"] p {
        color: #333333 !important;
        font-weight: 600 !important;
        font-size: 13px !important; /* Optimale Größe für Mobilgeräte */
        margin: 0;
    }

    /* Aktiver Balken: Kletter-Grün */
    .stTabs [aria-selected="true"] {
        background-color: #2e7d32 !important;
        border-color: #2e7d32 !important;
    }
    
    .stTabs [aria-selected="true"] p {
        color: #ffffff !important; /* Weißer Text auf Grün */
    }

    /* Hover-Effekt */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e0e0e0;
    }

    /* Standard-Buttons (Logout etc.) */
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    # Initialisierung der Zustände
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_role' not in st.session_state: st.session_state.user_role = 'guest'

    if not st.session_state.logged_in:
        # --- LOGIN BEREICH ---
        st.title(f"🧗 KletterKompass Login")
        
        # .strip().lower() bügelt Handy-Tippfehler (Leerzeichen/Großschreibung) glatt
        u_in = st.text_input("Nutzername", key="login_u").strip().lower()
        p_in = st.text_input("Passwort", type="password", key="login_p")
        
        if st.button("Anmelden", use_container_width=True):
            df_n = hole_df("nutzer")
            if not df_n.empty:
                # Sicherer Vergleich: Beide Seiten kleingeschrieben vergleichen
                match = df_n[
                    (df_n['benutzername'].str.lower() == u_in) & 
                    (df_n['passwort'] == hash_passwort(p_in))
                ]
                
                if not match.empty:
                    st.session_state.logged_in = True
                    # Wir speichern den Namen exakt wie in der DB (für die Optik)
                    st.session_state.user = match.iloc[0]['benutzername']
                    st.session_state.user_role = match.iloc[0]['rolle']
                    st.rerun()
                else:
                    st.error("Login-Daten falsch. Prüfe dein Passwort!")
            else:
                st.error("Keine Nutzerdaten gefunden.")
    else:
        # --- HAUPTMENÜ (Das Dashboard) ---
        st.title(f"🧗 KletterKompass")
        
        # Menüpunkte definieren
        menu = ["👤 Mein Bereich", "💬 Feedback"]
        if st.session_state.user_role == 'admin':
            menu.append("🛠️ Admin")
        menu.append("📄 Recht")
        
        # Erstellt die schmalen Balken oben
        main_tabs = st.tabs(menu)

        with main_tabs[0]:
            # LANDING PAGE: Hier wird show_profile_area() aufgerufen,
            # welche wiederum eigene Unter-Balken für Suche/Vorschlag hat.
            show_profile_area()

        with main_tabs[1]:
            show_feedback_area()

        if st.session_state.user_role == 'admin':
            with main_tabs[2]:
                show_admin_area()
            with main_tabs[3]:
                show_legal_area()
        else:
            with main_tabs[2]:
                show_legal_area()

if __name__ == "__main__":
    main()
