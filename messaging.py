import streamlit as st
from database_manager import hole_df, sende_nachricht, hole_nachrichten, fuege_freund_hinzu, hole_freundesliste

def show_messaging_area():
    st.subheader("📩 Wusel-Funk & Crew")
    
    t1, t2, t3 = st.tabs(["📭 Posteingang", "✍️ Nachricht schreiben", "👥 Meine Crew"])
    
    # --- TAB 1: POSTEINGANG ---
    with t1:
        df_m = hole_nachrichten(st.session_state.user)
        if not df_m.empty:
            for i, r in df_m.iterrows():
                with st.container(border=True):
                    st.write(f"**Von:** {r['von_nutzer']}")
                    st.write(r['nachricht'])
                    st.caption(f"{r['zeitpunkt']}")
        else:
            st.info("Dein Postfach ist leer.")

    # --- TAB 2: NACHRICHT SCHREIBEN ---
    with t2:
        meine_freunde = hole_freundesliste(st.session_state.user)
        
        if not meine_freunde:
            st.warning("Du hast noch niemanden in deiner Crew. Suche unter 'Meine Crew' nach Nutzern!")
        
        with st.form("send_msg", clear_on_submit=True):
            # Hier erscheinen jetzt nur deine Freunde zur Auswahl
            ziel = st.selectbox("An wen?", meine_freunde if meine_freunde else ["Keine Kontakte"])
            text = st.text_area("Deine Nachricht")
            if st.form_submit_button("Abschicken"):
                if text and ziel != "Keine Kontakte":
                    if sende_nachricht(st.session_state.user, ziel, text):
                        st.success(f"Nachricht an {ziel} gesendet!")
                    else:
                        st.error("Fehler beim Senden.")

    # --- TAB 3: MEINE CREW (FREUNDESLISTE) ---
    with t3:
        st.write("### 🔍 Nutzer suchen & hinzufügen")
        suche = st.text_input("Nutzername eingeben").strip().lower()
        if st.button("Hinzufügen"):
            df_u = hole_df("nutzer")
            # Prüfen ob Nutzer existiert
            if suche in df_u['benutzername'].values:
                if suche != st.session_state.user.lower():
                    if fuege_freund_hinzu(st.session_state.user, suche):
                        st.success(f"{suche} wurde deiner Crew hinzugefügt!")
                        st.rerun()
                else:
                    st.warning("Du kannst dich nicht selbst hinzufügen.")
            else:
                st.error("Nutzer nicht gefunden.")
        
        st.divider()
        st.write("### 👥 Deine Crew")
        crew = hole_freundesliste(st.session_state.user)
        if crew:
            for f in crew:
                st.write(f"🧗 **{f}**")
        else:
            st.caption("Noch keine Kontakte gespeichert.")
