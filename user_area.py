import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import os
from database_manager import (
    hole_df, sende_vorschlag, sende_feedback, 
    optimiere_bild, check_duplikat, aktualisiere_profil
)

# Hilfsfunktion für die Entfernung
def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

# --- 1. SUCH-BEREICH ---
def show_user_area():
    st.title("📍 Spielplätze finden")
    
    banner_path = "assets/Kletterkompass.png"
    if os.path.exists(banner_path):
        st.image(banner_path, use_container_width=True)
    
    c1, c2 = st.columns([3, 1])
    with c1:
        adr = st.text_input("Wo suchst du? (Ort / Adresse)", "Varel")
    with c2:
        km = st.slider("Umkreis (km)", 1, 100, 20)
    
    if st.button("🔍 Jetzt Suchen", type="primary"):
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
                                if r.get('bild_data'):
                                    st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
                                st.write(f"**Ort:** {r.get('stadt', 'Unbekannt')} ({r.get('plz', '-')})")
                                st.write(f"**Alter:** {r.get('altersfreigabe', 'Alle')}")
                    with col_r:
                        fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10, height=600)
                        fig.update_layout(
                            mapbox_style="open-street-map", 
                            margin={"r":0,"t":0,"l":0,"b":0},
                            mapbox_center={"lat": slat, "lon": slon}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Keine Spielplätze in diesem Radius gefunden.")
        else:
            st.error("Ort konnte nicht gefunden werden.")

# --- 2. VORSCHLAGS-BEREICH ---
def show_proposal_area():
    st.title("💡 Neuen Spielplatz vorschlagen")
    st.write("Hilf uns, die Karte zu füllen! Pflichtfelder sind mit * markiert.")
    
    with st.form("vorschlags_form"):
        v_n = st.text_input("Name des Spielplatzes*")
        
        col_adr1, col_adr2 = st.columns([3, 1])
        with col_adr1:
            v_str = st.text_input("Straße*")
        with col_adr2:
            v_nr = st.text_input("Hausnr.")
            
        col_adr3, col_adr4 = st.columns([1, 2])
        with col_adr3:
            v_p = st.text_input("PLZ*")
        with col_adr4:
            v_s = st.text_input("Stadt*")
            
        v_b = st.selectbox("Bundesland", [
            "Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", 
            "Hamburg", "Hessen", "Mecklenburg-Vorpommern", "Niedersachsen", 
            "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland", "Sachsen", 
            "Sachsen-Anhalt", "Schleswig-Holstein", "Thüringen"
        ], index=8) # Niedersachsen Default
        
        v_alt = st.selectbox("Altersgruppe", ["0-3 Jahre", "3-12 Jahre", "Alle"])
        v_img = st.file_uploader("Bild hochladen (optional)", type=["jpg", "png", "jpeg"])
        
        st.write("---")
        ds_check = st.checkbox("Datenschutz: Ich bestätige, dass auf dem Foto keine Personen (insb. Kinder) erkennbar sind.*")
        
        if st.form_submit_button("Vorschlag absenden"):
            if v_n and v_str and v_p and v_s and ds_check:
                # Prüfen auf Duplikate
                if check_duplikat("spielplaetze", v_n, v_p) or check_duplikat("vorschlaege", v_n, v_p):
                    st.warning("⚠️ Dieser Spielplatz wurde bereits eingetragen!")
                else:
                    bild_data = optimiere_bild(v_img)
                    adr_komplett = f"{v_str} {v_nr}".strip()
                    sende_vorschlag(v_n, adr_komplett, v_alt, st.session_state.user, v_b, v_p, v_s, bild_data, ds_check)
                    st.success("✅ Danke! Dein Vorschlag wird vom Admin geprüft.")
            else:
                st.error("Bitte alle Pflichtfelder (*) ausfüllen und den Datenschutz bestätigen.")

# --- 3. PROFIL-BEREICH ---
def show_profile_area():
    st.title("👤 Mein Profil")
    df_u = hole_df("nutzer")
    user_data = df_u[df_u['benutzername'] == st.session_state.user].iloc[0]
    
    with st.form("profil_edit"):
        st.subheader("Daten anpassen")
        nv = st.text_input("Vorname", value=user_data.get('vorname', ''))
        nn = st.text_input("Nachname", value=user_data.get('nachname', ''))
        ne = st.text_input("E-Mail", value=user_data.get('email', ''))
        na = st.number_input("Alter", value=int(user_data.get('alter_jahre', 25)))
        emo = st.selectbox("Dein Emoji", ["🧗", "🤸", "🦁", "🚀", "🌟", "🧗‍♂️"], index=0)
        
        if st.form_submit_button("Speichern"):
            if aktualisiere_profil(st.session_state.user, ne, nv, nn, na, emo):
                st.success("Profil erfolgreich aktualisiert!")
                st.rerun()

# --- 4. FEEDBACK-BEREICH ---
def show_feedback_area():
    st.title("💬 Feedback & Hilfe")
    st.write("Probleme mit der App? Ideen für neue Funktionen? Schreib mir!")
    
    with st.form("feedback_form"):
        msg = st.text_area("Deine Nachricht", height=150)
        if st.form_submit_button("Abschicken"):
            if msg.strip():
                if sende_feedback(st.session_state.user, msg):
                    st.success("✅ Nachricht gesendet. Carlos schaut es sich an!")
                else:
                    st.error("Fehler beim Senden.")
            else:
                st.warning("Bitte gib eine Nachricht ein.")
