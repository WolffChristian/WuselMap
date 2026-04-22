import streamlit as st
import pandas as pd
from database_manager import (
    hole_df, 
    speichere_spielplatz, 
    loesche_vorschlag, 
    loesche_feedback, 
    loesche_spielplatz,
    loesche_oeffentliche_nachrichten,
    get_db_connection,
    optimiere_bild
)
from opencage.geocoder import OpenCageGeocode

# --- MASTER UPDATE FUNKTION (Inkl. Parkplatz) ---
def update_spot_komplett(s_id, d):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        sql = """UPDATE spielplaetze SET 
                 Standort=%s, adresse=%s, stadt=%s, plz=%s, bundesland=%s,
                 altersfreigabe=%s, ausstattung=%s, 
                 hat_schatten=%s, hat_sitze=%s, hat_wc=%s, hat_parkplatz=%s,
                 lat=%s, lon=%s, status=%s 
                 WHERE id=%s"""
        
        params = (
            str(d['name']), str(d['adr']), str(d['stadt']), str(d['plz']), str(d['bund']),
            str(d['alt']), str(d['aus']), int(d['schatten']), int(d['sitze']), int(d['wc']),
            int(d['parken']), float(d['lat']), float(d['lon']), str(d['stat']), int(s_id)
        )
        
        cursor.execute(sql, params)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Datenbank-Fehler beim Update: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# --- STYLING HELPER ---
def apply_blue_style(df):
    return df.style.set_properties(**{
        'background-color': '#0056b3',
        'color': 'white',
        'border-color': 'white'
    })

