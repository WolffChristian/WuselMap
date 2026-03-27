import streamlit as st
from database_manager import hash_passwort, hole_df, ausfuehren

def login_bereich():
    t1, t2, t3 = st.tabs(["🔑 Login", "📝 Registrierung", "❓ Passwort vergessen"])
    
    with t1:
        u = st.text_input("Nutzername", key="l_u")
        p = st.text_input("Passwort", type="password", key="l_p")
        if st.button("Anmelden", width='stretch'):
            hashed_p = hash_passwort(p)
            df = hole_df("SELECT nutzer_id, rolle FROM nutzer WHERE benutzername=%s AND passwort=%s", (u, hashed_p))
            if not df.empty:
                st.session_state.logged_in = True
                st.session_state.nutzer_id = int(df.iloc[0]['nutzer_id'])
                st.session_state.rolle = df.iloc[0]['rolle']
                st.rerun()
            else: st.error("Nutzername oder Passwort falsch.")

    with t2:
        with st.form("reg_form"):
            reg_u = st.text_input("Wunsch-Nutzername")
            reg_p = st.text_input("Sicheres Passwort", type="password")
            reg_m = st.text_input("E-Mail Adresse")
            reg_v = st.text_input("Vorname")
            reg_n = st.text_input("Nachname")
            reg_a = st.number_input("Alter", 0, 120, 30)
            reg_agb = st.checkbox("Ich akzeptiere die AGB & Datenschutz")
            if st.form_submit_button("Konto erstellen", width='stretch'):
                if reg_agb and all([reg_u, reg_p, reg_m]):
                    hashed_p = hash_passwort(reg_p)
                    sql = "INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, alter_wert, rolle) VALUES (%s,%s,%s,%s,%s,%s,'user')"
                    if ausfuehren(sql, (reg_u, hashed_p, reg_m, reg_v, reg_n, reg_a)):
                        st.success("Konto erstellt! Bitte einloggen.")
                        st.balloons()
                else: st.warning("Bitte alle Pflichtfelder ausfüllen.")

    with t3:
        st.subheader("Passwort vergessen?")
        with st.form("reset_form"):
            res_u = st.text_input("Nutzername")
            res_m = st.text_input("Deine E-Mail")
            new_p = st.text_input("Neues Passwort wählen", type="password")
            if st.form_submit_button("Passwort zurücksetzen"):
                df = hole_df("SELECT nutzer_id FROM nutzer WHERE benutzername=%s AND email=%s", (res_u, res_m))
                if not df.empty:
                    if ausfuehren("UPDATE nutzer SET passwort=%s WHERE benutzername=%s", (hash_passwort(new_p), res_u)):
                        st.success("Passwort wurde erfolgreich aktualisiert!")
                else: st.error("Daten passen nicht zusammen.")
