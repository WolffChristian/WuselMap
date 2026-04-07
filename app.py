import streamlit as st
# WICHTIG: Importiert deine Seitenfunktionen aus der user_area.py
import user_area 

# 1. GRUNDKONFIGURATION
st.set_page_config(
    page_title="Kletter-App Varel",
    page_icon="🧗‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS-HACK: Sidebar verstecken & Radio-Buttons als Handy-Menü stylen
st.markdown("""
    <style>
        /* Sidebar komplett ausblenden */
        [data-testid="stSidebar"] {
            display: none;
        }
        /* Radio-Buttons horizontal zentrieren */
        .stRadio > div {
            flex-direction: row;
            justify-content: center;
            gap: 20px;
        }
        /* Radio-Button Beschriftung ausblenden */
        [data-testid="stWidgetLabel"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

def main():
    # --- SESSION STATE INITIALISIERUNG ---
    # Falls noch kein User eingeloggt ist, setzen wir ihn auf None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    if 'wahl' not in st.session_state:
        st.session_state.wahl = "📍 Spots"

    # --- PRÜFUNG: IST DER USER EINGELOGGT? ---
    if st.session_state.user_id is None:
        show_login_screen()
    else:
        show_main_app()

def show_login_screen():
    st.title("Willkommen beim Kletter-Kompass")
    st.subheader("Bitte einloggen")
    
    # Einfacher Login für den Test (hier deine echte Logik einbauen)
    u_id = st.number_input("Deine User-ID", value=30001)
    if st.button("Login"):
        st.session_state.user_id = u_id
        st.rerun()

def show_main_app():
    # --- HORIZONTALE NAVIGATION (OBEN) ---
    # Das ersetzt die Sidebar auf dem Handy
    menu = ["📍 Spots", "💡 Vorschlag", "⚙️ Profil"]
    
    wahl = st.radio(
        "Menü",
        menu,
        index=menu.index(st.session_state.wahl) if st.session_state.wahl in menu else 0,
        horizontal=True
    )
    
    st.session_state.wahl = wahl
    st.divider()

    # --- SEITEN-LOGIK ---
    if wahl == "📍 Spots":
        # Ruft die Funktion in deiner user_area.py auf
        user_area.show_user_area()
        
    elif wahl == "💡 Vorschlag":
        # Ruft die Funktion in deiner user_area.py auf
        user_area.show_proposal_area()
        
    elif wahl == "⚙️ Profil":
        st.subheader("Mein Profil")
        st.write(f"Angemeldet als User: **{st.session_state.user_id}**")
        
        if st.button("Abmelden"):
            st.session_state.user_id = None
            st.rerun()

if __name__ == "__main__":
    main()
