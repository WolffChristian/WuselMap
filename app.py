import streamlit as st
import user_area

# --- STABILE KONFIGURATION ---
st.set_page_config(page_title="Kletter-Kompass", page_icon="🧗‍♂️", initial_sidebar_state="collapsed")

# CSS: Sidebar komplett unsichtbar machen
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stRadio > div {flex-direction: row; justify-content: center; gap: 20px;}
    </style>
""", unsafe_allow_html=True)

def main():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    # LOGIN (Ganz einfach, wie es bei dir funktioniert hat)
    if st.session_state.user_id is None:
        st.title("🧗‍♂️ Kletter-Kompass")
        # Hier dein alter Login-Weg:
        user_input = st.text_input("Dein Name")
        if st.button("Starten"):
            if user_input:
                st.session_state.user_id = user_input
                st.rerun()
    
    # HAUPT-APP
    else:
        # Die Buttons als Navigation oben
        wahl = st.radio("Menü", ["📍 Spots", "💡 Vorschlag"], horizontal=True, label_visibility="collapsed")
        st.divider()

        if wahl == "📍 Spots":
            user_area.show_user_area()
        elif wahl == "💡 Vorschlag":
            user_area.show_proposal_area()
        
        if st.button("Abmelden"):
            st.session_state.user_id = None
            st.rerun()

if __name__ == "__main__":
    main()
