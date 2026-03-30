import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import requests
import os

from database_manager import hole_df, ausfuehren, image_optimieren, hash_passwort

# --- SETUP & DESIGN ---
st.set_page_config(page_title="KletterKompass Deutschland", layout="wide")

st.markdown("""
    <style>
    h1, h2, h3, .stSubheader, label { color: #2e7d32 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; border: none; }
    </style>
    """, unsafe_allow_html=True)

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# --- SIDEBAR ---
with st.sidebar:
    logo_path = "assets/Kletterkompass_Logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    else:
        st.title("🧗 Kletterkompass")
    
    st.write("---")
    if st.button("📍 Spielplatz suchen", use_container_width=True): st.session_state.wahl = "📍 Suche"
    if st.button("📄 Rechtliches", use_container_width=True): st.session_state.wahl = "📄 Rechtliches"

# --- HAUPTBEREICH ---
if st.session_state.wahl == "📍 Suche":
    banner_path = "assets/Kletterkompass.png"
    if os.path.exists(banner_path):
        st.image(banner_path, use_container_width=True)
    
    st.title("Spielplätze & Parks")
    
    c1, c2 = st.columns([3, 1])
    with c1:
        adr = st.text_input("Ort / Adresse", "Varel")
    with c2:
        km = st.slider("Radius (km)", 1, 100, 20)
    
    if st.button("🔍 Suchen", type="primary"):
        # Wir nutzen st.status, damit die Meldung nicht wegflasht
        with st.status("Suche läuft...", expanded=True) as status:
            try:
                # 1. Geocoder prüfen
                st.write("Prüfe Adresse...")
                geocoder = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                res_g = geocoder.geocode(adr + ", Deutschland")
                
                if not res_g:
                    st.error(f"❌ Adresse '{adr}' wurde nicht gefunden. Tippfehler?")
                    status.update(label="Suche abgebrochen", state="error")
                else:
                    slat, slon = res_g[0]['geometry']['lat'], res_g[0]['geometry']['lng']
                    st.write(f"Koordinaten gefunden: {slat}, {slon}")
                    
                    # 2. Daten laden
                    st.write("Lade Spielplätze aus Google Sheets...")
                    df = hole_df("SELECT * FROM spielplaetze")
                    
                    if df.empty:
                        st.warning("⚠️ Tabelle 'spielplaetze' ist leer oder nicht erreichbar.")
                        status.update(label="Keine Daten", state="error")
                    else:
                        st.write(f"{len(df)} Orte geladen. Berechne Distanz...")
                        
                        # Sicherstellen, dass lat/lon Zahlen sind
                        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
                        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
                        df = df.dropna(subset=['lat', 'lon'])
                        
                        df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                        final = df[df['distanz'] <= km].sort_values('distanz')
                        
                        if final.empty:
                            st.info(f"Keine Spots im Umkreis von {km} km gefunden.")
                            status.update(label="Keine Treffer", state="complete")
                        else:
                            status.update(label="Suche erfolgreich!", state="complete", expanded=False)
                            
                            # Ergebnisse anzeigen
                            cl, cr = st.columns(2)
                            with cl:
                                for i, r in final.iterrows():
                                    with st.expander(f"📍 {r['Standort']} ({round(r['distanz'], 1)} km)"):
                                        st.write(f"Infos zum Spot...")
                            with cr:
                                fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10)
                                fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                                st.plotly_chart(fig, use_container_width=True)
                                
            except Exception as e:
                st.error(f"💥 Kritischer Fehler: {e}")
                status.update(label="Fehler aufgetreten", state="error")

elif st.session_state.wahl == "📄 Rechtliches":
    st.title("Impressum & Datenschutz")
