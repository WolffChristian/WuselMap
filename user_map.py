import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
from database_manager import hole_df, optimiere_bild, sende_vorschlag, get_db_connection
import numpy as np
import requests

# --- HILFSFUNKTIONEN ---

def get_weather(lat, lon):
    """Holt aktuelle Wetterdaten für exakte Koordinaten"""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url).json()
        temp = response['current_weather']['temperature']
        code = response['current_weather']['weathercode']
        # Wetter-Emoji Logik
        emoji = "☀️" if code == 0 else "☁️" if code < 50 else "🌧️"
        return f"{emoji} {temp}°C"
    except:
        return "❓ Wetter unbekannt"

def distanz(lat1, lon1, lat2, lon2):
    """Berechnet die Entfernung zwischen zwei Koordinaten in km"""
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

# --- HAUPTFUNKTION ---

def show_map_section():
    """Die Such- und Kartenansicht für Spielplätze"""
    st.subheader("📍 Spielplätze suchen")
    
    with st.expander("🔍 Suche & Filter", expanded=True):
        c1, c2 = st.columns([3, 1])
        with c1: 
            adr = st.text_input("Wo suchst du?", "Varel", key="search_adr")
        with c2: 
            km = st.slider("Umkreis (km)", 1, 100, 20, key="search_km")
        
        alter_filter = st.multiselect(
            "Altersgruppe", 
            options=["0-3", "3-6", "6-12", "3-12", "Alle"], 
            default=["0-3", "3-6", "6-12", "3-12", "Alle"],
            key="search_age"
        )
    
    df = hole_df("spielplaetze")
    
    if st.button("🔍 Suchen", type="primary", use_container_width=True):
        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        res = gc.geocode(adr + ", Deutschland")
        
        if res:
            slat, slon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
            
            if not df.empty:
                # Daten vorbereiten
                df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
                df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
                df = df.dropna(subset=['lat', 'lon'])
                
                # Distanz berechnen
                df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                
                # Filtern
                final = df[df['distanz'] <= km]
                final = final[final['altersfreigabe'].isin(alter_filter)].sort_values('distanz')

                if not final.empty:
                    # Status für die Karte lesbar machen
                    final['KartenStatus'] = final['status'].apply(lambda x: "✅ Spielbereit" if x == 'aktiv' else "⚠️ Wartung/Defekt")

                    col_l, col_r = st.columns([1, 1.5])
                    with col_l:
                        for i, r in final.iterrows():
                            # Wetter für diesen speziellen Spot abrufen
                            spot_weather = get_weather(r['lat'], r['lon'])
                            
                            titel = f"📍 {r['Standort']}"
                            with st.expander(f"{titel} ({round(r['distanz'], 1)} km)"):
                                
                                # Wetter direkt oben im Expander
                                st.markdown(f"**Aktuelles Wetter vor Ort:** {spot_weather}")
                                
                                # Foto
                                if r.get('bild_data'): 
                                    st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
                                else:
                                    st.warning("📸 Foto fehlt!")
                                    with st.form(f"up_foto_{i}", clear_on_submit=True):
                                        n_img = st.file_uploader("Foto beisteuern", type=["jpg","png","jpeg"], key=f"f_up_{i}")
                                        if st.form_submit_button("An Admin senden"):
                                            if n_img:
                                                b_data = optimiere_bild(n_img)
                                                sende_vorschlag(r['Standort'], "FOTO-UPDATE", r['altersfreigabe'], 
                                                                st.session_state.user, "Niedersachsen", "00000", r['stadt'], 
                                                                b_data, 1, status="foto_neu")
                                                st.info("Danke! Foto wird geprüft.")

                                # Details
                                st.write(f"**Alter:** {r['altersfreigabe']} | **Ort:** {r['stadt']}")
                                st.write(f"**Vorhandene Geräte:** {r.get('ausstattung', 'Keine Angabe')}")
                                
                                # Extras (Häkchen aus der DB)
                                extras = []
                                if r.get('hat_schatten') == 1: extras.append("🌳 Schatten")
                                if r.get('hat_sitze') == 1: extras.append("🪑 Sitzplätze")
                                if r.get('hat_wc') == 1: extras.append("🚽 Toilette")
                                
                                if extras:
                                    st.success(" | ".join(extras))
                                
                                st.divider()
                                st.feedback("stars", key=f"rate_{r.get('id', i)}")

                    with col_r:
                        # Karte mit neuen Farben (Orange & Rot)
                        fig = px.scatter_mapbox(
                            final, 
                            lat="lat", 
                            lon="lon", 
                            hover_name="Standort",
                            color="KartenStatus",
                            color_discrete_map={
                                "✅ Spielbereit": "#FF8C00", # Kräftiges Orange
                                "⚠️ Wartung/Defekt": "#CC0000"  # Dunkelrot
                            },
                            zoom=11, 
                            height=600, 
                            mapbox_style="open-street-map"
                        )
                        fig.update_layout(
                            margin={"r":0,"t":0,"l":0,"b":0}, 
                            mapbox_center={"lat": slat, "lon": slon},
                            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Keine Spielplätze in diesem Bereich gefunden.")
        else:
            st.error("Konnte den Ort nicht finden.")