import streamlit as st
from database_manager import hole_df, hash_passwort
from user_area import show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area

st.set_page_config(page_title="KletterKompass", layout="wide")

# CSS für Slim-Balken
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    h1 { color: #2e7d32 !important; font-size: 20px !important; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { gap: 5px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { height: 35px; background-color: #eeeeee; border-radius: 6px; padding: 4px 12px; border: 1px solid #cccccc; }
    .stTabs [data-baseweb="tab"] p { color: #333333 !important; font-weight: 600; font-size: 13px; }
    .stTabs [aria-selected="true"] { background-color: #2e7d32 !important; }
    .stTabs [aria-selected="true"] p { color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

def main():
    # REFRESH-SCHUTZ: Prüfen ob User in URL gespeichert ist
    if 'logged_in' not in st.session_state:
        saved_user = st.query_params.get("user")
        if saved_user:
            df_n = hole_df("nutzer")
            match = df_n[df_n['benutzername'] == saved_user]
            if not match.empty:
                st.session_state.logged_in = True
                st.session_state.user = saved_user
                st.session_state.user_role = match.iloc[0]['rolle']
            else: st.session_state.logged_in = False
        else: st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🧗 KletterKompass Login")
        u_in = st.text_input("Nutzername").strip().lower()
        p_in = st.text_input("Passwort", type="password")
        if st.button("Anmelden", use_container_width=True):
            df_n = hole_df("nutzer")
            match = df_n[(df_n['benutzername'].str.lower() == u_in) & (df_n['passwort'] == hash_passwort(p_in))]
            if not match.empty:
                st.session_state.logged_in = True
                st.session_state.user = match.iloc[0]['benutzername']
                st.session_state.user_role = match.iloc[0]['rolle']
                # LOGIN IN URL SPEICHERN (Refresh-Schutz)
                st.query_params["user"] = st.session_state.user
                st.rerun()
            else: st.error("Daten falsch.")
    else:
        menu = ["👤 Mein Bereich", "💬 Feedback"]
        if st.session_state.user_role == 'admin': menu.append("🛠️ Admin")
        menu.append("📄 Recht")
        
        main_tabs = st.tabs(menu)
        with main_tabs[0]: show_profile_area()
        with main_tabs[1]: show_feedback_area()
        if st.session_state.user_role == 'admin':
            with main_tabs[2]: show_admin_area()
            with main_tabs[3]: show_legal_area()
        else:
            with main_tabs[2]: show_legal_area()

if __name__ == "__main__":
    main()
