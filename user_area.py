import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
# WICHTIG: Das neue Tool muss installiert sein (pip install streamlit-geolocation)
from streamlit_geolocation import streamlit_geolocation
from database_manager import hole_df, sende_vorschlag, sende_feedback, optimiere_bild, aktualisiere_profil
from messaging import show_wuselfunk, show_wusel_crew, show_spielplatzfunk

# --- HILFSFUNKTIONEN ---

def distanz(lat1, lon1, lat2, lon2):
    """Berechnet die Entfernung zwischen zwei Koordinaten in km"""
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

# --- HAUPTBEREICHE ---

def show_user_area():
    """Die Such- und Kartenansicht für Spielplätze"""
    st.subheader("📍 Spielplätze in deiner Nähe")
    
    with st.expander("🔍 Suche & Filter anpassen", expanded=True):
        c1, c2 = st.columns([3, 1])
        with c1: 
            adr = st.text_input("Wo suchst du?", "Varel")
        with c2: 
            km = st.slider("Umkreis (km)", 1, 100, 20)
        
        f1, f2 = st.columns(2)
        with f1:
            alter_filter = st.multiselect("Altersgruppe", options=["0-3", "3-12", "Alle"], default=["0-3", "3-12", "Alle"])
        with f2:
            show_maintenance = st.toggle("Auch Plätze in Wartung anzeigen", value=True)
    
    df = hole_df("spielplaetze")
    
    if st.button("🔍 Suchen", type="primary", use_container_width=True):
        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        res = gc.geocode(adr + ", Deutschland")
        if res:
            slat, slon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
            
            if not df.empty:
                df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
                df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
                df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                
                final = df[df['distanz'] <= km]
                final = final[final['altersfreigabe'].isin(alter_filter)]
                if not show_maintenance:
                    final = final[final.get('status', 'aktiv') != 'wartung']
                
                final = final.sort_values('distanz')

                if not final.empty:
                    final['Status'] = final['status'].apply(lambda x: "✅ AKTIV" if x == 'aktiv' else "⚠️ WARTUNG")
                    final['Ausstattung_Info'] = final['ausstattung'].apply(lambda x: x if x and str(x).lower() != 'none' else "Keine Angabe")
                    final['size'] = 15 

                    col_l, col_r = st.columns([1, 1.5])
                    with col_l:
                        for i, r in final.iterrows():
                            titel = f"📍 {r['Standort']}"
                            if r.get('status') == 'wartung':
                                titel = f"⚠️ {r['Standort']} (Wartung)"
                            
                            with st.expander(f"{titel} ({round(r['distanz'], 1)} km)"):
                                if r.get('status') == 'wartung':
                                    st.error("🚨 **Achtung:** Dieser Spot wurde als beschädigt gemeldet.")
                                if r.get('bild_data'): 
                                    st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
                                
                                st.write(f"**Ort:** {r['stadt']}")
                                st.write(f"**Ausstattung:** {r['Ausstattung_Info']}")
                                
                                extras = []
                                if r.get('hat_schatten'): extras.append("🌳 Schatten")
                                if r.get('hat_sitze'): extras.append("🪑 Sitzplätze")
                                if r.get('hat_wc'): extras.append("🚽 Toilette")
                                if extras: st.write(" | ".join(extras))
                                
                                st.divider()
                                rating = st.feedback("stars", key=f"rate_{r.get('id', i)}")
                                if rating is not None: st.toast(f"Danke für {rating + 1} Sterne!")

                    with col_r:
                        color_map = {"✅ AKTIV": "#00FF00", "⚠️ WARTUNG": "#FF0000"} 
                        fig = px.scatter_mapbox(
                            final, lat="lat", lon="lon", hover_name="Standort",
                            hover_data={"lat": False, "lon": False, "size": False, "Status": True, "Ausstattung_Info": True},
                            color="Status", color_discrete_map=color_map, size="size", size_max=18, zoom=11, height=600,
                            labels={"Ausstattung_Info": "Ausstattung"}
                        )
                        fig.update_layout(
                            mapbox_style="open-street-map", 
                            margin={"r":0,"t":0,"l":0,"b":0},
                            mapbox_center={"lat": slat, "lon": slon}
                        )
                        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
                else: st.warning("Keine Spots im Umkreis gefunden.")
            else: st.info("Noch keine Spielplätze in der Datenbank.")
        else: st.error("Adresse konnte nicht gefunden werden.")

def show_proposal_area():
    """Bereich zum Vorschlagen neuer Spots mit dem stabilen Weltkugel-Button"""
    st.subheader("💡 Spot vorschlagen")
    
    st.info("Klicke auf die Weltkugel, um deinen Standort zu erfassen:")
    
    # Das neue Tool: Erzeugt einen Button mit Weltkugel-Icon
    location = streamlit_geolocation()
    
    gps_lat = location.get('latitude')
    gps_lon = location.get('longitude')

    if gps_lat and gps_lon:
        st.success(f"📍 Standort fixiert: {gps_lat}, {gps_lon}")
    else:
        st.warning("Kein GPS-Signal. Klicke auf die Weltkugel oder gib die Adresse manuell ein.")

    with st.form("v_form", clear_on_submit=True):
        v_n = st.text_input("Name des Spots*")
        
        # Adresse optional bei GPS-Nutzung
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
        
        st.write("---")
        v_img = st.file_uploader("Foto hochladen", type=["jpg", "png", "jpeg"])
        ds = st.checkbox("Keine Personen auf dem Foto erkennbar*")
        
        if st.form_submit_button("Einsenden", use_container_width=True):
            if v_n and (v_s or gps_lat) and v_st and ds:
                final_lat, final_lon = gps_lat, gps_lon
                
                # Wenn kein GPS-Fix da ist, Geocoder nutzen
                if not final_lat:
                    gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                    res = gc.geocode(f"{v_s}, {v_st}, Deutschland")
                    if res:
                        final_lat, final_lon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
                
                if final_lat:
                    ausst_str = ", ".join(ausst_list)
                    bild_data = optimiere_bild(v_img)
                    if sende_vorschlag(v_n, v_s if v_s else "GPS-Ortung", v_alt, st.session_state.user, v_bund, "00000", v_st, bild_data, 1, ausst_str, 1 if v_schatten else 0, 1 if v_sitze else 0, 1 if v_wc else 0, final_lat, final_lon):
                        st.success(f"Erfolg! '{v_n}' wird geprüft.")
                else:
                    st.error("Weder GPS noch Adresse konnten zugeordnet werden.")
            else: st.warning("Bitte alle Pflichtfelder (*) ausfüllen!")

def show_profile_area():
    """Das Profil-Dashboard mit allen Tabs"""
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