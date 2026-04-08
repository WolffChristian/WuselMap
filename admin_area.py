import streamlit as st
from database_manager import hole_df, speichere_spielplatz, loesche_vorschlag
from opencage.geocoder import OpenCageGeocode

def show_admin_area():
    st.title("🛠️ Admin-Bereich")
    
    t1, t2, t3 = st.tabs(["📥 Vorschläge", "💬 Feedback", "👥 Nutzer"])
    
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            df_v.columns = [c.lower().strip() for c in df_v.columns]
            st.info(f"Es liegen {len(df_v)} Vorschläge zur Prüfung vor.")
            
            for i, r in df_v.iterrows():
                v_id = r.get('id', i)
                name_spot = r.get('standort', 'Unbekannter Spot')
                stadt_spot = r.get('stadt', 'Unbekannter Ort')
                adresse_spot = r.get('adresse', 'Keine Adresse')
                plz_spot = r.get('plz', '00000')
                alter_spot = r.get('altersfreigabe', 'Alle')
                bild_data = r.get('bild_data')
                
                with st.container(border=True):
                    st.markdown(f"### 📍 {name_spot}")
                    col_text, col_img = st.columns([1, 1])
                    
                    with col_text:
                        st.write(f"**Stadt:** {stadt_spot}")
                        st.write(f"**Adresse:** {adresse_spot}")
                        st.divider()
                        
                        if st.button(f"✅ Spot live schalten", key=f"v_{v_id}"):
                            # --- DOPPEL-CHECK LOGIK ---
                            df_check = hole_df("spielplaetze")
                            # Prüfen ob Name UND Stadt schon existieren
                            existiert_bereits = not df_check[
                                (df_check['Standort'].str.lower() == name_spot.lower()) & 
                                (df_check['stadt'].str.lower() == stadt_spot.lower())
                            ].empty
                            
                            if existiert_bereits:
                                st.warning("⚠️ Dieser Spot existiert bereits in der Datenbank!")
                                # Wir löschen den Vorschlag trotzdem, damit er aus der Admin-Liste verschwindet
                                if loesche_vorschlag(v_id):
                                    st.info("Der doppelte Vorschlag wurde aus der Liste entfernt.")
                                    st.rerun()
                            else:
                                with st.spinner("Wird verarbeitet..."):
                                    gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                                    query = f"{adresse_spot}, {plz_spot} {stadt_spot}, Deutschland"
                                    res = gc.geocode(query)
                                    
                                    if res:
                                        lat, lon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
                                        
                                        if speichere_spielplatz(name_spot, lat, lon, alter_spot, "Niedersachsen", plz_spot, stadt_spot, bild_data, r.get('foto_datenschutz', 1)):
                                            loesche_vorschlag(v_id)
                                            st.success(f"'{name_spot}' ist jetzt live!")
                                            st.rerun()
                                    else:
                                        st.error("Adresse nicht gefunden.")

                    with col_img:
                        if bild_data:
                            st.image(f"data:image/jpeg;base64,{bild_data}", use_container_width=True)

        else:
            st.write("Keine neuen Vorschläge.")

    # Rest bleibt gleich (Feedback & Nutzer)
    with t2:
        df_f = hole_df("feedback")
        if not df_f.empty: st.table(df_f)
    with t3:
        df_n = hole_df("nutzer")
        if not df_n.empty: st.table(df_n.drop(columns=['passwort'], errors='ignore'))
