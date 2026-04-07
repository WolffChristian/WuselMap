import streamlit as st
from database_manager import hole_df, speichere_spielplatz
from opencage.geocoder import OpenCageGeocode

def show_admin_area():
    st.title("🛠️ Admin-Cockpit")
    t1, t2, t3 = st.tabs(["📥 Vorschläge", "💬 Nutzer-Feedback", "👥 Nutzerliste"])
    
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            for i, r in df_v.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        if r['bild_data']: st.image(f"data:image/jpeg;base64,{r['bild_data']}", width=150)
                    with c2:
                        st.write(f"**{r['name']}** in {r['stadt']}")
                        if st.button(f"✅ Freischalten: {r['name']}", key=f"v_{r['id']}"):
                            gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                            res = gc.geocode(f"{r['adresse']}, {r['plz']} {r['stadt']}, Deutschland")
                            if res:
                                if speichere_spielplatz(r['name'], res[0]['geometry']['lat'], res[0]['geometry']['lng'], "Alle", r['bundesland'], r['plz'], r['stadt'], r['bild_data'], r['foto_datenschutz']):
                                    st.success("Live!")
        else: st.write("Keine Vorschläge.")

    with t2:
        st.subheader("Eingegangene Nachrichten")
        df_f = hole_df("feedback")
        if not df_f.empty:
            # Neueste Nachrichten zuerst anzeigen
            df_f = df_f.sort_values(by='erstellt_am', ascending=False)
            for i, f in df_f.iterrows():
                with st.chat_message("user"):
                    st.write(f"**Von:** {f['nutzername']} ({f['erstellt_am']})")
                    st.write(f.get('nachricht', 'Kein Inhalt'))
        else:
            st.write("Noch kein Feedback erhalten.")

    with t3:
        df_u = hole_df("nutzer")
        if not df_u.empty: st.dataframe(df_u[['benutzername', 'email', 'rolle']])