def show_admin_area():
    # CSS für Mobile Responsiveness & Karten
    st.markdown("""
        <style>
        .stDataFrame { width: 100%; overflow-x: auto; }
        .mobile-card {
            background-color: #0056b3;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid white;
            margin-bottom: 10px;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("🛠️ Admin-Zentrale")
    
    # Jetzt 5 Tabs inkl. Quick-Capture
    t1, t2, t3, t4, t5 = st.tabs(["📥 Vorschläge", "💬 Feedback", "👥 Nutzer", "🏗️ Spot-Manager", "🚀 Quick-Capture"])
    
    # --- TAB 1: VORSCHLÄGE ---
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            df_v.columns = [c.lower().strip() for c in df_v.columns]
            for i, r in df_v.iterrows():
                v_id = r.get('id', i)
                with st.container(border=True):
                    st.write(f"### Vorschlag: {r.get('standort')}")
                    v_adr = st.text_input("Adresse", value=r.get('adresse'), key=f"v_a_{v_id}")
                    v_stadt = st.text_input("Stadt", value=r.get('stadt'), key=f"v_s_{v_id}")
                    
                    if st.button(f"🚀 Live schalten", key=f"live_{v_id}", use_container_width=True):
                        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                        res = gc.geocode(f"{v_adr}, {v_stadt}, Deutschland")
                        if res:
                            lat, lon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
                            # Übergabe aller Felder an die Haupttabelle
                            if speichere_spielplatz(
                                r.get('standort'), lat, lon, r.get('altersfreigabe', 'Alle'), 
                                r.get('bundesland', ''), r.get('plz', ''), v_stadt, 
                                r.get('bild_data'), 'aktiv', r.get('ausstattung', ''), 
                                r.get('hat_schatten', 0), r.get('hat_sitze', 0), r.get('hat_wc', 0), 
                                v_adr, r.get('hat_parkplatz', 0)
                            ):
                                loesche_vorschlag(v_id); st.rerun()
                        else: st.error("Adresse nicht gefunden!")
        else: st.info("Keine neuen Vorschläge.")

    # --- TAB 2: FEEDBACK ---
    with t2:
        df_f = hole_df("feedback")
        if not df_f.empty:
            st.dataframe(apply_blue_style(df_f), use_container_width=True, hide_index=True)
            for i, r in df_f.iterrows():
                if st.button(f"🗑️ Lösche Feedback {r.get('id')}", key=f"f_{i}"):
                    if loesche_feedback(r.get('id')): st.rerun()

    # --- TAB 3: NUTZER ---
    with t3:
        df_n = hole_df("nutzer")
        if not df_n.empty:
            st.dataframe(apply_blue_style(df_n.drop(columns=['passwort', 'profilbild'], errors='ignore')), use_container_width=True, hide_index=True)

    # --- TAB 4: SPOT-MANAGER ---
    with t4:
        st.subheader("🏗️ Spielplatz suchen & bearbeiten")
        ansicht = st.radio("Ansichts-Modus:", ["📱 Mobil-Liste", "💻 PC-Tabelle"], horizontal=True)
        suche = st.text_input("🔍 Name, Stadt oder ID eingeben", "").lower()
        df_s = hole_df("spielplaetze")
        
        if not df_s.empty:
            if suche:
                mask = df_s.apply(lambda r: suche in str(r['Standort']).lower() or suche in str(r['stadt']).lower() or suche == str(r['id']), axis=1)
                df_res = df_s[mask]
            else:
                df_res = df_s.tail(5)

            if ansicht == "💻 PC-Tabelle":
                st.dataframe(apply_blue_style(df_res[['id', 'Standort', 'stadt', 'status']]), use_container_width=True, hide_index=True)
            else:
                for _, spot in df_res.iterrows():
                    st.markdown(f"""<div class="mobile-card"><strong>📍 {spot['Standort']}</strong> (ID: {spot['id']})<br><small>Stadt: {spot['stadt']} | Status: {spot['status']}</small></div>""", unsafe_allow_html=True)

            # EDITOR BEREICH
            if suche and len(df_res) == 1:
                st.divider()
                spot = df_res.iloc[0]
                s_id = spot['id']
                
                with st.form("edit_form_v2"):
                    st.markdown(f"### 🖋️ Editor: {spot['Standort']} (ID: {s_id})")
                    col1, col2 = st.columns(2)
                    with col1:
                        n_name = st.text_input("Name", value=spot['Standort'])
                        n_adr = st.text_input("Adresse", value=spot.get('adresse', ''))
                        n_stadt = st.text_input("Stadt", value=spot.get('stadt', ''))
                        n_plz = st.text_input("PLZ", value=spot.get('plz', ''))
                    
                    with col2:
                        n_stat = st.selectbox("Status", ["aktiv", "wartung"], index=0 if spot['status'] == 'aktiv' else 1)
                        
                        # FIX: Altersgruppe (striktes Matching)
                        alt_optionen = ["0-3", "3-6", "6-12", "Alle"]
                        db_alt = str(spot.get('altersfreigabe', 'Alle')).strip()
                        alt_idx = alt_optionen.index(db_alt) if db_alt in alt_optionen else 3
                        n_alt = st.selectbox("Altersgruppe", alt_optionen, index=alt_idx)
                        
                        geraete_liste = ["Schaukel", "Rutsche", "Wippe", "Klettergerüst", "Sandkasten", "Seilbahn", "Karussell", "Trampolin", "Wasserspiel", "Tischtennis", "Fußballplatz", "Basketball"]
                        aktuelle_ausst = [x.strip() for x in str(spot.get('ausstattung', '')).split(',') if x.strip() in geraete_liste]
                        n_aus_list = st.multiselect("Ausstattung", geraete_liste, default=aktuelle_ausst)
                        n_aus_str = ", ".join(n_aus_list)
                        
                    st.write("**Extras & GPS:**")
                    ce1, ce2, ce3, ce4, ce5, ce6 = st.columns(6)
                    n_sch = ce1.checkbox("🌳 Schatten", value=bool(spot.get('hat_schatten')))
                    n_sit = ce2.checkbox("🪑 Sitze", value=bool(spot.get('hat_sitze')))
                    n_wc = ce3.checkbox("🚽 WC", value=bool(spot.get('hat_wc')))
                    n_park = ce4.checkbox("🚗 Parkplatz", value=bool(spot.get('hat_parkplatz')))
                    n_lat = ce5.number_input("Lat", value=float(spot['lat']), format="%.6f")
                    n_lon = ce6.number_input("Lon", value=float(spot['lon']), format="%.6f")

                    if st.form_submit_button("💾 Änderungen speichern", use_container_width=True):
                        up_d = {
                            'name': n_name, 'adr': n_adr, 'stadt': n_stadt, 'plz': n_plz, 
                            'bund': spot.get('bundesland',''), 'alt': n_alt, 'aus': n_aus_str, 
                            'schatten': 1 if n_sch else 0, 'sitze': 1 if n_sit else 0, 
                            'wc': 1 if n_wc else 0, 'parken': 1 if n_park else 0,
                            'lat': n_lat, 'lon': n_lon, 'stat': n_stat
                        }
                        if update_spot_komplett(s_id, up_d):
                            st.success("Erfolgreich aktualisiert!"); st.rerun()

                if st.button("🗑️ Spot löschen", type="secondary", use_container_width=True):
                    if loesche_spielplatz(s_id): st.rerun()
        else: st.info("Datenbank leer.")

    # --- TAB 5: QUICK-CAPTURE ---
    with t5:
        st.subheader("📸 Schnellerfassung (Unterwegs)")
        st.info("Foto machen, Name tippen, Position sichern - fertig!")
        with st.form("quick_form", clear_on_submit=True):
            foto = st.camera_input("Foto schießen")
            q_name = st.text_input("Name des Spielplatzes")
            col1, col2 = st.columns(2)
            q_lat = col1.number_input("Lat", format="%.6f", value=53.450000)
            q_lon = col2.number_input("Lon", format="%.6f", value=8.130000)
            q_stadt = st.text_input("Stadt", value="Varel")

            if st.form_submit_button("📍 Spot sofort live schalten"):
                if q_name and foto:
                    bild_str = optimiere_bild(foto)
                    if speichere_spielplatz(q_name, q_lat, q_lon, "Alle", "Niedersachsen", "", q_stadt, bild_str, "aktiv", "", 0, 0, 0, "", 0):
                        st.success(f"✅ {q_name} ist jetzt auf der Karte!")
                    else: st.error("Fehler beim Speichern.")
                else: st.warning("Name und Foto fehlen!")

    st.divider()
    if st.button("🚨 Funk leeren", use_container_width=True):
        if loesche_oeffentliche_nachrichten(): st.rerun()