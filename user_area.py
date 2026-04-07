import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
from database_manager import hole_df, sende_vorschlag, sende_feedback, optimiere_bild, check_duplikat, aktualisiere_profil

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

def show_user_area():
    st.title("📍 Kletter-Spots finden")
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Wo suchst du?", "Varel")
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

def show_proposal_area():
    st.title("💡 Neuen Spot vorschlagen")
    with st.form("vorschlags_form"):
        v_n = st.text_input("Name des Spots*")
        v_str = st.text_input("Straße*")
        v_p = st.text_input("PLZ*")
        v_s = st.text_input("Stadt*")
        v_b = st.selectbox("Bundesland", ["Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen", "Mecklenburg-Vorpommern", "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland", "Sachsen", "Sachsen-Anhalt", "Schleswig-Holstein", "Thüringen"], index=8)
        v_alt = st.selectbox("Altersgruppe", ["0-3 Jahre", "3-12 Jahre", "Alle"])
        v_img = st.file_uploader("Bild (keine Personen!)", type=["jpg", "png", "jpeg"])
        ds_check = st.checkbox("Ich bestätige, dass keine fremden Personen auf dem Foto sind.*")
        
        if st.form_submit_button("Einsenden"):
            if v_n and v_str and v_p and v_s and ds_check:
                if not check_duplikat("spielplaetze", v_n, v_p) and not check_duplikat("vorschlaege", v_n, v_p):
                    sende_vorschlag(v_n, v_str, v_alt, st.session_state.user, v_b, v_p, v_s, optimiere_bild(v_img), ds_check)
                    st.success("Danke! Wir prüfen das.")
                else: st.warning("Eintrag existiert bereits!")
            else: st.warning("Bitte alle Pflichtfelder (*) ausfüllen.")

def show_profile_area():
    st.title("👤 Profil")
    df_u = hole_df("nutzer")
    user_data = df_u[df_u['benutzername'] == st.session_state.user].iloc[0]
    with st.form("p_edit"):
        nv, nn = st.text_input("Vorname", value=user_data['vorname']), st.text_input("Nachname", value=user_data['nachname'])
        ne, na = st.text_input("E-Mail", value=user_data['email']), st.number_input("Alter", value=int(user_data['alter_jahre']))
        emo = st.selectbox("Avatar", ["🧗", "🦁", "🚀", "🤸"], index=0)
        if st.form_submit_button("Speichern"):
            if aktualisiere_profil(st.session_state.user, ne, nv, nn, na, emo): st.success("Gespeichert!"); st.rerun()

def show_feedback_area():
    st.title("💬 Feedback")
    with st.form("f_form"):
        msg = st.text_area("Deine Nachricht an uns")
        if st.form_submit_button("Senden"):
            if msg.strip() and sende_feedback(st.session_state.user, msg): st.success("Danke!")
