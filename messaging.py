import streamlit as st
from database_manager import hole_df, sende_nachricht, hole_nachrichten, fuege_freund_hinzu, hole_freundesliste

# --- Ersetze den Bereich in messaging.py ---

def show_wuselfunk():
    st.subheader("📻 Wuselfunk (Nachrichten)")
    
    t1, t2 = st.tabs(["📭 Posteingang", "✍️ Nachricht schreiben"])
    
    with t1:
        df_m = hole_nachrichten(st.session_state.user)
        if not df_m.empty:
            for i, r in df_m.iterrows():
                with st.container(border=True):
                    st.write(f"**Von:** {r['von_nutzer']}")
                    st.write(r['nachricht'])
                    st.caption(f"{r['zeitpunkt']}")
                    # FIX: Antwort-Button hinzugefügt
                    if st.button(f"↩️ Antworten an {r['von_nutzer']}", key=f"reply_{i}"):
                        st.session_state.msg_target = r['von_nutzer']
                        st.success(f"Empfänger {r['von_nutzer']} wurde ausgewählt! Geh jetzt zum Tab 'Nachricht schreiben'.")
        else:
            st.info("Dein Postfach ist leer.")

    with t2:
        meine_freunde = hole_freundesliste(st.session_state.user)
        
        # Check: Wurde ein Empfänger aus der Crew oder per Antwort-Button gewählt?
        default_index = 0
        if 'msg_target' in st.session_state and st.session_state.msg_target in meine_freunde:
            default_index = meine_freunde.index(st.session_state.msg_target)

        if not meine_freunde:
            st.warning("Du hast noch niemanden in deiner Crew.")
        else:
            with st.form("send_msg", clear_on_submit=True):
                ziel = st.selectbox("An wen?", meine_freunde, index=default_index)
                text = st.text_area("Deine Nachricht")
                if st.form_submit_button("Abschicken"):
                    if text:
                        if sende_nachricht(st.session_state.user, ziel, text):
                            st.success(f"Funkspruch an {ziel} ist raus!")
                            if 'msg_target' in st.session_state:
                                del st.session_state.msg_target
                            st.rerun()
                        else:
                            st.error("Funkstörung – Nachricht konnte nicht gesendet werden.")
def show_wusel_crew():
    st.subheader("👥 Wusel-Crew")
    
    # 1. Nutzer suchen
    with st.expander("🔍 Neue Leute zur Crew hinzufügen"):
        suche = st.text_input("Nutzername eingeben").strip().lower()
        if st.button("Hinzufügen"):
            df_u = hole_df("nutzer")
            if suche in df_u['benutzername'].values:
                if suche != st.session_state.user.lower():
                    if fuege_freund_hinzu(st.session_state.user, suche):
                        st.success(f"{suche} ist jetzt in deiner Crew!")
                        st.rerun()
                else:
                    st.warning("Du bist schon dein eigener bester Freund!")
            else:
                st.error("Nutzer existiert nicht.")
    
    st.divider()

    # 2. Liste der Crew-Mitglieder
    crew = hole_freundesliste(st.session_state.user)
    if crew:
        for f in crew:
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"🧗 **{f}**")
            with c2:
                # Der "Direkt-Funk" Button
                if st.button("📩 Funk", key=f"btn_{f}"):
                    st.session_state.msg_target = f
                    st.info(f"Empfänger {f} ausgewählt. Geh jetzt zum Tab 'Wuselfunk'!")
                    # Optional: st.rerun() um den Status sofort zu zeigen
    else:
        st.caption("Deine Crew ist noch leer.")
