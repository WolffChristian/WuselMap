import streamlit as st
from database_manager import hole_df, hash_passwort
from user_area import show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

st.set_page_config(page_title="KletterKompass", layout="wide")

# CSS: Hier fixen wir die Farben für die Tabs (Balken)
st.markdown("""
    <style>
    /* Sidebar komplett weg */
    [data-testid="stSidebar"] { display: none; }
    
    /* Haupt-Überschrift */
    h1 { color: #2e7d32 !important; text-align: center; }

    /* --- TABS / BALKEN DESIGN --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
    }

    /* 1. Inaktive Balken (Hellgrau mit dunkler Schrift) */
    .stTabs [data-baseweb="tab"] {
        background-color: #eeeeee; 
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        border: 1px solid #cccccc;
    }
    
    /* Textfarbe für inaktive Balken (Muss dunkel sein!) */
    .stTabs [data-baseweb="tab"] p {
        color: #333333 !important;
        font-weight: bold !important;
    }

    /* 2. Aktiver Balken (Dein Kletter-Grün) */
    .stTabs [aria-selected="true"] {
        background-color: #2e7d32 !important;
        border-color: #2e7d32 !important;
    }
    
    /* Textfarbe für aktiven Balken (Weiß) */
    .stTabs [aria-selected="true"] p {
        color: #ffffff !important;
    }

    /* 3. Hover-Effekt (Wenn man mit dem Finger draufkommt) */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e0e0e0;
    }

    /* Standard-Buttons im Rest der App auch grün machen */
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_role' not in st.session_state: st.session_state.user_role = 'guest'

    if not st.session_state.logged_in:
        # --- LOGIN ---
        st.title(f"🧗 KletterKompass Login")
       # --- LOGIN BEREICH ---
        # --- LOGIN BEREICH ---
        u_in = st.text_input("Nutzername", key="login_u").strip().lower()
        p_in = st.text_input("Passwort", type="password", key="login_p")
        
        if st.button("Anmelden", use_container_width=True):
            df_n = hole_df("nutzer")
            if not df_n.empty:
                # Wir machen beim Vergleich BEIDE SEITEN klein (.str.lower())
                # So findet er 'christian' egal ob 'Christian' oder 'CHRISTIAN' in der DB steht
                match = df_n[
                    (df_n['benutzername'].str.lower() == u_in) & 
                    (df_n['passwort'] == hash_passwort(p_in))
                ]
                
                if not match.empty:
                    st.session_state.logged_in = True
                    # Wir nehmen den Namen so, wie er in der DB steht
                    st.session_state.user = match.iloc[0]['benutzername']
                    st.session_state.user_role = match.iloc[0]['rolle']
                    st.rerun()
                else:
                    st.error("Login-Daten falsch. Prüfe dein Passwort!")
    else:
        # --- HAUPTMENÜ (Balken oben) ---
        menu = ["👤 Mein Bereich", "💬 Feedback"]
        if st.session_state.user_role == 'admin':
            menu.append("🛠️ Admin")
        menu.append("📄 Recht")
        
        main_tabs = st.tabs(menu)

        with main_tabs[0]:
            # Hier landen die User -> show_profile_area() hat eigene Unter-Tabs
            show_profile_area()

        with main_tabs[1]:
            show_feedback_area()

        if st.session_state.user_role == 'admin':
            with main_tabs[2]: show_admin_area()
            with main_tabs[3]: show_legal_area()
        else:
            with main_tabs[2]: show_legal_area()

if __name__ == "__main__":
    main()
