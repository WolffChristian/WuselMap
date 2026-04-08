import streamlit as st
from database_manager import hole_df, speichere_spielplatz
from opencage.geocoder import OpenCageGeocode

def show_admin_area():
    st.title("🛠️ Admin-Bereich")
    
    # Jetzt mit drei Tabs
    t1, t2, t3 = st.tabs(["📥 Vorschläge", "💬 Feedback", "👥 Nutzer"])
    
    # TAB 1: Vorschläge bearbeiten
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            for i, r in df_v.iterrows():
                with st.container(border=True):
                    st.write(f"**{r['name']}** in {r['stadt']}")
                    st.write(f"Eingereicht von: {r.get('eingereicht_von', 'Unbekannt')}")
                    
                    if st.button(f"✅ Freigeben: {r['name']}", key=f"v_{r['id']}"):
                        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                        res = gc.geocode(f"{r['adresse']}, {r['plz']} {r['stadt']}, Deutschland")
                        if res:
                            speichere_spielplatz(
                                r['name'], 
                                res[0]['geometry']['lat'], 
                                res[0]['geometry']['lng'], 
                                r['alter_gruppe'], 
                                r['bundesland'], 
                                r['plz'], 
                                r['stadt'], 
                                r['bild_data'], 
                                r.get('foto_datenschutz', True)
                            )
                            st.success(f"{r['name']} ist jetzt live!"); st.rerun()
        else: 
            st.info("Keine neuen Vorschläge.")

    # TAB 2: Feedback lesen
    with t2:
        df_f = hole_df("feedback")
        if not df_f.empty: 
            st.dataframe(df_f, use_container_width=True)
        else:
            st.write("Kein Feedback vorhanden.")

    # TAB 3: Nutzer-Verwaltung (NEU)
    with t3:
        st.subheader("Registrierte Kletter-Freunde")
        df_n = hole_df("nutzer")
        if not df_n.empty:
            # Wir zeigen nur die wichtigen Spalten an
            spalten = ['benutzername', 'vorname', 'nachname', 'email', 'rolle', 'alter_jahre']
            # Sicherstellen, dass nur vorhandene Spalten gewählt werden
            vorhanden = [c for c in spalten if c in df_n.columns]
            st.dataframe(df_n[vorhanden], use_container_width=True)
        else:
            st.write("Noch keine Nutzer registriert.")
