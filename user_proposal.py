import streamlit as st
from opencage.geocoder import OpenCageGeocode
from database_manager import sende_vorschlag, optimiere_bild

def show_proposal_section():
    """Bereich zum Einreichen neuer Spielplätze"""
    st.subheader("💡 Neuen Spot vorschlagen")
    
    with st.form("v_form_main", clear_on_submit=True):
        v_n = st.text_input("Name des Spielplatzes*", placeholder="z.B. Piratenschiff")
        v_s = st.text_input("Straße & Hausnummer oder Kreuzung*")
        v_st = st.text_input("Stadt*") 
        v_alt = st.selectbox("Altersgruppe", ["0-3", "3-6", "6-12", "Alle"])
        
        st.write("---")
        ausst_list = st.multiselect("Ausstattung", ["Rutsche", "Schaukel", "Seilbahn", "Klettergerüst", "Sandkasten", "Wippe", "Karussell"])
        
        v_img = st.file_uploader("Foto hochladen (optional)", type=["jpg", "png", "jpeg"])
        ds = st.checkbox("Ich bestätige: Keine Personen auf dem Foto erkennbar*")
        
        if st.form_submit_button("Vorschlag einsenden", use_container_width=True):
            missing = []
            if not v_n.strip(): missing.append("Name")
            if not v_s.strip(): missing.append("Adresse")
            if not v_st.strip(): missing.append("Stadt")
            if not ds: missing.append("Datenschutz-Häkchen")
            
            if not missing:
                gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                res = gc.geocode(f"{v_s}, {v_st}, Deutschland")
                if res:
                    f_lat, f_lon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
                    b_data = optimiere_bild(v_img)
                    if sende_vorschlag(v_n, v_s, v_alt, st.session_state.user, "Niedersachsen", "00000", v_st, b_data, 1, ", ".join(ausst_list), 0,0,0, f_lat, f_lon):
                        st.success(f"✅ '{v_n}' eingereicht!")
                        st.balloons()
                else: st.error("📍 Adresse nicht gefunden.")
            else:
                st.warning(f"⚠️ Bitte ausfüllen: {', '.join(missing)}")