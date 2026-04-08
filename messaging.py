import streamlit as st
from database_manager import hole_df, sende_nachricht, hole_nachrichten

def show_messaging_area():
    st.subheader("📩 Wusel-Funk (Nachrichten)")
    
    t1, t2 = st.tabs(["Posteingang", "Nachricht schreiben"])
    
    with t1:
        df_m = hole_nachrichten(st.session_state.user)
        if not df_m.empty:
            for i, r in df_m.iterrows():
                status = "🔵" if r['gelesen'] == 0 else "⚪"
                with st.container(border=True):
                    st.write(f"{status} **Von:** {r['von_nutzer']}")
                    st.write(r['nachricht'])
                    st.caption(f"Gesendet am: {r['zeitpunkt']}")
        else:
            st.write("Dein Postfach ist leer.")

    with t2:
        df_u = hole_df("nutzer")
        nutzer_liste = df_u['benutzername'].tolist() if not df_u.empty else []
        
        # Den eigenen Namen aus der Liste entfernen
        if st.session_state.user in nutzer_liste:
            nutzer_liste.remove(st.session_state.user)
            
        with st.form("send_msg", clear_on_submit=True):
            ziel = st.selectbox("Empfänger", nutzer_liste)
            text = st.text_area("Deine Nachricht")
            if st.form_submit_button("Abschicken"):
                if text and sende_nachricht(st.session_state.user, ziel, text):
                    st.success(f"Nachricht an {ziel} gesendet!")
                else:
                    st.error("Fehler beim Senden.")
