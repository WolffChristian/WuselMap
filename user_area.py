import streamlit as st
import base64
from database_manager import get_all_playgrounds, sende_vorschlag, bestaetige_spot

def show_user_area():
    st.subheader("📍 Kletter-Spots in Varel")
    spots = get_all_playgrounds()
    if not spots:
        st.info("Noch keine Spots vorhanden.")
        return
    for r in spots:
        with st.expander(f"📍 {r['name']} ({r['stadt']})"):
            if r.get('bild_data'):
                st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
            st.write(f"**Alter:** {r['alter_empf']}")
            if r.get('hat_wc'): st.info("🚻 WC vor Ort")
            
            datum = r.get('zuletzt_bestaetigt')
            st.caption(f"✅ Zuletzt bestätigt: {datum if datum else 'Noch nie'}")
            if st.button("👍 Ich bin hier!", key=f"btn_{r['id']}"):
                if bestaetige_spot(r['id']): st.rerun()

def show_proposal_area():
    st.subheader("💡 Neuen Spot vorschlagen")
    with st.form("v_form", clear_on_submit=True):
        name = st.text_input("Name des Spots*")
        adr = st.text_input("Straße & Nr.*")
        col1, col2 = st.columns(2)
        with col1: plz = st.text_input("PLZ*")
        with col2: stadt = st.text_input("Stadt*", value="Varel")
        alt = st.selectbox("Alter", ["0-3", "3-12", "Alle"])
        wc = st.checkbox("Hat ein WC?")
        bild = st.file_uploader("Foto (max. 2MB)", type=["jpg", "png"])
        if st.form_submit_button("Absenden"):
            if name and adr and plz:
                img_b64 = base64.b64encode(bild.read()).decode() if bild else None
                if sende_vorschlag(name, adr, alt, st.session_state.user_id, "Niedersachsen", plz, stadt, img_b64, wc):
                    st.success("Danke! Christian prüft den Spot.")
            else:
                st.error("Pflichtfelder fehlen!")
