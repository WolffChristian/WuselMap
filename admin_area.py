import streamlit as st
from database_manager import hole_df, speichere_spielplatz, loesche_vorschlag # loesche_vorschlag importiert

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
                        st.write(f"**PLZ:** {plz_spot}")
                        st.write(f"**Altersgruppe:** {alter_spot}")
                        st.divider()
                        
                        if st.button(f"✅ Spot live schalten", key=f"v_{v_id}"):
                            with st.spinner("Geocoding & Speichern..."):
                                from opencage.geocoder import OpenCageGeocode
                                gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                                query = f"{adresse_spot}, {plz_spot} {stadt_spot}, Deutschland"
                                res = gc.geocode(query)
                                
                                if res:
                                    lat = res[0]['geometry']['lat']
                                    lon = res[0]['geometry']['lng']
                                    
                                    # 1. Schritt: In Haupttabelle speichern
                                    erfolg_save = speichere_spielplatz(
                                        name_spot, lat, lon, alter_spot, 
                                        "Niedersachsen", plz_spot, stadt_spot, 
                                        bild_data, r.get('foto_datenschutz', 1)
                                    )
                                    
                                    if erfolg_save:
                                        # 2. Schritt: Aus Vorschlägen löschen
                                        if loesche_vorschlag(v_id):
                                            st.success(f"'{name_spot}' ist live und Vorschlag wurde archiviert!")
                                            st.rerun() # Seite neu laden -> Vorschlag ist weg
                                        else:
                                            st.warning("Spot ist live, aber Vorschlag konnte nicht gelöscht werden.")
                                    else:
                                        st.error("Fehler beim Speichern.")
                                else:
                                    st.error("Adresse nicht gefunden.")

                    with col_img:
                        if bild_data:
                            st.image(f"data:image/jpeg;base64,{bild_data}", use_container_width=True)
                        else:
                            st.warning("Kein Foto.")
        else:
            st.write("Keine neuen Vorschläge vorhanden.")

    with t2:
        df_f = hole_df("feedback")
        if not df_f.empty: st.table(df_f)
        else: st.write("Kein Feedback.")

    with t3:
        df_n = hole_df("nutzer")
        if not df_n.empty:
            st.table(df_n.drop(columns=['passwort'], errors='ignore'))
        else: st.write("Keine Nutzer.")
