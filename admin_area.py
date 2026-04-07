import streamlit as st
import pandas as pd
from database_manager import hole_df, speichere_spielplatz
from opencage.geocoder import OpenCageGeocode

def show_admin_area():
    st.title("🛠️ Admin-Cockpit")
    
    t1, t2, t3, t4 = st.tabs(["📥 Vorschläge", "👥 Nutzer", "💬 Feedback", "🏗️ Neu anlegen"])
    
    with t1:
        st.subheader("Nutzer-Vorschläge")
        df_v = hole_df("vorschlaege")
        if not df_v.empty: st.dataframe(df_v)
        else: st.write("Keine Vorschläge.")

    with t2:
        st.subheader("Registrierte Nutzer")
        df_u = hole_df("nutzer")
        if not df_u.empty: 
            st.dataframe(df_u[['id', 'benutzername', 'email', 'vorname', 'nachname', 'rolle']])
    
    with t3:
        st.subheader("App-Feedback")
        df_f = hole_df("feedback")
        if not df_f.empty: st.dataframe(df_f)
        else: st.write("Kein Feedback.")

    with t4:
        st.subheader("Spot händisch einpflegen")
        with st.form("admin_add"):
            n = st.text_input("Name des Spots")
            a = st.text_input("Genaue Adresse")
            if st.form_submit_button("In Datenbank speichern"):
                gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                r = gc.geocode(a + ", Deutschland")
                if r and speichere_spielplatz(n, r[0]['geometry']['lat'], r[0]['geometry']['lng'], "Alle"):
                    st.success("Spot erfolgreich angelegt!")
