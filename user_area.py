import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import os
from database_manager import hole_df, sende_vorschlag, sende_feedback, optimiere_bild, check_duplikat, aktualisiere_profil

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

# --- 1. DIE SUCHE ---
def show_user_area():
    st.title("📍 Spielplätze finden")
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
                                if r.get('bild_data'): st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
                                st.write(f"**Ort:** {r['stadt']} ({r['plz']})")
                    with col_r:
                        fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10, height=500)
                        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0}, mapbox_center={"lat": slat, "lon": slon})
                        st.plotly_chart(fig, use_container_width=True)

# --- 2. DER VORSCHLAG ---
def show_proposal_area():
    st.title("💡 Neuen Spielplatz vorschlagen")
    st.info("Füll die Daten aus. Wir prüfen den Spot und schalten ihn dann für alle frei!")
    
    with st.form("vorschlags_form"):
        v_n = st.text_input("Name des Spielplatzes*")
        v_a = st.text_input("Straße & Hausnummer")
        v_p = st.text_input("Postleitzahl*")
        v_s = st.text_input("Stadt*")
        v_b = st.selectbox("Bundesland", ["Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen", "Mecklenburg-Vorpommern", "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland", "Sachsen", "Sachsen-Anhalt", "Schleswig-Holstein", "Thüringen"])
        v_alt = st.selectbox("Altersgruppe", ["0-3 Jahre", "3-12 Jahre", "Alle"])
        v_img = st.file_uploader("Bild hochladen", type=["jpg", "png", "jpeg"])
        
        if st.form_submit_button("Vorschlag jetzt einsenden"):
            if v_n and v_p and v_s:
                # Duplikat-Check
                if check_duplikat("spielplaetze", v_n, v_p) or check_duplikat("vorschlaege", v_n, v_p):
                    st.warning("⚠️ Dieser Spot existiert bereits in unserer Datenbank!")
                else:
                    bild_data = optimiere_bild(v_img)
                    sende_vorschlag(v_n, v_a, v_alt, st.session_state.user, v_b, v_p, v_s, bild_data)
                    st.success("✅ Danke! Dein Vorschlag ist bei uns eingegangen.")
            else:
                st.warning("Bitte fülle die Pflichtfelder (*) aus.")

# --- 3. DAS PROFIL ---
def show_profile_area():
    st.title("👤 Mein Profil")
    df_u = hole_df("nutzer")
    user_data = df_u[df_u['benutzername'] == st.session_state.user].iloc[0]
    
    with st.form("profil_edit"):
        nv = st.text_input("Vorname", value=user_data['vorname'])
        nn = st.text_input("Nachname", value=user_data['nachname'])
        ne = st.text_input("E-Mail", value=user_data['email'])
        na = st.number_input("Alter", value=int(user_data['alter_jahre']))
        emo = st.selectbox("Dein Emoji-Avatar", ["🧗", "🤸", "🦁", "🚀", "🌟"], index=0)
        
        if st.form_submit_button("Änderungen speichern"):
            if aktualisiere_profil(st.session_state.user, ne, nv, nn, na, emo):
                st.success("Profil aktualisiert!"); st.rerun()
