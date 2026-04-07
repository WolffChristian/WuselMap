import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import os
from database_manager import hole_df, sende_vorschlag, sende_feedback, optimiere_bild, check_duplikat

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

def show_user_area():
    st.title("📍 KletterKompass Suche")
    
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Ort / Adresse", "Varel")
    with c2: km = st.slider("Radius (km)", 1, 100, 20)
    
    if st.button("🔍 Suchen", type="primary"):
        # ... (Gleiche Suchlogik wie vorher)
        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        res = gc.geocode(adr + ", Deutschland")
        if res:
            slat, slon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
            df = hole_df("spielplaetze")
            if not df.empty:
                df['lat'] = pd.to_numeric(df['lat'], errors='coerce'); df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
                df = df.dropna(subset=['lat', 'lon'])
                df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                final = df[df['distanz'] <= km].sort_values('distanz')
                
                if not final.empty:
                    col_l, col_r = st.columns([1, 1.5])
                    with col_l:
                        for i, r in final.iterrows():
                            with st.expander(f"📍 {r['Standort']} ({round(r['distanz'], 1)} km)"):
                                if r.get('bild_data'):
                                    st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
                                st.write(f"**Ort:** {r['stadt']} ({r['plz']})")
                                st.write(f"**Alter:** {r['altersfreigabe']}")
                    with col_r:
                        fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10, height=500)
                        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0}, mapbox_center={"lat": slat, "lon": slon})
                        st.plotly_chart(fig, use_container_width=True)

    if st.session_state.logged_in:
        st.write("---")
        with st.expander("💡 Neuen Spielplatz vorschlagen"):
            with st.form("v_form"):
                v_n = st.text_input("Name des Spielplatzes")
                v_a = st.text_input("Straße & Hausnummer")
                v_plz = st.text_input("Postleitzahl")
                v_stadt = st.text_input("Stadt")
                v_bund = st.selectbox("Bundesland", ["Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen", "Mecklenburg-Vorpommern", "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland", "Sachsen", "Sachsen-Anhalt", "Schleswig-Holstein", "Thüringen"])
                v_img = st.file_uploader("Bild hochladen (wird automatisch optimiert)", type=["jpg", "jpeg", "png"])
                
                if st.form_submit_button("Vorschlag einsenden"):
                    if v_n and v_plz:
                        if check_duplikat("spielplaetze", v_n, v_plz) or check_duplikat("vorschlaege", v_n, v_plz):
                            st.warning("⚠️ Dieser Spielplatz wurde bereits eingetragen oder vorgeschlagen!")
                        else:
                            bild_base64 = optimiere_bild(v_img)
                            sende_vorschlag(v_n, v_a, "Alle", st.session_state.user, v_bund, v_plz, v_stadt, bild_base64)
                            st.success("Erfolg! Der Admin prüft dein Bild und die Daten.")
                    else: st.warning("Name und PLZ sind Pflicht!")
