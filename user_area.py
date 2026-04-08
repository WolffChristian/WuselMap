import streamlit as st
import base64
from database_manager import get_all_playgrounds, sende_vorschlag, bestaetige_spot

def show_user_area():
    st.subheader("📍 Spots")
    spots = get_all_playgrounds()
    for r in spots:
        with st.expander(f"{r['name']}"):
            if r.get('bild_data'):
                st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
            st.write(f"Adresse: {r['adresse']}")
            if r.get('hat_wc'): st.info("🚻 WC vorhanden")
            if st.button("👍 Ich bin hier", key=f"btn_{r['id']}"):
                bestaetige_spot(r['id'])
                st.rerun()

def show_proposal_area():
    st.subheader("💡 Neuer Spot")
    with st.form("v_form", clear_on_submit=True):
        n = st.text_input("Name*")
        ad = st.text_input("Straße*")
        p = st.text_input("PLZ*")
        s = st.text_input("Stadt*", value="Varel")
        al = st.selectbox("Alter", ["0-3", "3-12", "Alle"])
        wc = st.checkbox("WC vorhanden?")
        f = st.file_uploader("Foto")
        if st.form_submit_button("Abschicken"):
            img = base64.b64encode(f.read()).decode() if f else None
            if sende_vorschlag(n, ad, al, st.session_state.user_id, "Niedersachsen", p, s, img, wc):
                st.success("Gespeichert!")
