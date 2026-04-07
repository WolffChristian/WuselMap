import streamlit as st
from database_manager import hole_df, speichere_spielplatz
from opencage.geocoder import OpenCageGeocode

def show_admin_area():
    st.title("🛠️ Admin-Bereich")
    
    # Hier sind jetzt wieder alle drei Tabs drin!
    t1, t2, t3 = st.tabs(["📥 Vorschläge", "💬 Feedback", "👥 Nutzerliste"])
    
    with t1:
        st.subheader("Eingegangene Spot-Vorschläge")
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            for i, r in df_v.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        if r.get('bild_data'): 
                            st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
                    with c2:
                        st.write(f"**{r['name']}**")
                        st.write(f"Ort: {r['plz']} {r['stadt']}, {r['adresse']}")
                        st.write(f"Vorgeschlagen von: {r['eingereicht_von']}")
                        
                        if st.button(f"✅ Spot freigeben: {r['name']}", key=f"v_{r['id']}"):
                            gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                            res = gc.geocode(f"{r['adresse']}, {r['plz']} {r['stadt']}, Deutschland")
                            if res:
                                lat = res[0]['geometry']['lat']
                                lon = res[0]['geometry']['lng']
                                if speichere_spielplatz(r['name'], lat, lon, r['alter_gruppe'], r['bundesland'], r['plz'], r['stadt'], r['bild_data'], r['foto_datenschutz']):
                                    st.success(f"'{r['name']}' ist jetzt auf der Karte!")
                                    st.rerun()
                            else:
                                st.error("Adresse konnte nicht gefunden werden.")
        else:
            st.info("Keine neuen Vorschläge vorhanden.")

    with t2:
        st.subheader("Nutzer-Feedback")
        df_f = hole_df("feedback")
        if not df_f.empty:
            # Sortieren nach Datum (neueste oben)
            df_f = df_f.sort_values(by='erstellt_am', ascending=False)
            for i, f in df_f.iterrows():
                with st.chat_message("user"):
                    st.write(f"**{f['nutzername']}** schrieb am {f['erstellt_am']}:")
                    st.write(f['nachricht'])
        else:
            st.info("Noch kein Feedback eingegangen.")

    with t3:
        st.subheader("Registrierte Nutzer")
        df_u = hole_df("nutzer")
        if not df_u.empty:
            # Wir zeigen wichtige Infos an, aber das Passwort bleibt (gehasht) natürlich versteckt
            st.dataframe(
                df_u[['id', 'benutzername', 'email', 'vorname', 'nachname', 'rolle', 'erstellt_am']],
                use_container_width=True
            )
            st.write(f"Gesamtanzahl Nutzer: **{len(df_u)}**")
        else:
            st.warning("Keine Nutzer in der Datenbank gefunden.")
