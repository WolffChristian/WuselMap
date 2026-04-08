import streamlit as st
from database_manager import hole_df, hash_passwort
from user_area import show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

APP_NAME = "KletterKompass"

st.set_page_config(page_title=APP_NAME, layout="wide")

# CSS bleibt für das Design der Balken
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 8px; padding: 10px; }
    .stTabs [aria-selected="true"] { background-color: #2e7d32 !important; }
    .stTabs [aria-selected="true"] p { color: white !important; }
    </style>
""", unsafe_allow_html=True)

def main():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # ... Dein Login-Code ...
        st.title("Bitte einloggen")
    else:
        # DAS HAUPTMENÜ: Nur noch die Haupt-Kategorien!
        # Suche und Vorschlag sind hier VERSCHWUNDEN.
        menu_punkte = ["👤 Profil & Suche", "💬 Feedback"]
        
        if st.session_state.user_role == 'admin':
            menu_punkte.append("🛠️ Admin")
        
        menu_punkte.append("📄 Recht")
        
        main_tabs = st.tabs(menu_punkte)

        with main_tabs[0]:
            # Das hier ist jetzt der Dreh- und Angelpunkt. 
            # In show_profile_area() sind jetzt die Unter-Tabs für Suche/Vorschlag.
            show_profile_area()
            
            st.divider()
            if st.button("🚪 Abmelden", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

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
