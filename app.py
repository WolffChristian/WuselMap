import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import os
from database_manager import hole_df, speichere_spielplatz, registriere_nutzer, hash_passwort

# --- SETUP ---
st.set_page_config(page_title="KletterKompass", layout="wide")
st.markdown("""
    <style>
    h1, h2, h3, label { color: #2e7d32 !important; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; }
    .stTextInput>div>div>input { background-color: #f0f2f6 !important; border: 1px solid #2e7d32 !important; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

# --- SIDEBAR ---
with st.sidebar:
    st.title("🧗 KletterKompass")
    st.write("---")
    
    if not st.session_state.logged_in:
        mode = st.radio("Aktion:", ["Anmelden", "Registrieren"])
        
        if mode == "Anmelden":
            u = st.text_input("Nutzername")
            p = st.text_input("Passwort", type="password")
            if st.button("Login"):
                df_n = hole_df("nutzer")
                if not df_n.empty and not df_n[(df_n['benutzername'] == u) & (df_n['passwort'] == hash_passwort(p))].empty:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Fehler!")
        else:
            nu = st.text_input("Nutzername*")
            npw = st.text_input("Passwort*", type="password")
            ne = st.text_input("E-Mail*")
            nv = st.text_input("Vorname")
            nn = st.text_input("Nachname")
            na = st.number_input("Alter", 0, 100, 25)
            if st.button("Konto erstellen"):
                if nu and npw and ne:
                    if registriere_nutzer(nu, npw, ne, nv, nn, na): st.success("Erfolg! Bitte einloggen.")
                    else: st.error("Fehler (Name/E-Mail vergeben?)")
                else: st.warning("Pflichtfelder ausfüllen!")
    else:
        st.success(f"Moin {st.session_state.user}!")
        if st.button("Logout"): 
            st.session_state.logged_in = False
            st.rerun()

    st.write("---")
    if st.button("📍 Suche"): st.session_state.wahl = "📍 Suche"
    if st.button("📄 Recht"): st.session_state.wahl = "📄 Recht"

# --- HAUPTBEREICH ---
if st.session_state.wahl == "📍 Suche":
    st.title("Spielplatz-Finder")
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Wo?", "Varel")
    with c2: km = st.slider("Radius", 1, 100, 20)
    
    if st.button("Suchen"):
        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        res = gc.geocode(adr + ", Deutschland")
        if res:
            slat, slon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
            df = hole_df("spielplaetze")
            if not df.empty:
                df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                final = df[df['distanz'] <= km].sort_values('distanz')
                
                cl, cr = st.columns([1, 2])
                with cl:
                    for i, r in final.iterrows():
                        with st.expander(f"{r['Standort']}"): st.write(f"Distanz: {round(r['distanz'], 1)} km")
                with cr:
                    fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10, height=500)
                    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig, use_container_width=True)
        else: st.error("Ort nicht gefunden.")

    if st.session_state.logged_in:
        with st.expander("🏗️ Admin: Spot hinzufügen"):
            with st.form("add"):
                n = st.text_input("Name")
                a = st.text_input("Adresse")
                if st.form_submit_button("Speichern"):
                    gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                    r = gc.geocode(a + ", Deutschland")
                    if r and speichere_spielplatz(n, r[0]['geometry']['lat'], r[0]['geometry']['lng'], "Alle"):
                        st.success("Gespeichert!"); st.rerun()

elif st.session_state.wahl == "📄 Recht":
    st.write("Impressum & Datenschutz")
