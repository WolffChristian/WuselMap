import streamlit as st
from streamlit_js_eval import get_geolocation
import time

def show_proposal_section():
    st.subheader("💡 Spot vorschlagen oder ergänzen")
    
    # 1. Initialisierung
    if 'gps_lat' not in st.session_state: st.session_state.gps_lat = 0.0
    if 'gps_lon' not in st.session_state: st.session_state.gps_lon = 0.0
    if 'gps_active' not in st.session_state: st.session_state.gps_active = False

    # 2. Der Trigger-Button
    if st.button("📍 Meinen Standort jetzt erfassen", use_container_width=True):
        st.session_state.gps_active = True
        st.rerun()

    # 3. Der eigentliche Abruf (läuft nur, wenn aktiv geschaltet)
    if st.session_state.gps_active:
        with st.spinner("Warte auf Satelliten... Bitte am Handy 'Zulassen' klicken"):
            loc = get_geolocation() # Diese Zeile braucht eine Millisekunde
            
            if loc and 'coords' in loc:
                st.session_state.gps_lat = loc['coords']['latitude']
                st.session_state.gps_lon = loc['coords']['longitude']
                st.session_state.gps_active = False # Wieder ausschalten
                st.success("✅ Koordinaten geladen!")
                st.rerun()
            # Falls nach 5-10 Sek nichts kommt, könnte man hier einen Abbruch-Button zeigen

    # --- DAS FORMULAR ---
    with st.form("v_form_main", clear_on_submit=True):
        # ... dein restlicher Code ...
        col1, col2 = st.columns(2)
        f_lat = col1.text_input("Breitengrad", value=str(st.session_state.gps_lat))
        f_lon = col2.text_input("Längengrad", value=str(st.session_state.gps_lon))
        
        # WICHTIG: Ersetze 'use_container_width=True' durch 'width="stretch"' 
        # (Wegen der Warnung, die wir vorhin im Log gesehen haben)
        submit = st.form_submit_button("Vorschlag einsenden")