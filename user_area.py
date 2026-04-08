import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
from database_manager import hole_df, sende_vorschlag, sende_feedback, optimiere_bild, aktualisiere_profil

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

def show_user_area():
    st.subheader("📍 Kletter-Spots in deiner Nähe")
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Wo suchst du?", "Varel")
    with c2: km = st.slider("Umkreis (km)", 1, 100, 20)
    
    if st.button("🔍 Suchen", type="primary"):
        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        res = gc.geocode(adr + ", Deutschland")
        if res:
            slat, slon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
            df = hole_df("spielplaetze")
            if not df.empty:
                df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
                df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
                df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                final = df[df['distanz'] <= km].sort_values('distanz')
                
                if not final.empty:
                    col_l, col_r = st.columns([1, 1.5])
                    with col_l:
                        for i, r in final.iterrows():
                            with st.expander(f"📍 {r['Standort']} ({round(r['distanz'], 1)} km)"):
                                if r.get('bild_data'): 
                                    st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
                                st.write(f"**Ort:** {r['stadt']}")
                    with col_r:
                        fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10, height=500)
                        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0}, mapbox_center={"lat": slat, "lon": slon})
                        st.plotly_chart(fig, use_container_width=True)
                else: st.warning("Keine Spots im Umkreis gefunden.")
        else: st.error("Adresse nicht gefunden.")

def show_proposal_area():
    st.subheader("💡 Spot vorschlagen")
    with st.form("v_form", clear_on_submit=True):
        v_n = st.text_input("Name des Spots*")
        v_s = st.text_input("Straße & Hausnr.*")
        v_p = st.text_input("PLZ*")
        v_st = st.text_input("Stadt*")
        v_alt = st.selectbox("Altersgruppe", ["0-3", "3-12", "Alle"])
        v_img = st.file_uploader("Foto hochladen", type=["jpg", "png", "jpeg"])
        ds = st.checkbox("Keine Personen auf dem Foto erkennbar*")
        
        if st.form_submit_button("Einsenden"):
            if v_n and v_s and v_p and v_st and ds:
                bild_data = optimiere_bild(v_img)
                if sende_vorschlag(v_n, v_s, v_alt, st.session_state.user, "Niedersachsen", v_p, v_st, bild_data, ds):
                    st.success("Erfolg! Spot wird geprüft.")
            else: st.warning("Pflichtfelder (*) ausfüllen!")

def show_profile_area():
    st.title("👤 Mein Bereich")
    sub_tabs = st.tabs(["⚙️ Profil-Daten", "📍 Suche", "💡 Vorschlag"])
    with sub_tabs[0]:
        df_u = hole_df("nutzer")
        user_data = df_u[df_u['benutzername'] == st.session_state.user].iloc[0]
        with st.form("p_data"):
            ne = st.text_input("E-Mail", value=user_data['email'])
            nv = st.text_input("Vorname", value=user_data['vorname'])
            nn = st.text_input("Nachname", value=user_data['nachname'])
            na = st.number_input("Alter", value=int(user_data['alter_jahre']))
            emo = st.selectbox("Profil-Emoji", ["🧗", "🤸", "🦁", "🚀"])
            if st.form_submit_button("Speichern"):
                aktualisiere_profil(st.session_state.user, ne, nv, nn, na, emo)
                st.success("Daten aktualisiert!"); st.rerun()
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.query_params.clear()
            st.session_state.logged_in = False
            st.rerun()
    with sub_tabs[1]: show_user_area()
    with sub_tabs[2]: show_proposal_area()

def show_feedback_area():
    st.title("💬 Feedback")
    with st.form("f_form"):
        msg = st.text_area("Deine Nachricht")
        if st.form_submit_button("Absenden"):
            if msg and sende_feedback(st.session_state.user, msg):
                st.success("Vielen Dank!"); st.rerun()

