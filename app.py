import streamlit as st
import pandas as pd
import plotly.express as px
from opencage.geocoder import OpenCageGeocode
import numpy as np
import os
from database_manager import *

# --- SETUP & DESIGN ---
st.set_page_config(page_title="KletterKompass Deutschland", layout="wide")

st.markdown("""
    <style>
    h1, h2, h3, label { color: #2e7d32 !important; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; font-weight: bold; width: 100%; border: none; }
    .stButton>button:hover { background-color: #1b5e20; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>textarea { 
        background-color: #ffffff !important; border: 2px solid #2e7d32 !important; color: #000000 !important; 
    }
    [data-testid="stSidebar"] { background-color: #000000 !important; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label { color: #ffffff !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; color: white; border-radius: 5px; margin-right: 5px; }
    .stTabs [aria-selected="true"] { background-color: #2e7d32 !important; }
    </style>
    """, unsafe_allow_html=True)

def distanz(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2-lat1), np.radians(lon2-lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = 'guest'
if 'wahl' not in st.session_state: st.session_state.wahl = "📍 Suche"

# --- SIDEBAR ---
with st.sidebar:
    logo_path = "assets/Kletterkompass_Logo.png"
    if os.path.exists(logo_path): st.image(logo_path, width=180)
    st.write("---")
    
    if not st.session_state.logged_in:
        t_log, t_reg = st.tabs(["🔐 Login", "📝 Registrieren"])
        with t_log:
            u = st.text_input("Nutzername", key="l_u")
            p = st.text_input("Passwort", type="password", key="l_p")
            if st.button("Anmelden"):
                df_n = hole_df("nutzer")
                if not df_n.empty:
                    user_match = df_n[(df_n['benutzername'] == u) & (df_n['passwort'] == hash_passwort(p))]
                    if not user_match.empty:
                        st.session_state.logged_in = True; st.session_state.user = u
                        st.session_state.user_role = user_match.iloc[0]['rolle']
                        st.rerun()
                    else: st.error("Login falsch.")
        with t_reg:
            nu = st.text_input("Nutzername*", key="r_u")
            npw = st.text_input("Passwort*", type="password", key="r_p")
            ne = st.text_input("E-Mail*", key="r_e")
            nv, nn = st.text_input("Vorname"), st.text_input("Nachname")
            na = st.number_input("Alter", 0, 100, 25)
            agb = st.checkbox("AGB akzeptieren*")
            if st.button("Erstellen"):
                if nu and npw and ne and agb:
                    if registriere_nutzer(nu, npw, ne, nv, nn, na, agb): st.success("Konto bereit!")
                    else: st.error("Fehler.")
    else:
        st.success(f"Moin {st.session_state.user}!")
        if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

    st.write("---")
    if st.button("📍 Spielplatz suchen"): st.session_state.wahl = "📍 Suche"
    
    # ADMIN BUTTON (Nur sichtbar für Admins)
    if st.session_state.logged_in and st.session_state.user_role == 'admin':
        if st.button("🛠️ Admin-Bereich"): st.session_state.wahl = "🛠️ Admin"
    
    if st.button("📄 Rechtliches"): st.session_state.wahl = "📄 Recht"

# --- HAUPTBEREICH: SUCHE ---
if st.session_state.wahl == "📍 Suche":
    banner_path = "assets/Kletterkompass.png"
    if os.path.exists(banner_path): st.image(banner_path, use_container_width=True)
    st.title("Spielplätze finden")
    
    c1, c2 = st.columns([3, 1])
    with c1: adr = st.text_input("Ort", "Varel")
    with c2: km = st.slider("Radius", 1, 100, 20)
    
    if st.button("🔍 Suchen", type="primary"):
        gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
        res = gc.geocode(adr + ", Deutschland")
        if res:
            slat, slon = res[0]['geometry']['lat'], res[0]['geometry']['lng']
            df = hole_df("spielplaetze")
            if not df.empty:
                df['lat'] = pd.to_numeric(df['lat'], errors='coerce'); df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
                df = df.dropna(subset=['lat', 'lon'])
                df['distanz'] = df.apply(lambda r: distanz(slat, slon, r['lat'], r['lon']), axis=1)
                final = df[df['distanz'] <= km].sort_values('distanz')
                
                if not final.empty:
                    col_l, col_r = st.columns([1, 1.5])
                    with col_l:
                        for i, r in final.iterrows():
                            with st.expander(f"📍 {r['Standort']} ({round(r['distanz'], 1)} km)"):
                                st.write(f"Alter: {r['altersfreigabe']}")
                    with col_r:
                        fig = px.scatter_mapbox(final, lat="lat", lon="lon", hover_name="Standort", zoom=10, height=500)
                        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0}, mapbox_center={"lat": slat, "lon": slon})
                        st.plotly_chart(fig, use_container_width=True)

    # USER-FEEDBACK FORMULAR (Für alle eingeloggten User)
    if st.session_state.logged_in:
        st.write("---")
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            with st.expander("💡 Neuen Spielplatz vorschlagen"):
                with st.form("vorschlag"):
                    v_n = st.text_input("Name")
                    v_a = st.text_input("Adresse")
                    v_alt = st.selectbox("Alter", ["0-3", "3-12", "Alle"])
                    if st.form_submit_button("Vorschlag senden"):
                        sende_vorschlag(v_n, v_a, v_alt, st.session_state.user)
                        st.success("Danke! Der Admin prüft das.")
        with c_f2:
            with st.expander("💬 Feedback zur App"):
                with st.form("feedback"):
                    msg = st.text_area("Deine Nachricht an uns")
                    if st.form_submit_button("Senden"):
                        sende_feedback(st.session_state.user, msg)
                        st.success("Feedback gesendet!")

# --- ADMIN BEREICH ---
elif st.session_state.wahl == "🛠️ Admin":
    st.title("Admin-Cockpit")
    
    t1, t2, t3, t4 = st.tabs(["📥 Vorschläge", "👥 Nutzer", "💬 Feedback", "🏗️ Neu anlegen"])
    
    with t1:
        st.subheader("Neue Spielplatz-Vorschläge")
        df_v = hole_df("vorschlaege")
        if not df_v.empty: st.table(df_v)
        else: st.write("Keine neuen Vorschläge.")

    with t2:
        st.subheader("Registrierte Mitglieder")
        df_u = hole_df("nutzer")
        if not df_u.empty: 
            st.dataframe(df_u[['id', 'benutzername', 'email', 'vorname', 'nachname', 'alter_jahre', 'rolle']])
        
    with t3:
        st.subheader("Nutzer-Feedback")
        df_f = hole_df("feedback")
        if not df_f.empty: st.table(df_f)
        else: st.write("Noch kein Feedback erhalten.")

    with t4:
        st.subheader("Spot händisch hinzufügen")
        with st.form("admin_add"):
            n, a = st.text_input("Name"), st.text_input("Adresse")
            if st.form_submit_button("Speichern"):
                gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                r = gc.geocode(a + ", Deutschland")
                if r and speichere_spielplatz(n, r[0]['geometry']['lat'], r[0]['geometry']['lng'], "Alle"):
                    st.success("Gespeichert!"); st.rerun()

elif st.session_state.wahl == "📄 Recht":
    st.title("Rechtliches")
    st.write("Impressum & Datenschutz")
