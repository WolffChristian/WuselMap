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

# --- MASTER UPDATE FUNKTION (Ändert wirklich alles) ---
def update_spot_komplett(s_id, d):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        sql = """UPDATE spielplaetze SET 
                 Standort=%s, adresse=%s, stadt=%s, plz=%s, bundesland=%s,
                 altersfreigabe=%s, ausstattung=%s, 
                 hat_schatten=%s, hat_sitze=%s, hat_wc=%s,
                 lat=%s, lon=%s, status=%s 
                 WHERE id=%s"""
        cursor.execute(sql, (
            d['name'], d['adr'], d['stadt'], d['plz'], d['bund'],
            d['alt'], d['aus'], d['schatten'], d['sitze'], d['wc'],
            d['lat'], d['lon'], d['stat'], s_id
        ))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Fehler beim Master-Update: {e}")
        return False
    finally: cursor.close(); conn.close()

def show_admin_area():
    st.title("🛠️ Admin-Schaltzentrale")
    
    t1, t2, t3, t4 = st.tabs(["📥 Vorschläge", "💬 Feedback", "👥 Nutzer", "🏗️ Spot-Manager"])
    
    # --- TAB 1: NEUE VORSCHLÄGE PRÜFEN ---
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            df_v.columns = [c.lower().strip() for c in df_v.columns]
            for i, r in df_v.iterrows():
                v_id = r.get('id', i)
                with st.container(border=True):
                    st.markdown(f"### 📝 Vorschlag: {r.get('standort')}")
                    c_ed1, c_ed2 = st.columns(2)
                    with c_ed1:
                        v_name = st.text_input("Name", value=r.get('standort'), key=f"v_n_{v_id}")
                        v_adr = st.text_input("Adresse", value=r.get('adresse'), key=f"v_a_{v_id}")
                        v_stadt = st.text_input("Stadt", value=r.get('stadt'), key=f"v_s_{v_id}")
                    with c_ed2:
                        v_alt = st.selectbox("Alter", ["0-3", "3-6", "6-12", "Alle"], key=f"v_al_{v_id}")
                        has_img = r.get('bild_data') is not None and len(str(r.get('bild_data'))) > 20
                        if has_img:
                            st.image(f"data:image/jpeg;base64,{r['bild_data']}", width=150)
                            v_use_img = st.checkbox("✅ Foto übernehmen?", value=True, key=f"v_i_{v_id}")
                        else:
                            st.warning("Kein Foto dabei.")
                            v_use_img = False

                    if st.button(f"🚀 Live schalten", key=f"live_{v_id}", use_container_width=True):
                        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                        res = gc.geocode(f"{v_adr}, {v_stadt}, Deutschland")
                        if res:
                            lat, lon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
                            img = r.get('bild_data') if v_use_img else None
                            if speichere_spielplatz(v_name, lat, lon, v_alt, r.get('bundesland'), r.get('plz'), v_stadt, img, 'aktiv', r.get('ausstattung'), r.get('hat_schatten'), r.get('hat_sitze'), r.get('hat_wc'), v_adr):
                                loesche_vorschlag(v_id)
                                st.success("Spot ist jetzt live!"); st.rerun()
                        else: st.error("Adresse nicht gefunden!")
                    if st.button("🗑️ Ablehnen", key=f"rej_{v_id}"):
                        if loesche_vorschlag(v_id): st.rerun()
        else: st.info("☕ Keine neuen Vorschläge.")

    # --- TAB 2: FEEDBACK ---
    with t2:
        df_f = hole_df("feedback")
        if not df_f.empty:
            for i, r in df_f.iterrows():
                f_id = r.get('id', i)
                with st.container(border=True):
                    st.write(f"**Von:** {r.get('nutzername')} | **Nachricht:** {r.get('nachricht')}")
                    if st.button(f"🗑️ Löschen", key=f"fdel_{f_id}"):
                        if loesche_feedback(f_id): st.rerun()
        else: st.info("📭 Kein Feedback.")

    # --- TAB 3: NUTZER ---
    with t3:
        df_n = hole_df("nutzer")
        if not df_n.empty:
            st.write(f"Gesamtanzahl: {len(df_n)}")
            st.table(df_n.drop(columns=['passwort'], errors='ignore'))

    # --- TAB 4: SPOT-MANAGER (TABELLEN-VERSION) ---
    with t4:
        st.subheader("🏗️ Spielplatz-Datenbank")
        if 'e_id' not in st.session_state: st.session_state.e_id = None
        
        # Suchfunktion für die Tabelle
        s_term = st.text_input("🔍 Schnellsuche (Name oder Stadt)", "")
        df_s = hole_df("spielplaetze")
        
        if not df_s.empty:
            if s_term:
                df_s = df_s[df_s['Standort'].str.contains(s_term, case=False) | df_s['stadt'].str.contains(s_term, case=False)]

            # Tabellenkopf
            c1, c2, c3, c4 = st.columns([2, 1.5, 1, 0.5])
            c1.write("**Name**"); c2.write("**Stadt**"); c3.write("**Status**"); c4.write("**Edit**")
            st.divider()

            for i, r in df_s.iterrows():
                sid = r['id']
                d1, d2, d3, d4 = st.columns([2, 1.5, 1, 0.5])
                d1.write(r['Standort'])
                d2.write(r.get('stadt', '---'))
                d3.write("✅" if r['status'] == 'aktiv' else "⚠️")
                if d4.button("✏️", key=f"ed_{sid}"):
                    st.session_state.e_id = sid
                    st.rerun()

            # --- MASTER-EDITOR (erscheint nur bei Klick auf ✏️) ---
            if st.session_state.e_id:
                st.divider()
                spot = df_s[df_s['id'] == st.session_state.e_id].iloc[0]
                st.markdown(f"### 🖋️ Bearbeite: {spot['Standort']}")
                
                with st.form("master_edit"):
                    col_l, col_r = st.columns(2)
                    with col_l:
                        n_n = st.text_input("Name", value=spot['Standort'])
                        n_a = st.text_input("Adresse", value=spot.get('adresse', ''))
                        n_s = st.text_input("Stadt", value=spot.get('stadt', ''))
                        n_p = st.text_input("PLZ", value=spot.get('plz', ''))
                        n_b = st.text_input("Bundesland", value=spot.get('bundesland', ''))
                        n_st = st.selectbox("Status", ["aktiv", "wartung"], index=0 if spot['status'] == 'aktiv' else 1)
                    with col_r:
                        n_al = st.selectbox("Alter", ["0-3", "3-6", "6-12", "Alle"], index=3)
                        n_au = st.text_area("Geräte", value=spot.get('ausstattung', ''))
                        st.write("**Extras:**")
                        n_sch = st.checkbox("🌳 Schatten", value=bool(spot.get('hat_schatten')))
                        n_sit = st.checkbox("🪑 Sitzplätze", value=bool(spot.get('hat_sitze')))
                        n_wc = st.checkbox("🚽 WC", value=bool(spot.get('hat_wc')))
                        st.write("**Koordinaten:**")
                        lat_c, lon_c = st.columns(2)
                        n_lat = lat_c.number_input("Lat", value=float(spot['lat']), format="%.6f")
                        n_lon = lon_c.number_input("Lon", value=float(spot['lon']), format="%.6f")

                    if st.form_submit_button("💾 Master-Update speichern"):
                        d = {'name': n_n, 'adr': n_a, 'stadt': n_s, 'plz': n_p, 'bund': n_b, 'alt': n_al, 'aus': n_au, 
                             'schatten': 1 if n_sch else 0, 'sitze': 1 if n_sit else 0, 'wc': 1 if n_wc else 0, 
                             'lat': n_lat, 'lon': n_lon, 'stat': n_st}
                        if update_spot_komplett(st.session_state.e_id, d):
                            st.success("Erfolgreich!"); st.session_state.e_id = None; st.rerun()
                    if st.form_submit_button("❌ Abbrechen"):
                        st.session_state.e_id = None; st.rerun()
                
                if st.button("🗑️ DIESEN SPOT LÖSCHEN", type="secondary", use_container_width=True):
                    if loesche_spielplatz(st.session_state.e_id):
                        st.session_state.e_id = None; st.rerun()

        st.divider()
        st.subheader("🧹 System-Reinigung")
        if st.button("🚨 Alle öffentlichen Funksprüche löschen", use_container_width=True):
            if loesche_oeffentliche_nachrichten(): st.success("Gereinigt!"); st.rerun()