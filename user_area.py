import streamlit as st
import base64
# WICHTIG: Hier holen wir uns die Funktionen aus der database_manager.py
from database_manager import get_all_playgrounds, sende_vorschlag, bestaetige_spot

# SEITE 1: Liste der Spots
def show_user_area():
    st.subheader("📍 Aktuelle Kletter-Spots")
    spots = get_all_playgrounds()
    
    if not spots:
        st.write("Keine Spots gefunden.")
        return

    for r in spots:
        with st.expander(f"📍 {r['name']} ({r['stadt']})"):
            if r.get('bild_data'):
                st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
            
            st.write(f"**Adresse:** {r['adresse']}, {r['plz']} {r['stadt']}")
            st.write(f"**Alter:** {r['alter_empf']}")
            
            if r.get('hat_wc'):
                st.info("🚻 WC vor Ort vorhanden")
            
            check = r.get('zuletzt_bestaetigt')
            st.caption(f"✅ Zuletzt bestätigt am: {check if check else 'Noch nie'}")
            
            if st.button("👍 Ich bin hier!", key=f"btn_{r['id']}"):
                if bestaetige_spot(r['id']):
                    st.success("Danke!")
                    st.rerun()

# SEITE 2: Das Formular für Sabrina
def show_proposal_area():
    st.subheader("💡 Neuen Spot vorschlagen")
    
    with st.form("vorschlag_form", clear_on_submit=True):
        v_name = st.text_input("Name*")
        v_adresse = st.text_input("Straße & Hausnr.*")
        col1, col2 = st.columns(2)
        with col1: v_plz = st.text_input("PLZ*")
        with col2: v_stadt = st.text_input("Stadt*", value="Varel")
        
        v_bundesland = st.selectbox("Bundesland", ["Niedersachsen", "Bremen", "Hamburg"])
        v_alter = st.selectbox("Alter", ["0-3 Jahre", "3-12 Jahre", "Alle"])
        v_wc = st.checkbox("WC vorhanden?")
        v_bild = st.file_uploader("Foto (max 2MB)", type=["jpg", "png"])
        
        if st.form_submit_button("Absenden"):
            if v_name and v_adresse and v_plz:
                img_b64 = None
                if v_bild:
                    if v_bild.size > 2 * 1024 * 1024:
                        st.error("Bild zu groß!")
                        return
                    img_b64 = base64.b64encode(v_bild.read()).decode()
                
                if sende_vorschlag(v_name, v_adresse, v_alter, st.session_state.user_id, 
                                   v_bundesland, v_plz, v_stadt, img_b64, v_wc):
                    st.success("Vorschlag gespeichert!")
            else:
                st.warning("Pflichtfelder ausfüllen!")
