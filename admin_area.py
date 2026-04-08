import streamlit as st
from database_manager import hole_df, speichere_spielplatz
from opencage.geocoder import OpenCageGeocode

def show_admin_area():
    st.title("🛠️ Admin")
    t1, t2 = st.tabs(["📥 Vorschläge", "👥 Nutzer"])
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            for i, r in df_v.iterrows():
                with st.container(border=True):
                    st.write(f"**{r['name']}**")
                    if st.button(f"Freigeben: {r['name']}", key=f"v_{r['id']}"):
                        st.success("Wird verarbeitet...")
        else: st.info("Keine Vorschläge.")
    with t2:
        df_n = hole_df("nutzer")
        if not df_n.empty: st.dataframe(df_n)
