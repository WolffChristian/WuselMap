import streamlit as st
from database_manager import (
    hole_df, 
    sende_nachricht, 
    hole_nachrichten, 
    fuege_freund_hinzu, 
    hole_freundesliste,
    hole_crew_anfragen, 
    bestaetige_anfrage, 
    lehne_anfrage_ab
)

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
                    if st.button(f"↩️ Antworten an {r['von_nutzer']}", key=f"reply_{i}"):
                        st.session_state.msg_target = r['von_nutzer']
                        st.success(f"Empfänger {r['von_nutzer']} ausgewählt!")
        else:
            st.info("Dein Postfach ist leer.")

    with t2:
        meine_freunde = hole_freundesliste(st.session_state.user)
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
                            if 'msg_target' in st.session_state: del st.session_state.msg_target
                            st.rerun()

def show_wusel_crew():
    st.subheader("👥 Wusel-Crew")
    
    # 1. Offene Anfragen anzeigen
    anfragen = hole_crew_anfragen(st.session_state.user)
    if anfragen:
        with st.expander(f"🔔 Du hast {len(anfragen)} neue Crew-Anfragen!", expanded=True):
            for absender in anfragen:
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"**{absender}** möchte in deine Crew.")
                if c2.button("✅ Ja", key=f"yes_{absender}"):
                    if bestaetige_anfrage(absender, st.session_state.user):
                        st.success("Bestätigt!"); st.rerun()
                if c3.button("❌ Nein", key=f"no_{absender}"):
                    if lehne_anfrage_ab(absender, st.session_state.user):
                        st.rerun()
        st.divider()

    # 2. Verbesserte Suche (Nutzername ODER echter Name)
    with st.expander("🔍 Neue Leute zur Crew hinzufügen"):
        suche = st.text_input("Name oder Nutzername eingeben").strip().lower()
        if st.button("Anfrage senden"):
            df_u = hole_df("nutzer")
            if not df_u.empty:
                # Wir suchen in allen Namens-Spalten
                df_u['voller_name'] = df_u['vorname'].str.lower() + " " + df_u['nachname'].str.lower()
                
                match = df_u[
                    (df_u['benutzername'].str.lower() == suche) | 
                    (df_u['vorname'].str.lower() == suche) | 
                    (df_u['nachname'].str.lower() == suche) |
                    (df_u['voller_name'] == suche)
                ]
                
                if not match.empty:
                    gefunden_un = match.iloc[0]['benutzername']
                    vorname = match.iloc[0]['vorname']
                    
                    if gefunden_un != st.session_state.user.lower():
                        if fuege_freund_hinzu(st.session_state.user, gefunden_un):
                            st.info(f"Anfrage an {vorname} ({gefunden_un}) wurde gesendet!")
                    else: st.warning("Das bist du selbst!")
                else: st.error("Niemanden unter diesem Namen gefunden.")
    
    st.divider()

    # 3. Bestätigte Crew
    crew = hole_freundesliste(st.session_state.user)
    if crew:
        st.write("Deine Crew:")
        for f in crew:
            c1, c2 = st.columns([3, 1])
            with c1: st.write(f"🧗 **{f}**")
            with c2:
                if st.button("📩 Funk", key=f"btn_{f}"):
                    st.session_state.msg_target = f
                    st.info(f"Geh zu 'Wuselfunk' um {f} zu schreiben.")
    else:
        st.caption("Deine Crew ist noch leer.")
