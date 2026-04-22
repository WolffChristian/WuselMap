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
    
    # 1. RECHTLICHER HINWEIS (Wichtig für dich als Betreiber)
    st.info("⚠️ **Sicherheitshinweis:** Kinder müssen auf den Spielplätzen immer von Erwachsenen beaufsichtigt werden. Nutzung auf eigene Gefahr.")
    
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
                    final['KartenStatus'] = final['status'].apply(lambda x: "✅ Spielbereit" if x == 'aktiv' else "⚠️ Wartung/Defekt")

                    col_l, col_r = st.columns([1, 1.5])
                    with col_l:
                        for i, r in final.iterrows():
                            spot_weather = get_weather(r['lat'], r['lon'])
                            titel = f"📍 {r['Standort']}"
                            
                            with st.expander(f"{titel} ({round(r['distanz'], 1)} km)"):
                                st.markdown(f"**Wetter vor Ort:** {spot_weather}")
                                
                                # --- FOTO ANZEIGE ---
                                if r.get('bild_data'): 
                                    st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
                                else:
                                    st.warning("📸 Foto fehlt noch!")

                                # --- DETAILS ---
                                st.write(f"**Alter:** {r['altersfreigabe']} | **Ort:** {r['stadt']}")
                                st.write(f"**Geräte:** {r.get('ausstattung', 'Keine Angabe')}")
                                
                                # --- EXTRAS (Inkl. Parkplatz) ---
                                extras = []
                                if r.get('hat_schatten') == 1: extras.append("🌳 Schatten")
                                if r.get('hat_sitze') == 1: extras.append("🪑 Sitzplätze")
                                if r.get('hat_wc') == 1: extras.append("🚽 Toilette")
                                if r.get('hat_parkplatz') == 1: extras.append("🚗 Parkplatz")
                                
                                if extras: 
                                    st.success(" | ".join(extras))
                                
                                st.divider()
                                
                                # --- NEU: DIREKT-UPDATE FÜR USER ---
                                with st.expander("✏️ Infos ergänzen oder Foto senden"):
                                    tab_foto, tab_info = st.tabs(["📷 Foto", "📝 Details"])
                                    
                                    with tab_foto:
                                        with st.form(f"up_foto_{i}", clear_on_submit=True):
                                            n_img = st.file_uploader("Bild auswählen", type=["jpg","png","jpeg"], key=f"f_up_{i}")
                                            if st.form_submit_button("Foto einreichen"):
                                                if n_img:
                                                    b_data = optimiere_bild(n_img)
                                                    sende_vorschlag(r['Standort'], r.get('adresse',''), r['altersfreigabe'], 
                                                                  st.session_state.user, "Niedersachsen", r.get('plz','00000'), r['stadt'], 
                                                                  b_data, 1, "Foto-Update", r.get('hat_schatten',0), 
                                                                  r.get('hat_sitze',0), r.get('hat_wc',0), r['lat'], r['lon'], r.get('hat_parkplatz',0))
                                                    st.info("Danke! Das Foto wird geprüft.")

                                    with tab_info:
                                        with st.form(f"quick_edit_{i}", clear_on_submit=True):
                                            st.write("Was gibt es hier wirklich?")
                                            q_schatten = st.checkbox("🌳 Schatten vorhanden", value=bool(r.get('hat_schatten')))
                                            q_sitze = st.checkbox("🪑 Sitzmöglichkeiten vorhanden", value=bool(r.get('hat_sitze')))
                                            q_parken = st.checkbox("🚗 Parkplätze vorhanden", value=bool(r.get('hat_parkplatz')))
                                            q_text = st.text_area("Weitere Infos", placeholder="z.B. Neue Doppelschaukel aufgebaut!")
                                            
                                            if st.form_submit_button("Infos absenden"):
                                                if sende_vorschlag(
                                                    r['Standort'], r.get('adresse', ''), r['altersfreigabe'], 
                                                    st.session_state.user, "Niedersachsen", r.get('plz', '00000'), r['stadt'], 
                                                    None, 1, q_text, 1 if q_schatten else 0, 1 if q_sitze else 0, 
                                                    r.get('hat_wc', 0), r['lat'], r['lon'], 1 if q_parken else 0
                                                ):
                                                    st.success("Danke! Wir prüfen deine Ergänzungen.")

                                st.feedback("stars", key=f"rate_{r.get('id', i)}")

                    with col_r:
                        fig = px.scatter_mapbox(
                            final, 
                            lat="lat", 
                            lon="lon", 
                            hover_name="Standort",
                            color="KartenStatus",
                            color_discrete_map={
                                "✅ Spielbereit": "#FF8C00", 
                                "⚠️ Wartung/Defekt": "#CC0000"
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
                        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
                else:
                    st.warning("Keine Spielplätze im Umkreis gefunden.")
        else:
            st.error("Ort konnte nicht gefunden werden. Bitte prüfe die Schreibweise.")