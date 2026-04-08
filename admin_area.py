import streamlit as st
from database_manager import hole_df, speichere_spielplatz
from opencage.geocoder import OpenCageGeocode

def show_admin_area():
    st.title("🛠️ Admin-Bereich")
    # Ab hier muss alles mit 4 Leerzeichen oder einem Tab eingerückt sein!
    t1, t2, t3 = st.tabs(["📥 Vorschläge", "💬 Feedback", "👥 Nutzer"])
    
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            for i, r in df_v.iterrows():
                with st.container(border=True):
                    # Wir nutzen hier schon die korrigierten Spaltennamen von vorhin!
                    st.write(f"**{r['standort']}** in {r['stadt']}")
                    if st.button(f"✅ Freigeben: {r['standort']}", key=f"v_{r['id']}"):
                        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                        res = gc.geocode(f"{r['adresse']}, {r['plz']} {r['stadt']}, Deutschland")
                        if res:
                            speichere_spielplatz(
                                r['standort'], 
                                res[0]['geometry']['lat'], 
                                res[0]['geometry']['lng'], 
                                r['altersfreigabe'], 
                                r['bundesland'], 
                                r['plz'], 
                                r['stadt'], 
                                r['bild_data'], 
                                r.get('foto_datenschutz', True)
                            )
                            st.success("Spot live!")
                            st.rerun()
        else:
            st.write("Keine Vorschläge.")

    with t2:
        df_f = hole_df("feedback")
        if not df_f.empty:
            st.dataframe(df_f, use_container_width=True)
        else:
            st.write("Kein Feedback.")

   with t3:
        df_n = hole_df("nutzer")
        if not df_n.empty:
            # KORREKTUR: st.table statt st.dataframe
            # st.table erzeugt eine saubere HTML-Tabelle, die unser CSS in styles.py versteht!
            st.table(df_n.drop(columns=['passwort'], errors='ignore'))
        else:
            st.write("Keine Nutzer registriert.")
