import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import requests
from database_manager import hole_df, sende_vorschlag, sende_feedback, optimiere_bild, aktualisiere_profil
from messaging import show_wuselfunk, show_wusel_crew, show_spielplatzfunk

# --- HILFSFUNKTIONEN ---

def distanz(lat1, lon1, lat2, lon2):
    """Berechnet die Entfernung zwischen zwei Koordinaten in km (Haversine-Formel)"""
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

# --- HAUPTBEREICHE ---

def show_user_area():
    """Die Such- und Kartenansicht für Spielplätze"""
    st.subheader("📍 Spielplätze in deiner Nähe")
    
    with st.expander("🔍 Suche & Filter anpassen", expanded=True):
        c1, c2 = st.columns([3, 1])
        with c1: 
            adr = st.text_input("Wo suchst du?", "Varel")
        with c2: 
            km = st.slider("Umkreis (km)", 1, 100, 20)
        
        f1, f2 = st.columns(2)
        with f1:
            alter_filter = st.multiselect("Altersgruppe", options=["0-3", "3-12", "Alle"], default=["0-3", "3-12", "Alle"])
        with f2:
            show_maintenance = st.toggle("Auch Plätze in Wartung anzeigen", value=True)
    
    df = hole_df("spielplaetze")
    
    if st.button("🔍 Suchen", type="primary", use_container_width=True):
        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        res = gc.geocode(adr + ", Deutschland")
        if res:
            slat, slon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
            
            if not df.empty:
                # Koordinaten in Zahlen umwandeln für Berechnung
                df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
                df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
                df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                
                # Filtern nach Kriterien
                final = df[df['distanz'] <= km]
                final = final[final['altersfreigabe'].isin(alter_filter)]
                if not show_maintenance:
                    final = final[final.get('status', 'aktiv') != 'wartung']
                
                final = final.sort_values('distanz')

                if not final.empty:
                    # Daten für Karte aufbereiten
                    final['Status'] = final['status'].apply(lambda x: "✅ AKTIV" if x == 'aktiv' else "⚠️ WARTUNG")
                    final['Ausstattung_Info'] = final['ausstattung'].apply(lambda x: x if x and str(x).lower() != 'none' else "Keine Angabe")
                    final['size'] = 15 

                    col_l, col_r = st.columns([1, 1.5])
                    with col_l:
                        for i, r in final.iterrows():
                            titel = f"📍 {r['Standort']}"
                            if r.get('status') == 'wartung':
                                titel = f"⚠️ {r['Standort']} (Wartung)"
                            
                            with st.expander(f"{titel} ({round(r['distanz'], 1)} km)"):
                                if r.get('status') == 'wartung':
                                    st.error("🚨 **Achtung:** Dieser Spot wurde als beschädigt gemeldet.")
                                if r.get('bild_data'): 
                                    st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
                                
                                st.write(f"**Ort:** {r['stadt']}")
                                st.write(f"**Ausstattung:** {r['Ausstattung_Info']}")
                                
                                extras = []
                                if r.get('hat_schatten'): extras.append("🌳 Schatten")
                                if r.get('hat_sitze'): extras.append("🪑 Sitzplätze")
                                if r.get('hat_wc'): extras.append("🚽 Toilette")
                                if extras: st.write(" | ".join(extras))
                                
                                st.divider()
                                rating = st.feedback("stars", key=f"rate_{r.get('id', i)}")
                                if rating is not None: st.toast(f"Danke für {rating + 1} Sterne!")

                    with col_r:
                        color_map = {"✅ AKTIV": "#00FF00", "⚠️ WARTUNG": "#FF0000"} 
                        fig = px.scatter_mapbox(
                            final, lat="lat", lon="lon", hover_name="Standort",
                            hover_data={"lat": False, "lon": False, "size": False, "Status": True, "Ausstattung_Info": True},
                            color="Status", color_discrete_map=color_map, size="size", size_max=18, zoom=11, height=600,
                            labels={"Ausstattung_Info": "Ausstattung"}
                        )
                        fig.update_layout(
                            mapbox_style="open-street-map", 
                            margin={"r":0,"t":0,"l":0,"b":0},
                            mapbox_center={"lat": slat, "lon": slon}
                        )
                        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
                else: st.warning("Keine Spots im Umkreis gefunden.")
            else: st.info("Noch keine Spielplätze in der Datenbank.")
        else: st.error("Adresse konnte nicht gefunden werden.")

