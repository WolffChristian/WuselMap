import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
# NEUES TOOL
from streamlit_geolocation import streamlit_geolocation
from database_manager import hole_df, sende_vorschlag, sende_feedback, optimiere_bild, aktualisiere_profil
from messaging import show_wuselfunk, show_wusel_crew, show_spielplatzfunk

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

# ... (show_user_area bleibt gleich) ...

def show_proposal_area():
    st.subheader("💡 Spot vorschlagen")
    
    st.info("Klicke auf die Weltkugel, um deinen Standort zu erfassen:")
    
    # Das neue Tool zeigt einen Button mit Weltkugel
    location = streamlit_geolocation()
    
    gps_lat = location.get('latitude')
    gps_lon = location.get('longitude')

    if gps_lat and gps_lon:
        st.success(f"📍 Standort fixiert: {gps_lat}, {gps_lon}")
    else:
        st.warning("Kein GPS-Signal. Klicke auf die Weltkugel oder gib die Adresse manuell ein.")

    with st.form("v_form", clear_on_submit=True):
        v_n = st.text_input("Name des Spots*")
        v_s = st.text_input("Straße & Hausnr. (optional bei GPS)")
        v_st = st.text_input("Stadt*", value="Varel")
        v_bund = st.selectbox("Bundesland*", ["Niedersachsen", "Bremen", "Hamburg", "Schleswig-Holstein", "Nordrhein-Westfalen"])
        v_alt = st.selectbox("Altersgruppe", ["0-3", "3-12", "Alle"])
        
        st.write("---")
        ausst_list = st.multiselect("Ausstattung", ["Rutsche", "Schaukel", "Seilbahn", "Klettergerüst", "Sandkasten", "Wippe", "Karussell"])
        c1, c2, c3 = st.columns(3)
        v_schatten = c1.checkbox("🌳 Schatten")
        v_sitze = c2.checkbox("🪑 Sitzplätze")
        v_wc = c3.checkbox("🚽 Toilette")
        
        v_img = st.file_uploader("Foto hochladen", type=["jpg", "png", "jpeg"])
        ds = st.checkbox("Keine Personen auf dem Foto erkennbar*")
        
        if st.form_submit_button("Einsenden", use_container_width=True):
            if v_n and (v_s or gps_lat) and v_st and ds:
                f_lat, f_lon = gps_lat, gps_lon
                
                if not f_lat:
                    gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                    res = gc.geocode(f"{v_s}, {v_st}, Deutschland")
                    if res:
                        f_lat, f_lon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
                
                if f_lat:
                    bild_data = optimiere_bild(v_img)
                    if sende_vorschlag(v_n, v_s if v_s else "GPS-Ortung", v_alt, st.session_state.user, v_bund, "00000", v_st, bild_data, 1, ", ".join(ausst_list), 1 if v_schatten else 0, 1 if v_sitze else 0, 1 if v_wc else 0, f_lat, f_lon):
                        st.success(f"Erfolg! '{v_n}' wird geprüft.")
                else:
                    st.error("Position konnte nicht ermittelt werden.")
            else: st.warning("Bitte Pflichtfelder (*) ausfüllen!")


def show_profile_area():
    """Das Profil-Dashboard"""
    st.title("Mein Bereich")
    sub_tabs = st.tabs(["⚙️ Profil-Daten", "📍 Suche", "💡 Vorschlag", "🔒 Wuselfunk", "👥 Freunde"])
    
    with sub_tabs[0]:
        df_u = hole_df("nutzer")
        u_data = df_u[df_u['benutzername'] == st.session_state.user].iloc[0]
        with st.form("p_data"):
            st.markdown(f"### Willkommen, {st.session_state.user}!")
            ne = st.text_input("E-Mail", value=u_data['email'])
            nv = st.text_input("Vorname", value=u_data['vorname'])
            nn = st.text_input("Nachname", value=u_data['nachname'])
            na = st.number_input("Alter", value=int(u_data['alter_jahre']))
            if st.form_submit_button("Speichern"):
                aktualisiere_profil(st.session_state.user, ne, nv, nn, na, u_data.get('profil_emoji', '🧗'))
                st.success("Daten aktualisiert!"); st.rerun()
                
    with sub_tabs[1]: show_user_area()
    with sub_tabs[2]: show_proposal_area()
    with sub_tabs[3]: show_wuselfunk()
    with sub_tabs[4]: show_wusel_crew()

def show_feedback_area():
    """Feedback-Funktion"""
    st.title("💬 Feedback")
    st.write("Hilf uns, WuselMap noch besser zu machen!")
    with st.form("f_form"):
        msg = st.text_area("Deine Nachricht an uns...")
        if st.form_submit_button("Feedback absenden"):
            if msg:
                if sende_feedback(st.session_state.user, msg):
                    st.success("Vielen Dank für dein Feedback!"); st.rerun()
            else:
                st.warning("Bitte gib eine Nachricht ein.")