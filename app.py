import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import os
from database_manager import hole_df, speichere_spielplatz, registriere_nutzer, hash_passwort

# --- SETUP & DESIGN ---
st.set_page_config(page_title="KletterKompass Deutschland", layout="wide")

# CSS für das dunkle Design mit grünen Akzenten
st.markdown("""
    <style>
    /* Hauptfarben */
    h1, h2, h3, label { color: #2e7d32 !important; font-family: 'Helvetica Neue', sans-serif; }
    
    /* Buttons */
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; border: none; font-weight: bold; width: 100%; }
    .stButton>button:hover { background-color: #1b5e20; color: white; }

    /* Eingabefelder: Weißer Hintergrund für maximale Lesbarkeit */
    .stTextInput>div>div>input, .stNumberInput>div>div>input { 
        background-color: #ffffff !important; 
        border: 2px solid #2e7d32 !important; 
        color: #000000 !important; 
    }
    
    /* SIDEBAR: Wieder Schwarz / Dunkelgrau */
    [data-testid="stSidebar"] { 
        background-color: #111111 !important; 
    }
    
    /* Text in der Sidebar auf Weiß setzen */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    /* Radio-Buttons in der Sidebar lesbar machen */
    [data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# --- SIDEBAR (DUNKEL) ---
with st.sidebar:
    logo_path = "assets/Kletterkompass_Logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    
    st.write("---")
    
    if not st.session_state.logged_in:
        auth_mode = st.radio("Bereich wählen:", ["Anmelden", "Registrieren"])
        
        if auth_mode == "Anmelden":
            st.subheader("🔐 Login")
            u = st.text_input("Nutzername")
            p = st.text_input("Passwort", type="password")
            if st.button("Einloggen"):
                df_n = hole_df("nutzer")
                if not df_n.empty:
                    user_match = df_n[(df_n['benutzername'] == u) & (df_n['passwort'] == hash_passwort(p))]
                    if not user_match.empty:
                        st.session_state.logged_in = True
                        st.session_state.user = u
                        st.rerun()
                    else: st.error("Daten falsch.")
        else:
            st.subheader("📝 Registrieren")
            nu = st.text_input("Nutzername*")
            npw = st.text_input("Passwort*", type="password")
            ne = st.text_input("E-Mail*")
            nv = st.text_input("Vorname")
            nn = st.text_input("Nachname")
            na = st.number_input("Alter", 0, 120, 25)
            if st.button("Konto erstellen"):
                if nu and npw and ne:
                    if registriere_nutzer(nu, npw, ne, nv, nn, na): 
                        st.success("Konto erstellt! Bitte anmelden.")
                    else: st.error("Fehler: Name oder E-Mail vergeben.")
                else: st.warning("Pflichtfelder (*) ausfüllen!")
    else:
        st.success(f"Moin {st.session_state.user}!")
        if st.button("🚪 Logout"): 
            st.session_state.logged_in = False
            st.rerun()

    st.write("---")
    if st.button("📍 Spielplatz suchen"): st.session_state.wahl = "📍 Suche"
    if st.button("📄 Rechtliches"): st.session_state.wahl = "📄 Rechtliches"

# --- HAUPTBEREICH ---
if st.session_state.wahl == "📍 Suche":
    banner_path = "assets/Kletterkompass.png"
    if os.path.exists(banner_path):
        st.image(banner_path, use_container_width=True)
    
    st.title("Spielplätze & Parks")
    
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Ort / Adresse", "Varel")
    with c2: km = st.slider("Radius (km)", 1, 100, 20)
    
    if st.button("🔍 Suchen", type="primary"):
        with st.status("Suche läuft...") as status:
            gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
            res = gc.geocode(adr + ", Deutschland")
            if res:
                slat, slon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
                df = hole_df("spielplaetze")
                if not df.empty:
                    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
                    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
                    df = df.dropna(subset=['lat', 'lon'])
                    df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                    final = df[df['distanz'] <= km].sort_values('distanz')
                    
                    if not final.empty:
                        status.update(label="Gefunden!", state="complete", expanded=False)
                        col_l, col_r = st.columns([1, 1.5])
                        with col_l:
                            for i, r in final.iterrows():
                                with st.expander(f"📍 {r['Standort']} ({round(r['distanz'], 1)} km)"):
                                    st.write(f"**Alter:** {r['altersfreigabe']}")
                        with col_r:
                            fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10, height=500)
                            fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0}, mapbox_center={"lat": slat, "lon": slon})
                            st.plotly_chart(fig, use_container_width=True)
                    else: st.warning("Keine Spots gefunden.")
                else: st.info("Datenbank ist noch leer.")
            else: st.error("Ort nicht gefunden.")

    if st.session_state.logged_in:
        st.write("---")
        with st.expander("🏗️ Admin: Neuen Spot hinzufügen"):
            with st.form("add"):
                n = st.text_input("Name")
                a = st.text_input("Adresse")
                alt = st.selectbox("Altersgruppe", ["0-3 Jahre", "3-12 Jahre", "Alle"])
                if st.form_submit_button("Speichern"):
                    gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                    r = gc.geocode(a + ", Deutschland")
                    if r and speichere_spielplatz(n, r[0]['geometry']['lat'], r[0]['geometry']['lng'], alt):
                        st.success("Gespeichert!"); st.rerun()

elif st.session_state.wahl == "📄 Rechtliches":
    st.title("Impressum & Datenschutz")
    st.write("Hier folgen deine rechtlichen Texte.")