def show_proposal_area():
    """Bereich zum Vorschlagen neuer Spots per smarter Adresssuche"""
    st.subheader("💡 Neuen Spot vorschlagen")
    
    st.markdown("""
    Da Handy-GPS oft blockiert wird, nutzen wir unsere **automatische Standorterkennung**. 
    Gib einfach Name und Adresse ein – unser System erledigt den Rest!
    """)

    with st.form("v_form", clear_on_submit=True):
        v_n = st.text_input("Name des Spielplatzes*", placeholder="z.B. Piratenschiff im Stadtpark")
        v_s = st.text_input("Straße & Hausnummer*", placeholder="z.B. Am Spielplatz 5")
        v_st = st.text_input("Stadt*", value="Varel")
        v_p = st.text_input("PLZ (optional)")
        v_bund = st.selectbox("Bundesland*", ["Niedersachsen", "Bremen", "Hamburg", "Schleswig-Holstein", "Nordrhein-Westfalen"])
        v_alt = st.selectbox("Altersgruppe", ["0-3", "3-12", "Alle"])
        
        st.write("---")
        st.write("**Zusatzinfos:**")
        ausst_list = st.multiselect("Ausstattung", ["Rutsche", "Schaukel", "Seilbahn", "Klettergerüst", "Sandkasten", "Wippe", "Karussell"])
        
        c1, c2, c3 = st.columns(3)
        v_schatten = c1.checkbox("🌳 Schatten")
        v_sitze = c2.checkbox("🪑 Sitzplätze")
        v_wc = c3.checkbox("🚽 Toilette")
        
        st.write("---")
        v_img = st.file_uploader("Foto hochladen (optional)", type=["jpg", "png", "jpeg"])
        ds = st.checkbox("Keine Personen auf dem Foto erkennbar*")
        
        if st.form_submit_button("Spot jetzt einsenden", use_container_width=True):
            if v_n and v_s and v_st and ds:
                # Geocoding: Adresse in Koordinaten umwandeln
                gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                res = gc.geocode(f"{v_s}, {v_st}, Deutschland")
                
                if res:
                    f_lat = res[0]['geometry']['lat']
                    f_lon = res[0]['geometry']['lng']
                    
                    # Doubletten-Check (Verhindert doppelte Einträge im Umkreis von 100m)
                    existierende = hole_df("spielplaetze")
                    is_double = False
                    if not existierende.empty:
                        for _, ex in existierende.iterrows():
                            if distanz(f_lat, f_lon, float(ex['lat']), float(ex['lon'])) < 0.1:
                                is_double = True
                                break
                    
                    if is_double:
                        st.error("🚨 An dieser Stelle existiert bereits ein Spielplatz!")
                    else:
                        bild_data = optimiere_bild(v_img)
                        ausst_str = ", ".join(ausst_list)
                        
                        if sende_vorschlag(
                            v_n, v_s, v_alt, st.session_state.user, v_bund, v_p or "00000", v_st, 
                            bild_data, 1, ausst_str, 
                            1 if v_schatten else 0, 1 if v_sitze else 0, 1 if v_wc else 0, 
                            f_lat, f_lon
                        ):
                            st.success(f"Klasse! '{v_n}' wurde erfolgreich lokalisiert und zur Prüfung gespeichert.")
                else:
                    st.error("Die Adresse wurde nicht gefunden. Bitte prüfe die Schreibweise!")
            else:
                st.warning("Bitte fülle alle Pflichtfelder (*) aus!")

def show_profile_area():
    """Das Profil-Dashboard mit allen Tabs"""
    st.title("Mein Bereich")
    sub_tabs = st.tabs(["⚙️ Profil-Daten", "📍 Suche", "💡 Vorschlag", "🔒 Wuselfunk", "👥 Freunde"])
    
    with sub_tabs[0]:
        df_u = hole_df("nutzer")
        u_data = df_u[df_u['benutzername'] == st.session_state.user].iloc[0]
        
        emo_liste = ["🧗", "🤸", "🦁", "🚀", "🌈", "🎈"]
        aktuelles_emo = u_data.get('profil_emoji', "🧗")
        emo_index = emo_liste.index(aktuelles_emo) if aktuelles_emo in emo_liste else 0
        
        with st.form("p_data"):
            st.markdown(f"### Hallo {st.session_state.user}!")
            ne = st.text_input("E-Mail", value=u_data['email'])
            nv = st.text_input("Vorname", value=u_data['vorname'])
            nn = st.text_input("Nachname", value=u_data['nachname'])
            na = st.number_input("Alter (Jahre)", value=int(u_data['alter_jahre']))
            emo = st.selectbox("Dein Profil-Emoji", emo_liste, index=emo_index)
            
            if st.form_submit_button("Änderungen speichern"):
                if aktualisiere_profil(st.session_state.user, ne, nv, nn, na, emo):
                    st.success("Daten aktualisiert!"); st.rerun()
                else:
                    st.error("Fehler beim Speichern.")
                
    with sub_tabs[1]: show_user_area()
    with sub_tabs[2]: show_proposal_area()
    with sub_tabs[3]: show_wuselfunk()
    with sub_tabs[4]: show_wusel_crew()

def show_feedback_area():
    """Feedback-Funktion für Nutzer"""
    st.title("💬 Feedback")
    st.write("Hast du Wünsche oder Probleme? Schreib uns!")
    with st.form("f_form"):
        msg = st.text_area("Deine Nachricht an das WuselMap-Team...")
        if st.form_submit_button("Feedback absenden"):
            if msg:
                if sende_feedback(st.session_state.user, msg):
                    st.success("Vielen Dank für deine Nachricht!"); st.rerun()
            else:
                st.warning("Bitte gib eine Nachricht ein.")