import streamlit as st
from database_manager import hole_df, speichere_spielplatz
from opencage.geocoder import OpenCageGeocode

def show_admin_area():
    st.title("🛠️ Admin-Cockpit")
    t1, t2 = st.tabs(["📥 Vorschläge prüfen", "👥 Nutzerliste"])
    
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            for i, r in df_v.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        if r['bild_data']: st.image(f"data:image/jpeg;base64,{r['bild_data']}", width=150)
                    with c2:
                        st.write(f"**{r['name']}**")
                        st.write(f"Adresse: {r['adresse']}, {r['plz']} {r['stadt']}")
                        st.write(f"Datenschutz bestätigt: {'✅ Ja' if r['foto_datenschutz'] else '❌ Nein'}")
                        if st.button(f"✅ Live schalten: {r['name']}", key=f"v_{r['id']}"):
                            gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                            res = gc.geocode(f"{r['adresse']}, {r['plz']} {r['stadt']}, Deutschland")
                            if res:
                                lat, lon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
                                if speichere_spielplatz(r['name'], lat, lon, r['alter_gruppe'], r['bundesland'], r['plz'], r['stadt'], r['bild_data'], r['foto_datenschutz']):
                                    st.success(f"{r['name']} ist jetzt online!")
        else: st.write("Keine Vorschläge.")

    with t2:
        df_u = hole_df("nutzer")
        if not df_u.empty: st.dataframe(df_u[['benutzername', 'email', 'rolle']])
