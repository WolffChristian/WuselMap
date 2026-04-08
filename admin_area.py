import streamlit as st
from database_manager import hole_df, speichere_spielplatz
from opencage.geocoder import OpenCageGeocode

def show_admin_area():
    st.title("🛠️ Admin-Bereich")
    
    t1, t2, t3 = st.tabs(["📥 Vorschläge", "💬 Feedback", "👥 Nutzer"])
    
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            # Wir säubern die Spaltennamen (alle klein und ohne Leerzeichen)
            df_v.columns = [c.lower().strip() for c in df_v.columns]
            
            for i, r in df_v.iterrows():
                with st.container(border=True):
                    # SICHERHEITS-CHECK: Wir suchen den Namen, egal wie er geschrieben ist
                    # Wir probieren 'standort', falls das fehlt 'name', sonst 'Unbekannt'
                    name_spot = r.get('standort', r.get('name', 'Unbekannter Spot'))
                    stadt_spot = r.get('stadt', 'Unbekannter Ort')
                    
                    st.write(f"**{name_spot}** in {stadt_spot}")
                    
                    # Button mit ID
                    btn_id = r.get('id', i)
                    if st.button(f"✅ Freigeben: {name_spot}", key=f"v_{btn_id}"):
                        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                        # Suche mit den verfügbaren Daten
                        query = f"{r.get('adresse', '')}, {r.get('plz', '')} {stadt_spot}, Deutschland"
                        res = gc.geocode(query)
                        
                        if res:
                            lat = res[0]['geometry']['lat']
                            lon = res[0]['geometry']['lng']
                            
                            erfolg = speichere_spielplatz(
                                name_spot, 
                                lat, 
                                lon, 
                                r.get('altersfreigabe', 'Alle'), 
                                r.get('bundesland', 'Niedersachsen'), 
                                r.get('plz', ''), 
                                stadt_spot, 
                                r.get('bild_data', None), 
                                r.get('foto_datenschutz', 1)
                            )
                            
                            if erfolg:
                                st.success(f"'{name_spot}' ist jetzt live!")
                                st.rerun()
                            else:
                                st.error("Konnte nicht in Haupttabelle speichern.")
                        else:
                            st.error("Adresse nicht gefunden.")
        else:
            st.write("Keine Vorschläge vorhanden.")

    with t2:
        df_f = hole_df("feedback")
        if not df_f.empty:
            st.table(df_f)
        else:
            st.write("Kein Feedback.")

    with t3:
        df_n = hole_df("nutzer")
        if not df_n.empty:
            st.table(df_n.drop(columns=['passwort'], errors='ignore'))
        else:
            st.write("Keine Nutzer registriert.")
