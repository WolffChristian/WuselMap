import streamlit as st
from opencage.geocoder import OpenCageGeocode
from database_manager import sende_vorschlag, optimiere_bild, hole_df

def show_proposal_section():
    st.subheader("💡 Spot vorschlagen oder ergänzen")
    df_spots = hole_df("spielplaetze")
    
    modus = st.radio("Was möchtest du tun?", ["Neuen Spot melden", "Bestehenden Spot ergänzen"], horizontal=True)
    
    with st.form("v_form_main", clear_on_submit=True):
        if modus == "Bestehenden Spot ergänzen" and not df_spots.empty:
            # NEU: Filter nach PLZ, um den richtigen Spot schneller zu finden
            plz_filter = st.text_input("Postleitzahl filtern (optional)", placeholder="z.B. 26316")
            
            filtered_list = df_spots
            if plz_filter:
                filtered_list = df_spots[df_spots['plz'].astype(str).str.contains(plz_filter)]
            
            v_n = st.selectbox("Welchen Spielplatz meinst du?", options=filtered_list['Standort'].tolist())
            st.info("Füll unten einfach aus, was ergänzt werden soll.")
        else:
            v_n = st.text_input("Name des Spielplatzes*", placeholder="z.B. Piratenschiff")
        
        
            
        v_s = st.text_input("Straße & Hausnummer oder Kreuzung*", placeholder="Für neue Spots zwingend")
        v_st = st.text_input("Stadt*", value="Varel") 
        v_alt = st.selectbox("Altersgruppe", ["0-3", "3-6", "6-12", "Alle"])
        
        st.write("---")
        ausst_list = st.multiselect("Ausstattung", ["Rutsche", "Schaukel", "Seilbahn", "Klettergerüst", "Sandkasten", "Wippe", "Karussell", "Trampolin", "Fußballplatz"])
        
        # NEU: Zusätzliche Features für User
        st.write("**Zusatzausstattung:**")
        col_ex1, col_ex2, col_ex3 = st.columns(3)
        v_schatten = col_ex1.checkbox("🌳 Schatten")
        v_sitze = col_ex2.checkbox("🪑 Sitze")
        v_parken = col_ex3.checkbox("🚗 Parkplätze")
        
        v_img = st.file_uploader("Foto hochladen", type=["jpg", "png", "jpeg"])
        ds = st.checkbox("Ich bestätige: Keine Personen auf dem Foto erkennbar*")
        
        if st.form_submit_button("Vorschlag einsenden", use_container_width=True):
            if v_n and v_st and ds:
                # GPS Suche (nur wenn Adresse angegeben wurde)
                f_lat, f_lon = 0.0, 0.0
                if v_s:
                    gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                    res = gc.geocode(f"{v_s}, {v_st}, Deutschland")
                    if res:
                        f_lat, f_lon = res[0]['geometry']['lat'], res[0]['geometry']['lng']

                b_data = optimiere_bild(v_img)
                # sende_vorschlag bekommt nun die neuen Parameter
                if sende_vorschlag(v_n, v_s, v_alt, st.session_state.user, "Niedersachsen", "00000", v_st, 
                                 b_data, 1, ", ".join(ausst_list), 
                                 1 if v_schatten else 0, 1 if v_sitze else 0, 0, f_lat, f_lon, 
                                 1 if v_parken else 0): # Parkplatz-Parameter
                    st.success(f"✅ Danke! Dein Beitrag zu '{v_n}' wird geprüft.")
                    st.balloons()
            else:
                st.warning("⚠️ Bitte Name, Stadt und Datenschutz-Check ausfüllen.")