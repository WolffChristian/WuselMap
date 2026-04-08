import streamlit as st
from database_manager import hole_df, hash_passwort
from user_area import show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

st.set_page_config(page_title="KletterKompass", layout="wide")

# CSS für die Balken (Grün wenn aktiv)
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
        # --- LOGIN BEREICH ---
        st.title("🧗 KletterKompass Login")
        u_in = st.text_input("Nutzername")
        p_in = st.text_input("Passwort", type="password")
        if st.button("Anmelden", use_container_width=True):
            # Login-Logik hier (gekürzt)
            st.session_state.logged_in = True
            st.session_state.user = u_in
            st.session_state.user_role = "admin" # Nur als Beispiel
            st.rerun()
    else:
        # --- HAUPTMENÜ (Nur 3-4 Punkte) ---
        # "Suche" und "Vorschlag" sind hier NICHT mehr drin!
        menu = ["👤 Profil & Navigation", "💬 Feedback"]
        
        if st.session_state.get('user_role') == 'admin':
            menu.append("🛠️ Admin")
        
        menu.append("📄 Recht")
        
        haupt_tabs = st.tabs(menu)

        with haupt_tabs[0]:
            # HIER passiert alles: Profil, Suche und Vorschlag
            show_profile_area()
            
            st.divider()
            if st.button("🚪 Abmelden", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

        with haupt_tabs[1]:
            show_feedback_area()

        # ... (Rest der Tabs für Admin und Recht)
