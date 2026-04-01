import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import os

# Wir importieren die Funktionen aus deinem neuen database_manager
from database_manager import hole_df, speichere_spielplatz, image_optimieren, hash_passwort

# --- 1. SETUP & DESIGN ---
st.set_page_config(page_title="KletterKompass Deutschland", layout="wide", page_icon="📍")

# Dein Kletterkompass-Grün und Styling
st.markdown("""
    <style>
    h1, h2, h3, .stSubheader, label { color: #2e7d32 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; border: none; width: 100%; }
    .stButton>button:hover { background-color: #1b5e20; color: white; }
    /* Karte schöner abrunden */
    .stPlotlyChart { border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# Mathematische Funktion für die Umkreissuche
def distanz(lat1, lon1, lat2, lon2):
    R = 6371 # Erd-Radius in km
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

# Session State initialisieren
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# --- 2. SIDEBAR (Login & Navigation) ---
with st.sidebar:
    # Logo laden
    logo_path = "assets/Kletterkompass_Logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    
    st.write("---")
    
    # LOGIN-BEREICH
    if not st.session_state.logged_in:
        st.subheader("🔐 Admin-Bereich")
        u = st.text_input("Nutzername", key="side_u")
        p = st.text_input("Passwort", type="password", key="side_p")
        if st.button("Einloggen"):
            # Wir holen die Nutzerdaten aus der MySQL-Tabelle
            df_n = hole_df("nutzer")
            if not df_n.empty:
                # Suche nach passendem User und gehashtem Passwort
                user_match = df_n[(df_n['benutzername'] == u) & (df_n['passwort'] == hash_passwort(p))]
                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Daten nicht korrekt.")
            else:
                st.error("Datenbank leer oder nicht erreichbar.")
    else:
        st.success(f"Moin, {st.session_state.user}!")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.write("---")
    if st.button("📍 Spielplatz suchen"): st.session_state.wahl = "📍 Suche"
    if st.button("📄 Rechtliches"): st.session_state.wahl = "📄 Rechtliches"

# --- 3. HAUPTBEREICH: SUCHE ---
if st.session_state.wahl == "📍 Suche":
    banner_path = "assets/Kletterkompass.png"
    if os.path.exists(banner_path):
        st.image(banner_path, use_container_width=True)
    
    st.title("Spielplätze & Parks finden")
    
    # Suchfelder
    c1, c2 = st.columns([3, 1])
    with c1:
        adr = st.text_input("Wo suchst du?", "Varel")
    with c2:
        km = st.slider("Radius (km)", 1, 100, 20)
    
    if st.button("🔍 Jetzt suchen", type="primary"):
        with st.status("Verbinde mit TiDB Cloud Datenbank...", expanded=True) as status:
            try:
                # 1. Adresse in Koordinaten umwandeln (OpenCage)
                geocoder = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                res_g = geocoder.geocode(adr + ", Deutschland")
                
                if not res_g:
                    st.error(f"Ort '{adr}' nicht gefunden.")
                    status.update(label="Fehler", state="error")
                else:
                    slat, slon = res_g[0]['geometry']['lat'], res_g[0]['geometry']['lng']
                    
                    # 2. Daten aus MySQL laden
                    df = hole_df("spielplaetze")
                    
                    if not df.empty:
                        # Daten-Typen sicherstellen
                        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
                        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
                        df = df.dropna(subset=['lat', 'lon'])
                        
                        # 3. Distanz berechnen
                        df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                        final = df[df['distanz'] <= km].sort_values('distanz')
                        
                        if final.empty:
                            st.warning(f"Keine Spots im Umkreis von {km} km gefunden.")
                            status.update(label="Suche beendet", state="complete")
                        else:
                            status.update(label="Spots gefunden!", state="complete", expanded=False)
                            
                            col_l, col_r = st.columns([1, 1.5])
                            with col_l:
                                st.subheader(f"Ergebnisse ({len(final)})")
                                for i, r in final.iterrows():
                                    with st.expander(f"📍 {r['Standort']} ({round(r['distanz'], 1)} km)"):
                                        st.write(f"**Altersgruppe:** {r['altersfreigabe']}")
                                        st.info("Klettergerüste, Schaukeln und viel Platz!")
                            
                            with col_r:
                                # Plotly Mapbox Karte
                                fig = px.scatter_mapbox(final, 
                                                        lat="lat", 
                                                        lon="lon", 
                                                        hover_name="Standort", 
                                                        hover_data=["altersfreigabe"],
                                                        zoom=10, 
                                                        height=500)
                                fig.update_layout(
                                    mapbox_style="open-street-map", 
                                    margin={"r":0,"t":0,"l":0,"b":0},
                                    mapbox_center={"lat": slat, "lon": slon}
                                )
                                st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Die Datenbank ist aktuell noch leer. Füge als Admin den ersten Spot hinzu!")
                        status.update(label="Datenbank leer", state="complete")
            
            except Exception as e:
                st.error(f"Fehler: {e}")
                status.update(label="Abbruch", state="error")

    # --- ZUSATZ: NEUEN SPOT MELDEN (Nur wenn eingeloggt) ---
    if st.session_state.logged_in:
        st.write("---")
        with st.expander("🏗️ Admin: Neuen Spielplatz direkt hinzufügen"):
            with st.form("admin_form"):
                n_name = st.text_input("Name des Spielplatzes")
                n_adr = st.text_input("Genaue Adresse (für Geocoder)")
                n_alter = st.selectbox("Alter", ["0-3 Jahre", "3-12 Jahre", "Alle"])
                
                if st.form_submit_button("In MySQL speichern"):
                    if n_name and n_adr:
                        geocoder = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                        res = geocoder.geocode(n_adr + ", Deutschland")
                        if res:
                            n_lat, n_lon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
                            # Hier rufen wir die neue Speicher-Funktion auf
                            if speichere_spielplatz(n_name, n_lat, n_lon, n_alter):
                                st.success(f"Erfolg! {n_name} ist jetzt in der TiDB Cloud gespeichert.")
                                st.rerun()
                        else:
                            st.error("Adresse nicht gefunden.")
                    else:
                        st.warning("Bitte alle Felder ausfüllen.")

# --- 4. HAUPTBEREICH: RECHTLICHES ---
elif st.session_state.wahl == "📄 Rechtliches":
    st.title("Impressum & Datenschutz")
    st.info("KletterKompass Deutschland - Ein Projekt zur Förderung von Bewegung.")
    st.write("""
    **Verantwortlich:** [Dein Name]  
    **Kontakt:** [Deine E-Mail]  
    
    Datenschutzerklärung: Wir speichern keine personenbezogenen Daten unserer Besucher. 
    Eingetragene Standorte dienen der öffentlichen Information.
    """)
