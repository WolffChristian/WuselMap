import streamlit as st
from database_manager import hole_df, speichere_spielplatz
from opencage.geocoder import OpenCageGeocode

def show_admin_area():
    st.title("🛠️ Admin-Bereich")
    
    t1, t2, t3 = st.tabs(["📥 Vorschläge", "💬 Feedback", "👥 Nutzer"])
    
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            # Spaltennamen säubern
            df_v.columns = [c.lower().strip() for c in df_v.columns]
            
            st.info(f"Es liegen {len(df_v)} Vorschläge zur Prüfung vor.")
            
            for i, r in df_v.iterrows():
                # Wir holen uns die Daten sicher ab
                name_spot = r.get('standort', 'Unbekannter Spot')
                stadt_spot = r.get('stadt', 'Unbekannter Ort')
                adresse_spot = r.get('adresse', 'Keine Adresse')
                plz_spot = r.get('plz', '00000')
                alter_spot = r.get('altersfreigabe', 'Alle')
                bild_data = r.get('bild_data')
                
                with st.container(border=True):
                    # Kopfzeile des Vorschlags
                    st.markdown(f"### 📍 {name_spot}")
                    
                    # Layout: Links Details, Rechts das Foto
                    col_text, col_img = st.columns([1, 1])
                    
                    with col_text:
                        st.write(f"**Stadt:** {stadt_spot}")
                        st.write(f"**Adresse:** {adresse_spot}")
                        st.write(f"**PLZ:** {plz_spot}")
                        st.write(f"**Altersgruppe:** {alter_spot}")
                        
                        st.divider()
                        
                        # Freigabe-Button
                        if st.button(f"✅ Spot live schalten", key=f"v_{r.get('id', i)}"):
                            with st.spinner("Geocoding & Speichern..."):
                                gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                                query = f"{adresse_spot}, {plz_spot} {stadt_spot}, Deutschland"
                                res = gc.geocode(query)
                                
                                if res:
                                    lat = res[0]['geometry']['lat']
                                    lon = res[0]['geometry']['lng']
                                    
                                    erfolg = speichere_spielplatz(
                                        name_spot, lat, lon, alter_spot, 
                                        "Niedersachsen", plz_spot, stadt_spot, 
                                        bild_data, r.get('foto_datenschutz', 1)
                                    )
                                    
                                    if erfolg:
                                        st.success(f"'{name_spot}' ist jetzt auf der Karte!")
                                        st.rerun()
                                    else:
                                        st.error("Fehler beim Speichern in der Haupttabelle.")
                                else:
                                    st.error("Adresse konnte nicht geocodiert werden.")

                    with col_img:
                        if bild_data:
                            # Wir zeigen das Foto direkt an
                            st.image(f"data:image/jpeg;base64,{bild_data}", 
                                     caption=f"Foto von {name_spot}", 
                                     use_container_width=True)
                        else:
                            st.warning("Kein Foto hochgeladen.")
        else:
            st.write("Keine neuen Vorschläge vorhanden.")

    with t2:
        df_f = hole_df("feedback")
        if not df_f.empty:
            st.table(df_f)
        else:
            st.write("Kein Feedback vorhanden.")

    with t3:
        df_n = hole_df("nutzer")
        if not df_n.empty:
            st.table(df_n.drop(columns=['passwort'], errors='ignore'))
        else:
            st.write("Keine Nutzer registriert.")
