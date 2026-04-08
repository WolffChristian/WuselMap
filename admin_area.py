import streamlit as st
from database_manager import hole_df, speichere_spielplatz
from opencage.geocoder import OpenCageGeocode

def show_admin_area():
    st.title("🛠️ Admin-Bereich")
    t1, t2 = st.tabs(["📥 Vorschläge", "💬 Feedback"])
    
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            for i, r in df_v.iterrows():
                with st.container(border=True):
                    st.write(f"**{r['name']}** in {r['stadt']}")
                    if st.button(f"✅ Freigeben: {r['name']}", key=f"v_{r['id']}"):
                        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                        res = gc.geocode(f"{r['adresse']}, {r['plz']} {r['stadt']}, Deutschland")
                        if res:
                            speichere_spielplatz(r['name'], res[0]['geometry']['lat'], res[0]['geometry']['lng'], r['alter_gruppe'], r['bundesland'], r['plz'], r['stadt'], r['bild_data'], r['foto_datenschutz'])
                            st.success("Live!"); st.rerun()
        else: st.write("Alles abgearbeitet.")

    with t2:
        df_f = hole_df("feedback")
        if not df_f.empty: st.dataframe(df_f)
