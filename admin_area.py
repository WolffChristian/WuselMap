import streamlit as st
from database_manager import hole_df, speichere_spielplatz, loesche_vorschlag, loesche_feedback, setze_spot_status

def show_admin_area():
    st.title("🛠️ Admin-Bereich")
    
    t1, t2, t3, t4 = st.tabs(["📥 Vorschläge", "💬 Feedback", "👥 Nutzer", "🏗️ Spot-Manager"])
    
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            df_v.columns = [c.lower().strip() for c in df_v.columns]
            for i, r in df_v.iterrows():
                v_id = r.get('id', i)
                with st.container(border=True):
                    st.markdown(f"### 📍 {r.get('standort', 'Unbekannt')}")
                    col_text, col_img = st.columns([3, 1]) 
                    with col_text:
                        st.write(f"**Stadt:** {r.get('stadt')} | **Adresse:** {r.get('adresse')}")
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
                                    st.info("Gelöscht."); st.rerun()
                    with col_img:
                        if r.get('bild_data'):
                            with st.expander("🖼️ Bild"):
                                st.image(f"data:image/jpeg;base64,{r.get('bild_data')}", width=250)
        else: st.info("☕ Alles erledigt!")

    with t2:
        df_f = hole_df("feedback")
        if not df_f.empty:
            for i, r in df_f.iterrows():
                f_id = r.get('id', i)
                with st.container(border=True):
                    st.write(f"**Von:** {r.get('nutzername')} | **Nachricht:** {r.get('nachricht')}")
                    if st.button(f"🗑️ Feedback löschen", key=f"fdel_{f_id}"):
                        if loesche_feedback(f_id): st.rerun()
        else: st.info("📭 Kein Feedback.")

    with t3:
        df_n = hole_df("nutzer")
        if not df_n.empty: st.table(df_n.drop(columns=['passwort'], errors='ignore'))

    with t4:
        st.subheader("🏗️ Alle Live-Spots verwalten")
        df_s = hole_df("spielplaetze")
        if not df_s.empty:
            for i, r in df_s.iterrows():
                s_id = r.get('id', i)
                status_aktuell = r.get('status', 'aktiv')
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"**{r['Standort']}** ({r['stadt']})")
                    c1.write(f"Aktueller Status: `{status_aktuell}`")
                    
                    if status_aktuell == 'aktiv':
                        if c2.button("⚠️ Wartung", key=f"maint_{s_id}"):
                            if setze_spot_status(s_id, 'wartung'):
                                st.success("Spot auf Wartung gesetzt!"); st.rerun()
                    else:
                        if c2.button("✅ Aktivieren", key=f"act_{s_id}"):
                            if setze_spot_status(s_id, 'aktiv'):
                                st.success("Spot wieder aktiv!"); st.rerun()
        else: st.warning("Keine Spielplätze in der Datenbank.")
