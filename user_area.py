import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import requests
from database_manager import hole_df, sende_vorschlag, sende_feedback, optimiere_bild, aktualisiere_profil
from messaging import show_wuselfunk, show_wusel_crew 

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

def show_user_area():
    st.subheader("📍 Kletter-Spots in deiner Nähe")
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Wo suchst du?", "Varel")
    with c2: km = st.slider("Umkreis (km)", 1, 100, 20)
    
    if st.button("🔍 Suchen", type="primary"):
        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        res = gc.geocode(adr + ", Deutschland")
        if res:
            slat, slon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
            df = hole_df("spielplaetze")
            if not df.empty:
                df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
                df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
                df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                final = df[df['distanz'] <= km].sort_values('distanz')
                
                if not final.empty:
                    col_l, col_r = st.columns([1, 1.5])
                    with col_l:
                        for i, r in final.iterrows():
                            # Titel ändert sich, wenn auf Wartung
                            titel = f"📍 {r['Standort']}"
                            if r.get('status') == 'wartung':
                                titel = f"⚠️ {r['Standort']} (Wartung)"
                            
                            with st.expander(f"{titel} ({round(r['distanz'], 1)} km)"):
                                # WARTUNGS-HINWEIS
                                if r.get('status') == 'wartung':
                                    st.error("🚨 **Achtung:** Dieser Spot wurde als beschädigt gemeldet. Nutzung auf eigene Gefahr!")

                                if r.get('bild_data'): 
                                    st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
                                
                                st.write(f"**Ort:** {r['stadt']}")
                                
                                # BEWERTUNG (Sterne)
                                st.write("**Wie gefällt dir der Spot?**")
                                rating = st.feedback("stars", key=f"rate_{r.get('id', i)}")
                                if rating is not None:
                                    # Hinweis: Speicher-Logik muss in database_manager ergänzt werden
                                    st.toast(f"Danke für {rating + 1} Sterne!")

                                # WETTER
                                try:
                                    stadt_w = r['stadt'].replace(" ", "+")
                                    w_res = requests.get(f"https://wttr.in/{stadt_w}?format=%c+%t&m", timeout=2)
                                    if w_res.status_code == 200:
                                        wetter_text = w_res.content.decode('utf-8').replace("Â", "")
                                        st.info(f"Wetter: {wetter_text}")
                                except: pass 

                    with col_r:
                        fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10, height=500, color_discrete_sequence=["#ff8c00"])
                        fig.update_layout(
                            mapbox_style="open-street-map", 
                            margin={"r":0,"t":0,"l":0,"b":0},
                            mapbox_center={"lat": slat, "lon": slon}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else: st.warning("Keine Spots im Umkreis gefunden.")
        else: st.error("Adresse nicht gefunden.")

# Rest der Funktionen (show_proposal_area, etc.) bleiben wie von dir gesendet...
def show_proposal_area():
    st.subheader("💡 Spot vorschlagen")
    with st.form("v_form", clear_on_submit=True):
        v_n = st.text_input("Name des Spots*")
        v_s = st.text_input("Straße & Hausnr.*")
        v_st = st.text_input("Stadt*")
        v_p = st.text_input("PLZ (optional)") 
        v_alt = st.selectbox("Altersgruppe", ["0-3", "3-12", "Alle"])
        v_img = st.file_uploader("Foto hochladen", type=["jpg", "png", "jpeg"])
        ds = st.checkbox("Keine Personen auf dem Foto erkennbar*")
        if st.form_submit_button("Einsenden"):
            if v_n and v_s and v_st and ds:
                plz_final = v_p.strip()
                if not plz_final:
                    try:
                        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                        res = gc.geocode(f"{v_s}, {v_st}, Deutschland")
                        plz_final = res[0]['components'].get('postcode', "00000") if res else "00000"
                    except: plz_final = "00000"
                bild_data = optimiere_bild(v_img)
                if sende_vorschlag(v_n, v_s, v_alt, st.session_state.user, "Niedersachsen", plz_final, v_st, bild_data, 1 if ds else 0):
                    st.success(f"Erfolg! Spot wird geprüft.")
            else: st.warning("Pflichtfelder (*) ausfüllen!")

def show_profile_area():
    st.title("👤 Mein Bereich")
    sub_tabs = st.tabs(["⚙️ Profil-Daten", "📍 Suche", "💡 Vorschlag", "📻 Wuselfunk", "👥 Wusel-Crew"])
    with sub_tabs[0]:
        df_u = hole_df("nutzer")
        user_data = df_u[df_u['benutzername'] == st.session_state.user].iloc[0]
        emo_liste = ["🧗", "🤸", "🦁", "🚀"]
        aktuelles_emo = user_data.get('profil_emoji', "🧗")
        emo_index = emo_liste.index(aktuelles_emo) if aktuelles_emo in emo_liste else 0
        with st.form("p_data"):
            ne = st.text_input("E-Mail", value=user_data['email'])
            nv = st.text_input("Vorname", value=user_data['vorname'])
            nn = st.text_input("Nachname", value=user_data['nachname'])
            na = st.number_input("Alter", value=int(user_data['alter_jahre']))
            emo = st.selectbox("Profil-Emoji", emo_liste, index=emo_index)
            if st.form_submit_button("Speichern"):
                aktualisiere_profil(st.session_state.user, ne, nv, nn, na, emo)
                st.success("Daten aktualisiert!"); st.rerun()
    with sub_tabs[1]: show_user_area()
    with sub_tabs[2]: show_proposal_area()
    with sub_tabs[3]: show_wuselfunk()
    with sub_tabs[4]: show_wusel_crew()

def show_feedback_area():
    st.title("💬 Feedback")
    with st.form("f_form"):
        msg = st.text_area("Deine Nachricht")
        if st.form_submit_button("Absenden"):
            if msg and sende_feedback(st.session_state.user, msg):
                st.success("Vielen Dank!"); st.rerun()

def show_legal_area():
    st.title("📄 Rechtliches & Sicherheit")
    legal_tabs = st.tabs(["⚖️ Impressum", "🔒 Datenschutz", "🛡️ Jugendschutz"])
    with legal_tabs[0]: 
        st.write("**Verantwortlich:** Christian Wolff")
        st.write("Kontakt: info@wuselmap.de")
    with legal_tabs[1]: st.write("Datenschutz-Infos...")
    with legal_tabs[2]: st.write("Eltern haften für ihre Kinder.")
