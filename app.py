import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import os

# Import der Funktionen aus dem database_manager
from database_manager import hole_df, speichere_spielplatz, registriere_nutzer, hash_passwort

# --- 1. SETUP & DESIGN ---
st.set_page_config(page_title="KletterKompass Deutschland", layout="wide", page_icon="📍")

# Design-Fix für bessere Sichtbarkeit der Eingabefelder
st.markdown("""
    <style>
    /* Hauptfarben */
    h1, h2, h3, .stSubheader, label { color: #4caf50 !important; font-family: 'Helvetica Neue', sans-serif; }
    
    /* Buttons */
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; width: 100%; border: none; }
    .stButton>button:hover { background-color: #4caf50; }

    /* Eingabefelder Sichtbarkeit verbessern */
    .stTextInput>div>div>input {
        background-color: #f0f2f6 !important;
        color: #262730 !important;
        border: 2px solid #2e7d32 !important;
        border-radius: 5px;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #1a1c23; }
    [data-testid="stSidebar"] .stMarkdown { color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# --- 2. SIDEBAR (Login, Registrierung & Navigation) ---
with st.sidebar:
    logo_path = "assets/Kletterkompass_Logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    
    st.write("---")
    
    if not st.session_state.logged_in:
        # Umschalter zwischen Login und Registrierung
        auth_mode = st.radio("Bereich wählen:", ["Anmelden", "Neu Registrieren"], label_visibility="collapsed")
        
        if auth_mode == "Anmelden":
            st.subheader("🔐 Login")
            u = st.text_input("Nutzername", placeholder="Dein Name")
            p = st.text_input("Passwort", type="password", placeholder="Dein Passwort")
            if st.button("Einloggen"):
                df_n = hole_df("nutzer")
                if not df_n.empty:
                    user_match = df_n[(df_n['benutzername'] == u) & (df_n['passwort'] == hash_passwort(p))]
                    if not user_match.empty:
                        st.session_state.logged_in = True
                        st.session_state.user = u
                        st.rerun()
                    else:
                        st.error("Daten falsch.")
        
        else:
            st.subheader("📝 Registrierung")
            new_u = st.text_input("Wunsch-Nutzername", placeholder="z.B. KletterMax")
            new_p = st.text_input("Wunsch-Passwort", type="password", placeholder="Mind. 6 Zeichen")
            if st.button("Konto erstellen"):
                if len(new_u) > 2 and len(new_p) > 5:
                    if registriere_nutzer(new_u, new_p):
                        st.success("Konto erstellt! Du kannst dich jetzt einloggen.")
                    else:
                        st.error("Name schon vergeben oder Fehler.")
                else:
                    st.warning("Eingaben zu kurz.")
    else:
        st.success(f"Eingeloggt als: {st.session_state.user}")
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
    
    st.title("Spielplätze & Parks")
    
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Wo suchst du?", "Varel", placeholder="Ort oder Adresse eingeben")
    with c2: km = st.slider("Radius (km)", 1, 100, 20)
    
    if st.button("🔍 Suche starten", type="primary"):
        with st.status("Daten werden geladen...") as status:
            try:
                geocoder = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                res_g = geocoder.geocode(adr + ", Deutschland")
                
                if res_g:
                    slat, slon = res_g[0]['geometry']['lat'], res_g[0]['geometry']['lng']
                    df = hole_df("spielplaetze")
                    
                    if not df.empty:
                        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
                        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
                        df = df.dropna(subset=['lat', 'lon'])
                        df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                        final = df[df['distanz'] <= km].sort_values('distanz')
                        
                        if not final.empty:
                            status.update(label="Fertig!", state="complete", expanded=False)
                            col_l, col_r = st.columns([1, 1.5])
                            with col_l:
                                st.subheader("Ergebnisse")
                                for i, r in final.iterrows():
                                    with st.expander(f"📍 {r['Standort']} ({round(r['distanz'], 1)} km)"):
                                        st.write(f"**Alter:** {r['altersfreigabe']}")
                            with col_r:
                                fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10, height=500)
                                fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0}, mapbox_center={"lat": slat, "lon": slon})
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Nichts gefunden.")
                else:
                    st.error("Ort unbekannt.")
            except Exception as e:
                st.error(f"Fehler: {e}")

    # --- ADMIN FUNKTION ---
    if st.session_state.logged_in:
        st.write("---")
        with st.expander("🏗️ Admin: Neuen Spot eintragen"):
            with st.form("add_form"):
                n_name = st.text_input("Name")
                n_adr = st.text_input("Adresse")
                n_alt = st.selectbox("Alter", ["0-3", "3-12", "Alle"])
                if st.form_submit_button("Speichern"):
                    geocoder = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                    res = geocoder.geocode(n_adr + ", Deutschland")
                    if res:
                        if speichere_spielplatz(n_name, res[0]['geometry']['lat'], res[0]['geometry']['lng'], n_alt):
                            st.success("Gespeichert!")
                            st.rerun()

elif st.session_state.wahl == "📄 Rechtliches":
    st.title("Rechtliches")
    st.write("Impressum und Datenschutz folgen hier.")
