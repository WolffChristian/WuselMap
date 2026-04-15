import streamlit as st
from database_manager import (
    hole_df, 
    speichere_spielplatz, 
    loesche_vorschlag, 
    loesche_feedback, 
    setze_spot_status,
    loesche_spielplatz,
    loesche_oeffentliche_nachrichten,
    get_db_connection
)
from opencage.geocoder import OpenCageGeocode

# Hilfsfunktion zum Updaten von bestehenden Spots (inkl. Adresse)
def update_spot_full(s_id, n_lat, n_lon, n_standort, n_adresse, n_stadt):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        sql = "UPDATE spielplaetze SET lat = %s, lon = %s, Standort = %s, adresse = %s, stadt = %s WHERE id = %s"
        cursor.execute(sql, (n_lat, n_lon, n_standort, n_adresse, n_stadt, s_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Fehler beim Update: {e}")
        return False
    finally: cursor.close(); conn.close()

def show_admin_area():
    st.title("🛠️ Admin-Bereich")
    
    t1, t2, t3, t4 = st.tabs(["📥 Vorschläge", "💬 Feedback", "👥 Nutzer", "🏗️ Spot-Manager"])
    
    # --- TAB 1: VORSCHLÄGE ---
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            df_v.columns = [c.lower().strip() for c in df_v.columns]
            for i, r in df_v.iterrows():
                v_id = r.get('id', i)
                
                with st.container(border=True):
                    st.markdown(f"### 📝 Vorschlag prüfen: {r.get('standort')}")
                    
                    # Bearbeitungs-Felder für den Admin
                    col_edit_1, col_edit_2 = st.columns(2)
                    with col_edit_1:
                        edit_name = st.text_input("Name korrigieren", value=r.get('standort'), key=f"v_name_{v_id}")
                        edit_adr = st.text_input("Adresse korrigieren", value=r.get('adresse'), key=f"v_adr_{v_id}")
                        edit_stadt = st.text_input("Stadt korrigieren", value=r.get('stadt'), key=f"v_stadt_{v_id}")
                    
                    with col_edit_2:
                        edit_alt = st.selectbox("Alter", ["0-3", "3-6", "6-12", "Alle"], index=0, key=f"v_alt_{v_id}")
                        # BILD-CHECK
                        show_img = False
                        if r.get('bild_data'):
                            st.image(f"data:image/jpeg;base64,{r['bild_data']}", width=150)
                            show_img = st.checkbox("✅ Foto übernehmen?", value=True, key=f"v_img_check_{v_id}")
                    
                    st.write(f"**Vorgeschlagene Ausstattung:** {r.get('ausstattung')}")
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button(f"🚀 Jetzt Live schalten", key=f"app_{v_id}", use_container_width=True):
                            # Geocoding für die (evtl. korrigierte) Adresse
                            gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                            res = gc.geocode(f"{edit_adr}, {edit_stadt}, Deutschland")
                            
                            if res:
                                final_lat, final_lon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
                                final_bild = r.get('bild_data') if show_img else None
                                
                                if speichere_spielplatz(
                                    edit_name, final_lat, final_lon, 
                                    edit_alt, r.get('bundesland'), r.get('plz'), edit_stadt, 
                                    final_bild, 1, r.get('ausstattung'), 
                                    r.get('hat_schatten'), r.get('hat_sitze'), r.get('hat_wc'),
                                    edit_adr # Wichtig: Die korrigierte Adresse mitgeben
                                ):
                                    loesche_vorschlag(v_id)
                                    st.success(f"'{edit_name}' ist jetzt live!")
                                    st.rerun()
                            else:
                                st.error("Konnte die Adresse nicht finden. Bitte prüfen!")
                                    
                    with c_btn2:
                        if st.button(f"❌ Ablehnen", key=f"rej_{v_id}", use_container_width=True):
                            if loesche_vorschlag(v_id):
                                st.info("Vorschlag gelöscht."); st.rerun()
        else: st.info("☕ Alles erledigt!")

    # --- TAB 2: FEEDBACK ---
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

    # --- TAB 3: NUTZER ---
    with t3:
        df_n = hole_df("nutzer")
        if not df_n.empty: st.table(df_n.drop(columns=['passwort'], errors='ignore'))

    # --- TAB 4: SPOT-MANAGER ---
    with t4:
        st.subheader("🏗️ Alle Spots verwalten & korrigieren")
        df_s = hole_df("spielplaetze")
        if not df_s.empty:
            for i, r in df_s.iterrows():
                s_id = r.get('id', i)
                status_aktuell = r.get('status', 'aktiv')
                with st.container(border=True):
                    st.write(f"### {r['Standort']}")
                    
                    with st.expander("✏️ Adresse, Stadt oder Name korrigieren"):
                        e_name = st.text_input("Name", value=r['Standort'], key=f"en_{s_id}")
                        e_adr = st.text_input("Straße & Hausnummer", value=r.get('adresse', ''), key=f"ea_{s_id}")
                        e_stadt = st.text_input("Stadt", value=r.get('stadt', ''), key=f"es_{s_id}")
                        
                        col_gps_1, col_gps_2 = st.columns(2)
                        e_lat = col_gps_1.number_input("Lat", value=float(r['lat']), format="%.6f", key=f"elat_{s_id}")
                        e_lon = col_gps_2.number_input("Lon", value=float(r['lon']), format="%.6f", key=f"elon_{s_id}")
                        
                        if st.button("💾 Änderungen am Spot speichern", key=f"sv_{s_id}"):
                            # Falls Adresse geändert wurde, aber GPS noch alt ist, könnte man hier optional neu geocoden.
                            # Hier speichern wir direkt die Eingaben:
                            if update_spot_full(s_id, e_lat, e_lon, e_name, e_adr, e_stadt):
                                st.success("Spot-Daten aktualisiert!"); st.rerun()

                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.write(f"Aktueller Status: `{status_aktuell}`")
                    
                    if status_aktuell == 'aktiv':
                        if c2.button("⚠️ Wartung", key=f"maint_{s_id}"):
                            if setze_spot_status(s_id, 'wartung'): st.rerun()
                    else:
                        if c2.button("✅ Aktivieren", key=f"act_{s_id}"):
                            if setze_spot_status(s_id, 'aktiv'): st.rerun()
                    
                    if c3.button("🗑️ Spot löschen", key=f"sdel_{s_id}"):
                        if loesche_spielplatz(s_id): st.rerun()
        
        st.divider()
        st.subheader("🧹 System-Reinigung")
        if st.button("🚨 Alle öffentlichen Funksprüche löschen", use_container_width=True):
            if loesche_oeffentliche_nachrichten():
                st.success("Geleert!"); st.rerun()
