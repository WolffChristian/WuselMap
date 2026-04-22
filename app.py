import streamlit as st
from database_manager import hole_df, hash_passwort, registriere_nutzer
from styles import apply_custom_css, show_header
from user_area import show_profile_area, show_feedback_area
from admin_area import show_admin_area
from legal_area import show_legal_area
from messaging import show_spielplatzfunk 
from user_map import show_map_section 

def main():
    apply_custom_css()
    show_header()
    
    st.warning("⚠️ **WuselMap Beta:** Wir optimieren gerade die Funktionen. 🧗‍♂️")

    # Session State initialisieren
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = "login"

    # Login-Check über URL-Parameter
    if not st.session_state.logged_in and "user" in st.query_params:
        u_name = st.query_params["user"]
        df = hole_df("nutzer")
        if not df.empty and u_name in df['benutzername'].values:
            st.session_state.logged_in = True
            st.session_state.user = u_name
            st.session_state.role = df[df['benutzername'] == u_name]['rolle'].values[0]

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
    # 1. Nutzerdaten für die Personalisierung abrufen
    df_n = hole_df("nutzer")
    user_row = df_n[df_n['benutzername'] == st.session_state.user]
    
    # Standardwerte
    mein_emoji = "👤" 
    bereichs_titel = "Mein Bereich"
    
    if not user_row.empty:
        u_data = user_row.iloc[0]
        # Emoji aus der DB laden
        mein_emoji = u_data.get('profil_emoji') or "👤"
        
        # Vornamen-Logik (z.B. Sabrinas Bereich)
        vn = u_data.get('vorname')
        if vn and str(vn).strip():
            # Grammatik: s, x, z Endungen erhalten nur ein Apostroph
            if vn.lower().endswith(('s', 'x', 'z')):
                bereichs_titel = f"{vn}' Bereich"
            else:
                bereichs_titel = f"{vn}s Bereich"

    # 2. Das Menü mit dynamischen Namen und Emoji zusammenbauen
    menu = ["📍 Suche", f"{mein_emoji} {bereichs_titel}", "📢 Funk", "💬 Feedback", "📄 Rechtliches"]
    
    if st.session_state.get('role') == 'admin':
        menu.append("🛠️ Admin")
    
    # Tabs erstellen
    choice = st.tabs(menu)
    
    # 3. Den Tabs die entsprechenden Funktionen zuordnen
    with choice[0]: show_map_section()
    with choice[1]: show_profile_area()  # Hier erscheint dein Foto und voller Name
    with choice[2]: show_spielplatzfunk()
    with choice[3]: show_feedback_area()
    with choice[4]: show_legal_area()
    
    if st.session_state.get('role') == 'admin' and len(choice) > 5:
        with choice[5]: show_admin_area()

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.query_params.clear()
        st.session_state.logged_in = False
        st.rerun()

if __name__ == "__main__":
    main()