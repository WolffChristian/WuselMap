import streamlit as st
from database_manager import hole_df, speichere_spielplatz, loesche_vorschlag, loesche_feedback

def show_admin_area():
    st.title("🛠️ Admin-Bereich")
    
    t1, t2, t3 = st.tabs(["📥 Vorschläge", "💬 Feedback", "👥 Nutzer"])
    
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            df_v.columns = [c.lower().strip() for c in df_v.columns]
            for i, r in df_v.iterrows():
                v_id = r.get('id', i)
                with st.container(border=True):
                    st.markdown(f"### 📍 {r.get('standort', 'Unbekannt')}")
                    # Spalten angepasst: Text bekommt mehr Platz (3), Bild weniger (1)
                    col_text, col_img = st.columns([3, 1]) 
                    
                    with col_text:
                        st.write(f"**Stadt:** {r.get('stadt')}")
                        st.write(f"**Adresse:** {r.get('adresse')}")
                        
                        c_btn1, c_btn2 = st.columns(2)
                        with c_btn1:
                            if st.button(f"✅ Live schalten", key=f"app_{v_id}"):
                                from opencage.geocoder import OpenCageGeocode
                                gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                                res = gc.geocode(f"{r.get('adresse')}, {r.get('stadt')}, Deutschland")
                                if res:
                                    if speichere_spielplatz(r.get('standort'), res[0]['geometry']['lat'], res[0]['geometry']['lng'], r.get('altersfreigabe'), "Niedersachsen", r.get('plz'), r.get('stadt'), r.get('bild_data'), 1):
                                        loesche_vorschlag(v_id)
                                        st.success("Spot ist live!")
                                        st.rerun()
                        with c_btn2:
                            if st.button(f"❌ Ablehnen", key=f"rej_{v_id}"):
                                if loesche_vorschlag(v_id):
                                    st.info("Vorschlag wurde gelöscht.")
                                    st.rerun()
                                    
                    with col_img:
                        if r.get('bild_data'):
                            # FIX: Bild in Expander und mit fester Breite
                            with st.expander("🖼️ Bild prüfen"):
                                st.image(f"data:image/jpeg;base64,{r.get('bild_data')}", width=250)
        else:
            st.info("☕ Keine neuen Vorschläge vorhanden. Zeit für einen Kaffee!")

    with t2:
        df_f = hole_df("feedback")
        if not df_f.empty:
            for i, r in df_f.iterrows():
                f_id = r.get('id', i)
                with st.container(border=True):
                    st.write(f"**Von:** {r.get('nutzername')}")
                    st.write(f"**Nachricht:** {r.get('nachricht')}")
                    if st.button(f"🗑️ Feedback löschen", key=f"fdel_{f_id}"):
                        if loesche_feedback(f_id):
                            st.success("Erledigt!")
                            st.rerun()
        else:
            st.info("📭 Kein neues Feedback vorhanden.")

    with t3:
        df_n = hole_df("nutzer")
        if not df_n.empty:
            st.table(df_n.drop(columns=['passwort'], errors='ignore'))
        else:
            st.warning("Keine Nutzer in der Datenbank gefunden.")
