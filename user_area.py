import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import os
from database_manager import hole_df, sende_vorschlag, sende_feedback

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

def show_user_area():
    banner_path = "assets/Kletterkompass.png"
    if os.path.exists(banner_path): st.image(banner_path, use_container_width=True)
    st.title("Spielplätze finden")
    
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Ort / Adresse", "Varel")
    with c2: km = st.slider("Radius (km)", 1, 100, 20)
    
    if st.button("🔍 Suchen", type="primary"):
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
                                st.write(f"Alter: {r['altersfreigabe']}")
                    with col_r:
                        fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10, height=500)
                        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0}, mapbox_center={"lat": slat, "lon": slon})
                        st.plotly_chart(fig, use_container_width=True)
                else: st.warning("Nichts in der Nähe gefunden.")
        else: st.error("Ort unbekannt.")

    if st.session_state.logged_in:
        st.write("---")
        cf1, cf2 = st.columns(2)
        with cf1:
            with st.expander("💡 Neuen Spielplatz vorschlagen"):
                with st.form("v_form"):
                    v_n, v_a = st.text_input("Name"), st.text_input("Adresse")
                    if st.form_submit_button("Absenden"):
                        sende_vorschlag(v_n, v_a, "Alle", st.session_state.user)
                        st.success("Danke!")
        with cf2:
            with st.expander("💬 App Feedback"):
                with st.form("f_form"):
                    msg = st.text_area("Nachricht")
                    if st.form_submit_button("Senden"):
                        sende_feedback(st.session_state.user, msg)
                        st.success("Gespeichert!")
