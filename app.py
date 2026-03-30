import streamlit as st
import pandas as pd
from database_manager import hole_daten, neue_zeile_schreiben, hash_passwort
import uuid
from datetime import datetime

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="Kletterkompass - Dein Spot-Finder",
    page_icon="🧗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. DEIN ORIGINAL DESIGN (CSS) ---
# Hier holen wir die grüne Schrift und das Styling zurück!
st.markdown("""
    <style>
    /* Haupt-Schriftart und Hintergrund */
    .main {
        background-color: #f9f9f9;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Die GRÜNE SCHRIFT für Titel */
    h1, h2, h3, .stSubheader {
        color: #2e7d32 !important; /* Dein Kletterkompass-Grün */
        font-weight: 700;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #ffffff;
        border-right: 1px solid #eeeeee;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #1b5e20;
        transform: translateY(-2px);
    }
    
    /* Karten-Container */
    .stMap {
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""

# --- 4. SIDEBAR (Original Anordnung) ---
# Hier laden wir DEINE BILDER aus GitHub!
st.sidebar.image("logo.png", width=150) # <-- Stell sicher, dass die Datei so heißt!
st.sidebar.title("🧗 Kletterkompass")

if not st.session_state.logged_in:
    st.sidebar.subheader("Login / Registrierung")
    login_tab, reg_tab = st.sidebar.tabs(["🔐 Login", "📝 Registrieren"])
    
    with login_tab:
        u = st.text_input("Nutzername", key="login_u")
        p = st.text_input("Passwort", type="password", key="login_p")
        if st.button("Einloggen"):
            df_n = hole_daten("nutzer")
            if not df_n.empty:
                user = df_n[(df_n['benutzername'] == u) & (df_n['passwort'] == hash_passwort(p))]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = u
                    st.rerun()
                else:
                    st.error("Daten falsch.")
                    
    with reg_tab:
        new_u = st.text_input("Wunsch-Nutzername")
        new_p = st.text_input("Passwort", type="password")
        new_e = st.text_input("E-Mail")
        if st.button("Konto erstellen"):
            neuer_nutzer = {
                "nutzer_id": str(uuid.uuid4())[:8],
                "benutzername": new_u,
                "passwort": hash_passwort(new_p),
                "email": new_e,
                "rolle": "user",
                "avatar_emoji": "🧗"
            }
            neue_zeile_schreiben("nutzer", neuer_nutzer)
            st.success("Konto erstellt! Bitte einloggen.")
else:
    st.sidebar.success(f"Eingeloggt als: {st.session_state.user_name}")
    if st.sidebar.button("Abmelden"):
        st.session_state.logged_in = False
        st.rerun()

# --- 5. HAUPTBEREICH (Original Anordnung) ---

# DEIN BANNER-BILD
st.image("banner.jpg", use_column_width=True) # <-- Stell sicher, dass die Datei so heißt!

st.title("Finde deinen nächsten Spot")
st.markdown("Dein Wegweiser zu den besten Kletter- und Spielplätzen in Varel & Umgebung.")

# DIE SUCHE (Original Position)
st.divider()
col1, col2 = st.columns([3, 1])
with col1:
    suche = st.text_input("🔍 Spot suchen...", placeholder="z.B. Hafen oder Dangast")

# DIE KARTE & DATEN LADEN
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
        map_df = df_gefiltert.rename(columns={'Lon': 'lon'}) 
        st.map(map_df)

        # Trefferliste (Original Design)
        st.subheader(f"Gefundene Spots ({len(df_gefiltert)})")
        for i, row in df_gefiltert.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([1, 2, 1])
                # Platzhalter für Spot-Bild (Funktion kommt später)
                c1.image("https://via.placeholder.com/150", width=100) 
                c2.markdown(f"### {row['Standort']}")
                c2.write(f"ID: {row['Spiel ID']}")
                if c3.button("Details", key=f"details_{i}"):
                    st.info(f"Details für {row['Standort']} folgen...")
                st.divider()
    else:
        st.info("Noch keine Daten in der Google Tabelle.")

except Exception as e:
    st.error(f"Datenbank-Verbindung wird geprüft... {e}")

# --- 6. VORSCHLÄGE & PITCH (Ganz unten, Original Design) ---
if st.session_state.logged_in:
    st.divider()
    st.subheader("💡 Neuen Spot vorschlagen")
    # ... (Original Formular)
    with st.form("vorschlag"):
        n_name = st.text_input("Name des Ortes")
        n_adr = st.text_input("Adresse")
        if st.form_submit_button("Vorschlag senden"):
            v_daten = {"v_id": str(uuid.uuid4())[:8], "platz_name": n_name, "adresse": n_adr, "status": "neu"}
            neue_zeile_schreiben("vorschlaege", v_daten)
            st.balloons()
            st.success("Gesendet!")

# DEIN PITCH-TEXT (Original Position)
st.divider()
st.markdown("""
    ### Warum Kletterkompass?
    *Von Eltern für Eltern.* Wir kennen die Suche nach dem perfekten Spot. 
    Kletterkompass hilft dir, schnell und einfach tolle Orte für deine Kinder zu finden, 
    damit ihr mehr Zeit beim Toben und weniger Zeit beim Suchen verbringt.
""")
