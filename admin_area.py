import streamlit as st
from database_manager import hole_df, speichere_spielplatz
from opencage.geocoder import OpenCageGeocode

def show_admin_area():
    st.title("🛠️ Admin-Bereich")
    
    # Die Tabs müssen eingerückt sein (4 Leerzeichen)
    t1, t2, t3 = st.tabs(["📥 Vorschläge", "💬 Feedback", "👥 Nutzer"])
    
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            for i, r in df_v.iterrows():
                with st.container(border=True):
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
                                r.get('foto_datenschutz', 1)
                            )
                            st.success("Spot live!")
                            st.rerun()
        else:
            st.write("Keine Vorschläge.")

    with t2:
        df_f = hole_df("feedback")
        if not df_f.empty:
            st.table(df_f) # Auch hier auf st.table umgestellt für den Dark Mode
        else:
            st.write("Kein Feedback.")

    with t3:
        # HIER WAR DER FEHLER: Alles unter 'with t3:' muss sauber eingerückt sein
        df_n = hole_df("nutzer")
        if not df_n.empty:
            # st.table statt st.dataframe für die dunkle Optik
            st.table(df_n.drop(columns=['passwort'], errors='ignore'))
        else:
            st.write("Keine Nutzer registriert.")
