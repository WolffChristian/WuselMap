import streamlit as st
from database_manager import hole_df, aktualisiere_profil

def show_profile_section():
    """Profil-Bearbeitung für den Nutzer"""
    df_u = hole_df("nutzer")
    if df_u.empty:
        st.error("Nutzerdaten konnten nicht geladen werden.")
        return

    u_data = df_u[df_u['benutzername'] == st.session_state.user].iloc[0]
    
    with st.form("p_data_form"):
        st.markdown(f"### Hallo {st.session_state.user}!")
        ne = st.text_input("E-Mail", value=u_data['email'])
        nv = st.text_input("Vorname", value=u_data['vorname'])
        nn = st.text_input("Nachname", value=u_data['nachname'])
        na = st.number_input("Alter (Jahre)", value=int(u_data['alter_jahre']))
        emo = st.selectbox("Emoji", ["🧗", "🤸", "🦁", "🚀", "🌈", "🎈"])
        
        if st.form_submit_button("Änderungen speichern"):
            if aktualisiere_profil(st.session_state.user, ne, nv, nn, na, emo):
                st.success("Gespeichert!"); st.rerun()
            else:
                st.error("Fehler beim Speichern.")