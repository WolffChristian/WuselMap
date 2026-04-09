import streamlit as st
from database_manager import hole_df, hash_passwort, registriere_nutzer
from styles import apply_custom_css, show_header
from user_area import show_profile_area, show_feedback_area # show_legal_area hier entfernt!
from admin_area import show_admin_area
from legal_area import show_legal_area # Das ist jetzt die einzige Quelle


def main():
    apply_custom_css()
    show_header()
    
    # Beta-Hinweis
    st.warning("⚠️ **WuselMap Beta:** Wir optimieren gerade die Funktionen. Fehler bitte an info@wuselmap.de melden! 🧗‍♂️")

    # --- PERSISTENZ-LOGIK ---
    if 'logged_in' not in st.session_state:
        if "user" in st.query_params:
            u_name = st.query_params["user"]
            df = hole_df("nutzer")
            if not df.empty and u_name in df['benutzername'].values:
                st.session_state.logged_in = True
                st.session_state.user = u_name
                st.session_state.role = df[df['benutzername'] == u_name]['rolle'].values[0]
            else:
                st.session_state.logged_in = False
        else:
            st.session_state.logged_in = False

    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = "login"

    # Navigation
    if not st.session_state.logged_in:
        if st.session_state.auth_mode == "login":
            show_login_page()
        else:
            show_registration_page()
    else:
        show_main_app()

def show_login_page():
    st.markdown("### 🔑 Login")
    with st.form("login_form"):
        u = st.text_input("Benutzername").lower().strip()
        p = st.text_input("Passwort", type="password")
        if st.form_submit_button("Anmelden", use_container_width=True):
            df = hole_df("nutzer")
            if not df.empty and u in df['benutzername'].values:
                pw_hash = df[df['benutzername'] == u]['passwort'].values[0]
                if pw_hash == hash_passwort(p):
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.session_state.role = df[df['benutzername'] == u]['rolle'].values[0]
                    st.query_params["user"] = u
                    st.rerun()
                else: st.error("Passwort falsch.")
            else: st.error("Nutzer nicht gefunden.")
    
    if st.button("Noch kein Konto? Hier registrieren", use_container_width=True):
        st.session_state.auth_mode = "register"
        st.rerun()

def show_registration_page():
    st.markdown("### 📝 Registrierung")
    with st.form("reg_form"):
        new_u = st.text_input("Wunsch-Benutzername*")
        new_p = st.text_input("Passwort*", type="password")
        new_e = st.text_input("E-Mail*")
        c1, c2 = st.columns(2)
        new_vn = c1.text_input("Vorname")
        new_nn = c2.text_input("Nachname")
        new_al = st.number_input("Alter", min_value=0, max_value=120, value=25)
        agb = st.checkbox("Ich akzeptiere die Nutzungsbedingungen*")
        
        if st.form_submit_button("Konto erstellen", use_container_width=True):
            if new_u and new_p and new_e and agb:
                if registriere_nutzer(new_u, new_p, new_e, new_vn, new_nn, new_al, 1):
                    st.success("Erfolg! Du kannst dich jetzt einloggen.")
                    st.session_state.auth_mode = "login"
                    st.rerun()
                else: st.error("Benutzername oder E-Mail bereits vergeben.")
            else: st.warning("Bitte alle Pflichtfelder (*) ausfüllen.")

    if st.button("Zurück zum Login", use_container_width=True):
        st.session_state.auth_mode = "login"
        st.rerun()

def show_main_app():
    menu = ["👤 Mein Bereich", "💬 Feedback", "📄 Rechtliches"]
    if st.session_state.role == 'admin':
        menu.append("🛠️ Admin")
    
    choice = st.tabs(menu)
    
    with choice[0]: show_profile_area()
    with choice[1]: show_feedback_area()
    with choice[2]: show_legal_area()
    
    if st.session_state.role == 'admin':
        with choice[3]: show_admin_area()

    # --- ZENTRALER LOGOUT (Wichtig!) ---
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.query_params.clear()
        st.session_state.logged_in = False
        st.rerun()

if __name__ == "__main__":
    main()
