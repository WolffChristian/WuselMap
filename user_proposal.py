import streamlit as st
from opencage.geocoder import OpenCageGeocode
from database_manager import sende_vorschlag, optimiere_bild, hole_df
from streamlit_js_eval import get_geolocation
import time

def show_proposal_section():
    st.subheader("💡 Spot vorschlagen oder ergänzen")
    
    # --- SPEICHER INITIALISIEREN ---
    if 'gps_lat' not in st.session_state: st.session_state.gps_lat = 0.0
    if 'gps_lon' not in st.session_state: st.session_state.gps_lon = 0.0
    if 'gps_adr' not in st.session_state: st.session_state.gps_adr = ""

    df_spots = hole_df("spielplaetze")
    modus = st.radio("Was möchtest du tun?", ["Neuen Spot melden", "Bestehenden Spot ergänzen"], horizontal=True)
    
    if modus == "Neuen Spot melden":
        # Den Standort-Abruf außerhalb des Buttons platzieren, damit er "aktiv" bleibt
        if st.button("📍 Standort vom Handy abrufen", use_container_width=True):
            with st.spinner("Hole GPS-Daten... Bitte am Handy 'Zulassen' klicken"):
                loc = get_geolocation()
                
                # Wir warten kurz, bis das GPS geantwortet hat
                if loc and 'coords' in loc:
                    st.session_state.gps_lat = loc['coords']['latitude']
                    st.session_state.gps_lon = loc['coords']['longitude']
                    st.session_state.gps_adr = "Koordinaten via GPS erfasst"
                    st.success("📍 Erfolg! Die Felder wurden befüllt.")
                    time.sleep(1) # Kurz warten für die Optik
                    st.rerun()
                else:
                    st.error("GPS konnte nicht empfangen werden. Hast du den Standortzugriff erlaubt?")

    # --- DAS FORMULAR ---
    with st.form("v_form_main", clear_on_submit=True):
        if modus == "Bestehenden Spot ergänzen" and not df_spots.empty:
            v_n = st.selectbox("Welchen Spielplatz meinst du?", options=df_spots['Standort'].tolist())
        else:
            v_n = st.text_input("Name des Spielplatzes*", placeholder="z.B. Piratenschiff")
        
        # Die Felder ziehen sich jetzt die Daten
        v_s = st.text_input("Straße & Hausnummer*", value=st.session_state.gps_adr)
        
        col_gps1, col_gps2 = st.columns(2)
        # Wir nutzen text_input statt number_input, das ist weniger fehleranfällig beim Vorbefüllen
        f_lat = col_gps1.text_input("Breitengrad", value=str(st.session_state.gps_lat))
        f_lon = col_gps2.text_input("Längengrad", value=str(st.session_state.gps_lon))

        v_st = st.text_input("Stadt*", value="Varel") 
        v_alt = st.selectbox("Altersgruppe", ["0-3", "3-6", "6-12", "Alle"])
        
        # ... Rest des Formulars ...
        st.write("---")
        v_img = st.file_uploader("Foto hochladen", type=["jpg", "png", "jpeg"])
        ds = st.checkbox("Ich bestätige: Keine Personen auf dem Foto erkennbar*")
        
        if st.form_submit_button("Vorschlag einsenden", use_container_width=True):
            if v_n and v_st and ds:
                b_data = optimiere_bild(v_img)
                # Hier wandeln wir die Text-Koordinaten wieder in Zahlen um
                try:
                    final_lat = float(f_lat)
                    final_lon = float(f_lon)
                except:
                    final_lat, final_lon = 0.0, 0.0

                if sende_vorschlag(v_n, v_s, v_alt, st.session_state.user, "Niedersachsen", "00000", v_st, 
                                  b_data, 1, "Neu gemeldet", 0, 0, 0, final_lat, final_lon, 0):
                    st.success("✅ Danke! Dein Beitrag wird geprüft.")
                    # Speicher leeren
                    st.session_state.gps_lat = 0.0
                    st.session_state.gps_lon = 0.0
                    st.session_state.gps_adr = ""
                    st.balloons()