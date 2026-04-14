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

# --- PRIVATER BEREICH ---
def show_wuselfunk():
    st.subheader("🔒 Wuselfunk (Privat)")
    t1, t2 = st.tabs(["📭 Posteingang", "✍️ Nachricht schreiben"])
    
    with t1:
        df_priv = hole_nachrichten(st.session_state.user, nur_privat=True)
        if not df_priv.empty:
            for i, r in df_priv.iterrows():
                with st.container(border=True):
                    st.write(f"**Von:** {r['von_nutzer']} ➡️ **An:** {r['recipient_id']}")
                    st.write(r['nachricht'])
                    st.caption(f"{r['zeitpunkt']}")
                    if st.button(f"↩️ Antworten an {r['von_nutzer']}", key=f"priv_reply_{i}"):
                        st.session_state.msg_target = r['von_nutzer']
                        st.rerun()
        else:
            st.info("Dein privates Postfach ist leer.")

    with t2:
        meine_freunde = hole_freundesliste(st.session_state.user)
        default_index = 0
        if 'msg_target' in st.session_state and st.session_state.msg_target in meine_freunde:
            default_index = meine_freunde.index(st.session_state.msg_target)

        if not meine_freunde:
            st.warning("Du hast noch niemanden in deiner Crew für private Nachrichten.")
        else:
            with st.form("send_priv_msg", clear_on_submit=True):
                ziel = st.selectbox("An wen aus deiner Crew?", meine_freunde, index=default_index)
                text = st.text_area("Deine private Nachricht")
                if st.form_submit_button("Abschicken"):
                    if text:
                        if sende_nachricht(st.session_state.user, ziel, text, is_private=True):
                            st.success(f"Private Nachricht an {ziel} gesendet!")
                            if 'msg_target' in st.session_state: del st.session_state.msg_target
                            st.rerun()

# --- ÖFFENTLICHER BEREICH ---
def show_spielplatzfunk():
    st.subheader("📢 Spielplatzfunk (Öffentlich)")
    t1, t2 = st.tabs(["📜 Aktuelle Meldungen", "🛰️ Funkspruch absetzen"])
    
    with t1:
        df_pub = hole_nachrichten(st.session_state.user, nur_privat=False)
        if not df_pub.empty:
            for i, r in df_pub.iterrows():
                with st.container(border=True):
                    # Anzeige welcher Spielplatz betroffen ist
                    st.markdown(f"**📍 {r['spot_name']}**")
                    st.write(f"*{r['von_nutzer']}:* {r['nachricht']}")
                    st.caption(f"{r['zeitpunkt']}")
        else:
            st.info("Noch keine öffentlichen Meldungen vorhanden.")

    with t2:
        st.write("Informiere andere Eltern über die Situation vor Ort.")
        df_spots = hole_df("spielplaetze")
        spot_namen = ["Allgemein"] + df_spots['Standort'].tolist() if not df_spots.empty else ["Allgemein"]
        
        with st.form("send_pub_msg", clear_on_submit=True):
            betroffener_spot = st.selectbox("Welchen Spielplatz betrifft es?", spot_namen)
            text = st.text_area("Was möchtest du mitteilen? (z.B. Eiswagen da, Wespen am Klettergerüst...)")
            if st.form_submit_button("Abschicken"):
                if text:
                    if sende_nachricht(st.session_state.user, 'GLOBAL', text, is_private=False, spot_name=betroffener_spot):
                        st.success("Dein Funkspruch wurde veröffentlicht!")
                        st.rerun()

def show_wusel_crew():
    st.subheader("👥 Wusel-Crew")
    anfragen = hole_crew_anfragen(st.session_state.user)
    if anfragen:
        with st.expander(f"🔔 Neue Crew-Anfragen!", expanded=True):
            for absender in anfragen:
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"**{absender}**")
                if c2.button("✅ Ja", key=f"yes_{absender}"):
                    if bestaetige_anfrage(absender, st.session_state.user): st.rerun()
                if c3.button("❌ Nein", key=f"no_{absender}"):
                    if lehne_anfrage_ab(absender, st.session_state.user): st.rerun()

    with st.expander("🔍 Crew erweitern"):
        suche = st.text_input("Nutzer suchen").strip().lower()
        if st.button("Suchen"):
            df_u = hole_df("nutzer")
            treffer = df_u[df_u['benutzername'].str.lower().str.contains(suche)]
            for _, row in treffer.iterrows():
                un = row['benutzername']
                if un.lower() == st.session_state.user.lower(): continue
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{row['vorname']} {row['nachname']}** (@{un})")
                if c2.button("Einladen", key=f"inv_{un}"):
                    if fuege_freund_hinzu(st.session_state.user, un):
                        st.success(f"Anfrage an {un} raus!")

    crew = hole_freundesliste(st.session_state.user)
    if crew:
        for f in crew:
            c1, c2 = st.columns([3, 1])
            c1.write(f"🧗 **{f}**")
            if c2.button(f"📩 Funk", key=f"btn_{f}"):
                st.session_state.msg_target = f
                st.info(f"Geh zum Wuselfunk um {f} privat zu schreiben.")