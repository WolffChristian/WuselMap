import streamlit as st
from database_manager import hole_df, hash_passwort
from user_area import show_profile_area, show_feedback_area, show_legal_area
from admin_area import show_admin_area
from styles import apply_custom_css  # Das Design-Paket importieren

# Seite konfigurieren
st.set_page_config(page_title="WuselMap", layout="wide")

def main():
    # Design anwenden
    apply_custom_css()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # Automatischer Login über URL-Parameter
    if not st.session_state.logged_in:
        user_param = st.query_params.get("user")
        if user_param:
            df_n = hole_df("nutzer")
            if not df_n.empty:
                match = df_n[df_n['benutzername'] == user_param]
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user = user_param
                    st.session_state.user_role = match.iloc[0]['rolle']

    # Login-Bereich
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            try:
                st.image("logo.png", use_container_width=True)
            except:
                st.title("🦊 WuselMap")
            
            st.markdown("### Login")
            u_in = st.text_input("Nutzername").strip().lower()
            p_in = st.text_input("Passwort", type="password")
            
            if st.button("Anmelden", use_container_width=True, type="primary"):
                df_n = hole_df("nutzer")
                match = df_n[(df_n['benutzername'].str.lower() == u_in) & (df_n['passwort'] == hash_passwort(p_in))]
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user = match.iloc[0]['benutzername']
                    st.session_state.user_role = match.iloc[0]['rolle']
                    st.query_params["user"] = st.session_state.user
                    st.rerun()
                else: 
                    st.error("Login falsch.")
    else:
        # Hauptmenü nach Login
        menu = ["👤 Mein Bereich", "💬 Feedback"]
        if st.session_state.user_role == 'admin':
            menu.append("🛠️ Admin")
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
