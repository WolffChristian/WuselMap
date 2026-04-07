import streamlit as st
import base64
from database_manager import get_all_playgrounds, sende_vorschlag

def show_user_area():
    st.subheader("📍 Spots in Varel")
    spots = get_all_playgrounds()
    for r in spots:
        with st.expander(f"{r['name']}"):
            if r.get('bild_data'):
                st.image(f"data:image/jpeg;base64,{r['bild_data']}")
            st.write(f"Adresse: {r['adresse']}")

def show_proposal_area():
    st.subheader("💡 Neuen Spot melden")
    with st.form("mein_form"):
        n = st.text_input("Name")
        a = st.text_input("Adresse")
        alt = st.selectbox("Alter", ["0-3", "3-12"])
        foto = st.file_uploader("Foto")
        if st.form_submit_button("Abschicken"):
            img = base64.b64encode(foto.read()).decode() if foto else None
            if sende_vorschlag(n, a, alt, st.session_state.user_id, img):
                st.success("Erledigt!")
