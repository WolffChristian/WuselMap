import streamlit as st
import pandas as pd
from database_manager import hole_df, speichere_spielplatz
from opencage.geocoder import OpenCageGeocode

def show_admin_area():
    st.title("🛠️ Admin-Cockpit")
    t1, t2, t3 = st.tabs(["📥 Vorschläge prüfen", "👥 Nutzer", "🏗️ Neu anlegen"])
    
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            for i, r in df_v.iterrows():
                with st.container(border=True):
                    c_a, c_b = st.columns([1, 2])
                    with c_a:
                        if r['bild_data']: st.image(f"data:image/jpeg;base64,{r['bild_data']}", width=150)
                    with c_b:
                        st.write(f"**{r['name']}** in {r['stadt']} ({r['plz']})")
                        st.write(f"Vorgeschlagen von: {r['eingereicht_von']}")
                        if st.button(f"✅ Freischalten: {r['name']}", key=f"btn_{r['id']}"):
                            gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                            res = gc.geocode(f"{r['adresse']}, {r['plz']} {r['stadt']}, Deutschland")
                            if res:
                                lat, lon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
                                if speichere_spielplatz(r['name'], lat, lon, r['alter_gruppe'], r['bundesland'], r['plz'], r['stadt'], r['bild_data']):
                                    st.success("Spot ist jetzt live!")
                                    # Hier könnte man noch einen DELETE-Befehl für den Vorschlag einbauen
            st.dataframe(df_v)
        else: st.write("Keine neuen Vorschläge.")

    with t3:
        st.subheader("Händisch anlegen")
        with st.form("admin_add"):
            n, a, p, s = st.text_input("Name"), st.text_input("Straße"), st.text_input("PLZ"), st.text_input("Stadt")
            bund = st.selectbox("Bundesland", ["Niedersachsen", "Bayern", "NRW", "..."]) # Kurzform für Test
            if st.form_submit_button("Direkt Speichern"):
                gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                r = gc.geocode(f"{a}, {p} {s}, Deutschland")
                if r:
                    speichere_spielplatz(n, r[0]['geometry']['lat'], r[0]['geometry']['lng'], "Alle", bund, p, s, None)
                    st.success("Gespeichert!")
