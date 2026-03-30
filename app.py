import streamlit as st
import pandas as pd
from database_manager import hole_daten, neue_zeile_schreiben, hash_passwort
import uuid

# --- 1. SEITEN-EINSTELLUNGEN & PITCH BILDER ---
st.set_page_config(page_title="Kletterkompass", page_icon="🧗", layout="centered")

# --- 2. BANNER / LOGO (Hauptbereich) ---
# HIER BITTE DEINEN DATEINAMEN FÜR DAS BANNER EINTRAGEN (z.B. "banner.jpg")
try:
    st.image("dein_banner_bild.png", use_column_width=True) # <-- BITTE ANPASSEN!
except:
    st.title("🧗 Kletterkompass") # Notfall-Text falls Datei nicht gefunden wird

st.markdown("### Dein Wegweiser zu den besten Spots in Varel & Umgebung")

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""

# --- 4. SIDEBAR (Login & Registrierung) ---

# HIER BITTE DEINEN DATEINAMEN FÜR DAS LOGO-SYMBOL EINTRAGEN (z.B. "logo.png")
try:
    st.sidebar.image("dein_logo_symbol.png", width=100) # <-- BITTE ANPASSEN!
except:
    st.sidebar.header("Kletterkompass") # Notfall-Text

st.sidebar.header("Benutzerbereich")

if not st.session_state.logged_in:
    with st.sidebar.expander("🔐 Login", expanded=True):
        u = st.text_input("Nutzername", key="login_u")
        p = st.text_input("Passwort", type="password", key="login_p")
        if st.button("Einloggen"):
            df_n = hole_daten("nutzer")
            if not df_n.empty:
                # Wir suchen nach dem Nutzer und dem gehashten Passwort
                user = df_n[(df_n['benutzername'] == u) & (df_n['passwort'] == hash_passwort(p))]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = u
                    st.rerun()
                else:
                    st.sidebar.error("Daten falsch.")

    with st.sidebar.expander("📝 Neu hier? Registrieren"):
        new_u = st.text_input("Wunsch-Nutzername")
        new_p = st.text_input("Passwort wählen", type="password")
        new_e = st.text_input("E-Mail Adresse")
        if st.button("Konto erstellen"):
            neuer_nutzer = {
                "nutzer_id": str(uuid.uuid4())[:8],
                "benutzername": new_u,
                "passwort": hash_passwort(new_p), # Passwort wird hier verschlüsselt!
                "email": new_e,
                "rolle": "user",
                "avatar_emoji": "🧗"
            }
            neue_zeile_schreiben("nutzer", neuer_nutzer)
            st.sidebar.success("Konto bereit! Log dich oben ein.")
else:
    st.sidebar.success(f"Hallo {st.session_state.user_name}!")
    if st.sidebar.button("Abmelden"):
        st.session_state.logged_in = False
        st.rerun()

# --- 5. SUCHE & KARTE (Das Herzstück) ---
st.divider()
suche = st.text_input("🔍 Spielplatz oder Park suchen...", placeholder="z.B. Hafen oder Dangast")

try:
    df = hole_daten("spielplaetze")
    
    if not df.empty:
        # Filter-Logik
        if suche:
            # Wir suchen im Spaltennamen 'Standort'
            df_gefiltert = df[df['Standort'].str.contains(suche, case=False, na=False)]
        else:
            df_gefiltert = df

        # Karte (Umbenennung für Streamlit von Lon zu lon)
        # 'lat' ist ja schon klein bei dir in der Tabelle!
        map_df = df_gefiltert.rename(columns={'Lon': 'lon'}) 
        st.map(map_df)

        # Trefferliste
        st.write(f"Gefundene Spots: {len(df_gefiltert)}")
        for i, row in df_gefiltert.iterrows():
            with st.expander(f"📍 {row['Standort']}"):
                st.write(f"ID: {row['Spiel ID']}")
                # Platzhalter für Details-Button (Funktion kommt später)
                st.button(f"Details ansehen", key=f"btn_{i}")
    else:
        st.info("Noch keine Daten in der Google Tabelle.")

except Exception as e:
    st.error(f"Datenbank-Verbindung wird geprüft... {e}")

# --- 6. VORSCHLÄGE (Nur für eingeloggte User) ---
if st.session_state.logged_in:
    st.divider()
    st.subheader("💡 Neuen Spot vorschlagen")
    with st.form("vorschlag"):
        n_name = st.text_input("Name des Ortes")
        n_adr = st.text_input("Adresse")
        if st.form_submit_button("Vorschlag senden"):
            v_daten = {
                "v_id": str(uuid.uuid4())[:8], 
                "platz_name": n_name, 
                "adresse": n_adr, 
                "status": "neu"
            }
            neue_zeile_schreiben("vorschlaege", v_daten)
            st.balloons()
            st.success("Gesendet! Wir prüfen deinen Vorschlag.")
