import streamlit as st
from database_manager import (
    hole_df, 
    speichere_spielplatz, 
    loesche_vorschlag, 
    loesche_feedback, 
    setze_spot_status,
    loesche_spielplatz,
    loesche_oeffentliche_nachrichten
)
from streamlit_js_eval import streamlit_js_eval

def update_spot_koordinaten(s_id, n_lat, n_lon, n_standort):
    from database_manager import get_db_connection
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        sql = "UPDATE spielplaetze SET lat = %s, lon = %s, standort = %s WHERE id = %s"
        cursor.execute(sql, (n_lat, n_lon, n_standort, s_id))
        conn.commit()
        return True
    except: return False
    finally: cursor.close(); conn.close()

def show_admin_area():
    st.title("🛠️ Admin-Bereich")
    
    t1, t2, t3, t4 = st.tabs(["📥 Vorschläge", "💬 Feedback", "👥 Nutzer", "🏗️ Spot-Manager"])
    
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            df_v.columns = [c.lower().strip() for c in df_v.columns]
            for i, r in df_v.iterrows():
                v_id = r.get('id', i)
                v_lat = r.get('lat')
                v_lon = r.get('lon')
                
                with st.container(border=True):
                    st.markdown(f"### 📍 {r.get('standort', 'Unbekannt')}")
                    col_text, col_img = st.columns([3, 1]) 
                    with col_text:
                        st.write(f"**Stadt:** {r.get('stadt')} | **Bundesland:** {r.get('bundesland')}")
                        st.write(f"**Adresse:** {r.get('adresse')}")
                        if v_lat and v_lon:
                            st.info(f"📍 GPS-Daten vorhanden: {v_lat}, {v_lon}")
                        
                        st.write(f"**Ausstattung:** {r.get('ausstattung')}")
                        extras = []
                        if r.get('hat_schatten'): extras.append("🌳 Schatten")
                        if r.get('hat_sitze'): extras.append("🪑 Sitzplätze")
                        if r.get('hat_wc'): extras.append("🚽 Toilette")
                        st.write(" | ".join(extras))
                        
                        c_btn1, c_btn2 = st.columns(2)
                        with c_btn1:
                            if st.button(f"✅ Live schalten", key=f"app_{v_id}"):
                                # Priorität: Erst vorgeschlagene Koordinaten nutzen
                                final_lat, final_lon = v_lat, v_lon
                                
                                # Fallback auf Geocoder, falls keine Koordinaten vorhanden
                                if not final_lat:
                                    from opencage.geocoder import OpenCageGeocode
                                    gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                                    res = gc.geocode(f"{r.get('adresse')}, {r.get('stadt')}, Deutschland")
                                    if res:
                                        final_lat, final_lon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
                                
                                if final_lat:
                                    if speichere_spielplatz(
                                        r.get('standort'), final_lat, final_lon, 
                                        r.get('altersfreigabe'), r.get('bundesland'), r.get('plz'), r.get('stadt'), 
                                        r.get('bild_data'), 1, r.get('ausstattung'), 
                                        r.get('hat_schatten'), r.get('hat_sitze'), r.get('hat_wc')
                                    ):
                                        loesche_vorschlag(v_id)
                                        st.success("Spot ist live!")
                                        st.rerun()
                                else:
                                    st.error("Keine Koordinaten gefunden!")
                                    
                        with c_btn2:
                            if st.button(f"❌ Ablehnen", key=f"rej_{v_id}"):
                                if loesche_vorschlag(v_id):
                                    st.info("Gelöscht."); st.rerun()
                    with col_img:
                        if r.get('bild_data'):
                            with st.expander("🖼️ Bild"):
                                st.image(f"data:image/jpeg;base64,{r['bild_data']}", width=250)
        else: st.info("☕ Alles erledigt!")

    # ... (Rest der Datei bleibt gleich) ...

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
        st.subheader("🏗️ Alle Spots verwalten")
        
        # GPS Check für Admin vor Ort
        if st.checkbox("📍 Meine aktuelle GPS-Position für Korrekturen nutzen"):
            loc_admin = streamlit_js_eval(data_of='geolocation', stop_after_found=True, key='admin_gps')
            if loc_admin:
                st.info(f"Deine Position: {loc_admin['coords']['latitude']}, {loc_admin['coords']['longitude']}")

        df_s = hole_df("spielplaetze")
        if not df_s.empty:
            for i, r in df_s.iterrows():
                s_id = r.get('id', i)
                status_aktuell = r.get('status', 'aktiv')
                with st.container(border=True):
                    st.write(f"### {r['Standort']}")
                    
                    with st.expander("✏️ Koordinaten oder Name anpassen"):
                        new_name = st.text_input("Name", value=r['Standort'], key=f"edit_n_{s_id}")
                        c_edit1, c_edit2 = st.columns(2)
                        new_lat = c_edit1.number_input("Breitengrad (Lat)", value=float(r['lat']), format="%.6f", key=f"edit_lat_{s_id}")
                        new_lon = c_edit2.number_input("Längengrad (Lon)", value=float(r['lon']), format="%.6f", key=f"edit_lon_{s_id}")
                        
                        if st.button("💾 Änderungen speichern", key=f"save_{s_id}"):
                            if update_spot_koordinaten(s_id, new_lat, new_lon, new_name):
                                st.success("Daten aktualisiert!"); st.rerun()

                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.write(f"Status: `{status_aktuell}`")
                    
                    if status_aktuell == 'aktiv':
                        if c2.button("⚠️ Wartung", key=f"maint_{s_id}"):
                            if setze_spot_status(s_id, 'wartung'): st.rerun()
                    else:
                        if c2.button("✅ Aktivieren", key=f"act_{s_id}"):
                            if setze_spot_status(s_id, 'aktiv'): st.rerun()
                    
                    if c3.button("🗑️ Löschen", key=f"sdel_{s_id}"):
                        if loesche_spielplatz(s_id): st.rerun()
        
        st.divider()
        st.subheader("🧹 System-Reinigung")
        if st.button("🚨 Alle öffentlichen Funksprüche löschen", use_container_width=True):
            if loesche_oeffentliche_nachrichten():
                st.success("Geleert!"); st.rerun()