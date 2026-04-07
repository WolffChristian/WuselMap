import streamlit as st
import user_area

# 1. Konfiguration (Muss ganz oben stehen)
st.set_page_config(page_title="Kletter-Kompass", page_icon="🧗‍♂️", initial_sidebar_state="collapsed")

# Sidebar verstecken & Menü-Design
st.markdown("""<style>[data-testid="stSidebar"] {display: none;} .stRadio > div {flex-direction: row; justify-content: center; gap: 30px;}</style>""", unsafe_allow_html=True)

def main():
    # Session State sicher initialisieren
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'wahl' not in st.session_state:
        st.session_state.wahl = "📍 Spots"

    # LOGIN-LOGIK
    if st.session_state.user_id is None:
        st.title("🧗‍♂️ Kletter-Kompass Varel")
        st.subheader("Login")
        
        # Container für ein sauberes Layout
        with st.container():
            u_name = st.text_input("Nutzername (z.B. Sabrina)")
            u_pw = st.text_input("Passwort", type="password")
            
            if st.button("Anmelden", use_container_width=True):
                if u_name and u_pw:
                    # Hier loggen wir den User ein
                    st.session_state.user_id = u_name
                    st.rerun()
                else:
                    st.warning("Bitte Namen und Passwort eingeben.")
    
    # HAUPT-APP (Nur wenn eingeloggt)
    else:
        # Navigation oben
        menu = ["📍 Spots", "💡 Vorschlag"]
        wahl = st.radio("Navigation", menu, horizontal=True, label_visibility="collapsed")
        st.divider()

        if wahl == "📍 Spots":
            user_area.show_user_area()
        elif wahl == "💡 Vorschlag":
            user_area.show_proposal_area()
        
        # Abmelden Button ganz unten
        st.sidebar.markdown("---") # Falls die Sidebar doch mal aufgeht
        if st.button("Abmelden", use_container_width=True):
            st.session_state.user_id = None
            st.rerun()

if __name__ == "__main__":
    main()