# --- RECHTS-BEREICH: VOLLSTÄNDIG AUSGEARBEITET ---
def show_legal_area():
    st.title("📄 Rechtliches & Sicherheit")
    legal_tabs = st.tabs(["⚖️ Impressum", "🔒 Datenschutz", "🛡️ Jugendschutz"])
    
    with legal_tabs[0]:
        st.subheader("Impressum")
        st.write("""
        **Verantwortlich für den Inhalt nach § 5 TMG:** Christian Wolff  
        [Deine Straße / Nr.]  
        [Deine PLZ] Varel  
        
        **Kontakt:** E-Mail: [Deine E-Mail Adresse]  
        Telefon: [Deine Telefonnummer, falls gewünscht]  
        
        **Haftungsausschluss:** Trotz sorgfältiger inhaltlicher Kontrolle übernehmen wir keine Haftung für die Inhalte externer Links. Für den Inhalt der verlinkten Seiten sind ausschließlich deren Betreiber verantwortlich.
        """)

    with legal_tabs[1]:
        st.subheader("Datenschutzerklärung (DSGVO)")
        st.info("Ihre Daten sind bei uns sicher. Wir verkaufen keine Daten an Dritte.")
        st.write("""
        **1. Verantwortliche Stelle** Verantwortlich für die Datenverarbeitung in dieser App ist Christian Wolff (Kontaktdaten siehe Impressum).
        
        **2. Erhebung und Speicherung personenbezogener Daten** Bei der Nutzung dieser App werden folgende Daten erhoben:  
        * **Registrierungsdaten:** Benutzername, E-Mail, Name, Alter (zur Bereitstellung des Profils).  
        * **Standortdaten:** Wir nutzen Geodaten über den Dienst *OpenCage*, um Ihnen Kletterspots in der Nähe anzuzeigen. Ihr genauer Standort wird nicht dauerhaft gespeichert.  
        * **Inhalte:** Von Ihnen hochgeladene Fotos von Spots werden in unserer Datenbank (TiDB Cloud) gespeichert.
        
        **3. Zweck der Verarbeitung** Die Verarbeitung erfolgt gemäß Art. 6 Abs. 1 lit. b DSGVO zur Erfüllung des Nutzungsvertrags (Bereitstellung der App-Funktionen).
        
        **4. Rechte der Nutzer** Sie haben das Recht auf Auskunft (Art. 15 DSGVO), Berichtigung (Art. 16), Löschung (Art. 17) und Datenübertragbarkeit (Art. 20). Kontaktieren Sie uns hierzu einfach per E-Mail.
        
        **5. Datensicherheit** Unsere Datenbank ist verschlüsselt und der Zugriff ist auf den Administrator beschränkt. Fotos werden vor der Speicherung optimiert und anonymisiert.
        """)

    with legal_tabs[2]:
        st.subheader("🛡️ Jugend- und Medienschutz")
        st.warning("Wichtiger Hinweis für Eltern und Jugendliche")
        st.write("""
        **1. Schutz von Minderjährigen (JuSchG & JMStV)** Die Sicherheit von Kindern steht bei KletterKompass an oberster Stelle. Wir halten uns strikt an die Vorgaben des Jugendschutzgesetzes.
        
        **2. Altersfreigaben** Diese App dient der Information über öffentliche Plätze. Wir erfassen das Alter der Nutzer, um sicherzustellen, dass jugendschutzrelevante Inhalte (z.B. Feedback-Funktionen) verantwortungsvoll genutzt werden.
        
        **3. Bildrechte & Schutz der Privatsphäre** Beim Hochladen von Spot-Vorschlägen gilt: **Es dürfen keine Personen, insbesondere keine Kinder, auf den Fotos erkennbar sein.** Verstöße gegen diese Regel führen zur sofortigen Löschung des Beitrags und können zum Ausschluss aus der App führen.
        
        **4. Moderation** Alle eingereichten Vorschläge und Feedbacks werden manuell durch den Administrator geprüft, bevor sie für andere Nutzer sichtbar werden. So verhindern wir ungeeignete Inhalte oder unangemessene Sprache.
        
        **5. Ansprechpartner für Jugendschutz** Sollten Sie Inhalte entdecken, die Sie als gefährdend empfinden, melden Sie diese bitte sofort über die Feedback-Funktion oder per E-Mail.
        """)
