import streamlit as st
from streamlit_js_eval import get_geolocation
from database_manager import sende_vorschlag, optimiere_bild, hole_df
import time

def show_proposal_section():
    st.subheader("💡 Spot vorschlagen oder ergänzen")
    
    # --- 1. SPEICHER INITIALISIEREN ---
    if 'gps_lat' not in st.session_state: st.session_state.gps_lat = 0.0
    if 'gps_lon' not in st.session_state: st.session_state.gps_lon = 0.0
    if 'gps_active' not in st.session_state: st.session_state.gps_active = False

    df_spots = hole_df("spielplaetze")
    modus = st.radio("Was möchtest du tun?", ["Neuen Spot melden", "Bestehenden Spot ergänzen"], horizontal=True)
    
    # --- 2. GPS LOGIK (Stabil außerhalb des Formulars) ---
    if modus == "Neuen Spot melden":
        if st.button("📍 Standort vom Handy abrufen", use_container_width=True):
            st.session_state.gps_active = True
            st.rerun()

        if st.session_state.gps_active:
            with st.spinner("Hole GPS-Daten..."):
                loc = get_geolocation()
                if loc and 'coords' in loc:
                    st.session_state.gps_lat = loc['coords']['latitude']
                    st.session_state.gps_lon = loc['coords']['longitude']
                    st.session_state.gps_active = False
                    st.success("📍 Koordinaten erfasst!")
                    st.rerun()

    # --- 3. DAS KOMPLETTE FORMULAR ---
    with st.form("v_form_main", clear_on_submit=True):
        if modus == "Bestehenden Spot ergänzen" and not df_spots.empty:
            v_n = st.selectbox("Welchen Spielplatz meinst du?", options=df_spots['Standort'].tolist())
        else:
            v_n = st.text_input("Name des Spielplatzes*", placeholder="z.B. Piratenschiff")
        
        # Adresse und Stadt
        v_s = st.text_input("Straße & Hausnummer*", placeholder="Musterstraße 1")
        v_st = st.text_input("Stadt*", value="Varel")
        
        # GPS Felder (vorgefüllt durch den Button oben)
        col_gps1, col_gps2 = st.columns(2)
        f_lat = col_gps1.text_input("Breitengrad", value=str(st.session_state.gps_lat))
        f_lon = col_gps2.text_input("Längengrad", value=str(st.session_state.gps_lon))

        v_alt = st.selectbox("Altersgruppe", ["0-3", "3-6", "6-12", "Alle"])
        
        st.write("---")
        v_img = st.file_uploader("Foto hochladen", type=["jpg", "png", "jpeg"])
        ds = st.checkbox("Ich bestätige: Keine Personen auf dem Foto erkennbar*")
        
        # Button zum Absenden
        if st.form_submit_button("Vorschlag einsenden"):
            if v_n and v_st and ds:
                b_data = optimiere_bild(v_img)
                try:
                    final_lat = float(f_lat)
                    final_lon = float(f_lon)
                except:
                    final_lat, final_lon = 0.0, 0.0

                if sende_vorschlag(v_n, v_s, v_alt, st.session_state.user, "Niedersachsen", "26316", v_st, 
                                  b_data, 1, "Neu gemeldet", 0, 0, 0, final_lat, final_lon, 0):
                    st.success("✅ Danke! Dein Beitrag wird geprüft.")
                    # Speicher leeren nach Erfolg
                    st.session_state.gps_lat, st.session_state.gps_lon = 0.0, 0.0
                    st.balloons()
            else:
                st.error("Bitte fülle alle Pflichtfelder (*) aus.")