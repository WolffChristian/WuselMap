import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import os
from database_manager import hole_df, speichere_spielplatz, registriere_nutzer, hash_passwort

# --- SETUP & DESIGN ---
st.set_page_config(page_title="KletterKompass Deutschland", layout="wide")

st.markdown("""
    <style>
    /* Haupt-Design */
    h1, h2, h3, label { color: #2e7d32 !important; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    
    /* Eingabefelder Sichtbarkeit */
    .stTextInput>div>div>input, .stNumberInput>div>div>input { 
        background-color: #ffffff !important; color: #000000 !important; border: 2px solid #2e7d32 !important; 
    }
    
    /* Schwarze Sidebar */
    [data-testid="stSidebar"] { background-color: #000000 !important; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label { color: #ffffff !important; }
    
    /* Tabs Design (Anmelden/Registrieren) */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #1a1a1a; border-radius: 5px; color: white; padding: 10px 20px; 
    }
    .stTabs [aria-selected="true"] { background-color: #2e7d32 !important; }
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
    if os.path.exists(logo_path): st.image(logo_path, width=180)
    
    st.write("---")
    
    if not st.session_state.logged_in:
        # TABS statt Radio-Buttons für "Anmelden" / "Registrieren"
        tab_login, tab_reg = st.tabs(["🔐 Anmelden", "📝 Registrieren"])
        
        with tab_login:
            u = st.text_input("Nutzername", key="l_u")
            p = st.text_input("Passwort", type="password", key="l_p")
            if st.button("Einloggen"):
                df_n = hole_df("nutzer")
                if not df_n.empty and not df_n[(df_n['benutzername'] == u) & (df_n['passwort'] == hash_passwort(p))].empty:
                    st.session_state.logged_in = True; st.session_state.user = u; st.rerun()
                else: st.error("Login falsch.")
        
        with tab_reg:
            nu = st.text_input("Nutzername*", key="r_u")
            npw = st.text_input("Passwort*", type="password", key="r_p")
            ne = st.text_input("E-Mail*", key="r_e")
            nv = st.text_input("Vorname")
            nn = st.text_input("Nachname")
            na = st.number_input("Alter", 0, 100, 25)
            agb = st.checkbox("Ich akzeptiere die AGB & Datenschutz*")
            
            if st.button("Konto erstellen"):
                if nu and npw and ne and agb:
                    if registriere_nutzer(nu, npw, ne, nv, nn, na, agb): st.success("Erfolg! Bitte einloggen.")
                    else: st.error("Name/E-Mail vergeben.")
                else: st.warning("Pflichtfelder + AGB prüfen!")
    else:
        st.success(f"Moin {st.session_state.user}!")
        if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()

    st.write("---")
    if st.button("📍 Suche"): st.session_state.wahl = "📍 Suche"
    if st.button("📄 Recht"): st.session_state.wahl = "📄 Recht"

# --- HAUPTBEREICH: SUCHE ---
if st.session_state.wahl == "📍 Suche":
    banner_path = "assets/Kletterkompass.png"
    if os.path.exists(banner_path): st.image(banner_path, use_container_width=True)
    
    st.title("Spielplätze & Parks")
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Ort / Adresse", "Varel")
    with c2: km = st.slider("Radius (km)", 1, 100, 20)
    
    if st.button("🔍 Suchen", type="primary"):
        # KEIN Status-Fenster, direkt laden
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
                    col_l, col_r = st.columns([1, 1.5])
                    with col_l:
                        st.subheader(f"{len(final)} Treffer")
                        for i, r in final.iterrows():
                            with st.expander(f"📍 {r['Standort']} ({round(r['distanz'], 1)} km)"):
                                st.write(f"**Alter:** {r['altersfreigabe']}")
                    with col_r:
                        fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10, height=600)
                        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0}, mapbox_center={"lat": slat, "lon": slon})
                        st.plotly_chart(fig, use_container_width=True)
                else: st.warning("Keine Spots gefunden.")
        else: st.error("Ort nicht gefunden.")

    # Admin Bereich
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
