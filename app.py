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
    .stTextInput>div>div>input, .stNumberInput>div>div>input { 
        background-color: #ffffff !important; border: 2px solid #2e7d32 !important; color: #000000 !important; 
    }
    [data-testid="stSidebar"] { background-color: #000000 !important; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label { color: #ffffff !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; color: white; border-radius: 5px; margin-right: 5px; }
    .stTabs [aria-selected="true"] { background-color: #2e7d32 !important; }
    /* Profilbild-Zentrierung */
    .avatar-circle { font-size: 80px; text-align: center; margin-bottom: 20px; }
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
if 'forgot_pw' not in st.session_state: st.session_state.forgot_pw = False

# --- SIDEBAR ---
with st.sidebar:
    logo_path = "assets/Kletterkompass_Logo.png"
    if os.path.exists(logo_path): st.image(logo_path, width=180)
    st.write("---")
    
    if not st.session_state.logged_in:
        t_log, t_reg = st.tabs(["🔐 Login", "📝 Registrieren"])
        with t_log:
            if not st.session_state.forgot_pw:
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
                if st.button("🔑 Passwort vergessen?"):
                    st.session_state.forgot_pw = True; st.rerun()
            else:
                res_u, res_m = st.text_input("Nutzername"), st.text_input("E-Mail")
                neu_pw = st.text_input("Neues Passwort", type="password")
                if st.button("Passwort ändern"):
                    if check_user_mail_match(res_u, res_m) and update_passwort(res_u, neu_pw):
                        st.success("Erledigt!"); st.session_state.forgot_pw = False; st.rerun()
                    else: st.error("Daten falsch.")
                if st.button("Zurück"): st.session_state.forgot_pw = False; st.rerun()
        with t_reg:
            nu, npw, ne = st.text_input("Nutzer*"), st.text_input("PW*", type="password"), st.text_input("Mail*")
            nv, nn, na = st.text_input("Vorname"), st.text_input("Nachname"), st.number_input("Alter", 0, 100, 25)
            agb = st.checkbox("AGB akzeptieren*")
            if st.button("Erstellen"):
                if nu and npw and ne and agb:
                    if registriere_nutzer(nu, npw, ne, nv, nn, na, agb): st.success("Konto bereit!")
                    else: st.error("Fehler.")
    else:
        st.success(f"Moin {st.session_state.user}!")
        if st.button("👤 Mein Profil"): st.session_state.wahl = "👤 Profil"
        if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()

    st.write("---")
    if st.button("📍 Spielplatz suchen"): st.session_state.wahl = "📍 Suche"
    if st.session_state.logged_in and st.session_state.user_role == 'admin':
        if st.button("🛠️ Admin-Bereich"): st.session_state.wahl = "🛠️ Admin"
    if st.button("📄 Rechtliches"): st.session_state.wahl = "📄 Recht"

# --- HAUPTBEREICH: PROFIL ---
if st.session_state.wahl == "👤 Profil":
    st.title("Dein Profil")
    df_u = hole_df("nutzer")
    user_data = df_u[df_u['benutzername'] == st.session_state.user].iloc[0]
    
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        st.markdown(f'<div class="avatar-circle">{user_data.get("profil_emoji", "🧗")}</div>', unsafe_allow_html=True)
        st.subheader("Profilbild wählen")
        neues_emoji = st.selectbox("Wähle dein Emoji", ["🧗", "🏃", "🧗‍♂️", "⛰️", "🤸", "🏀", "⚽", "🌟", "🦁", "🚀"])
    
    with col_p2:
        with st.form("edit_profil"):
            st.subheader("Persönliche Daten")
            e_mail = st.text_input("E-Mail", value=user_data['email'])
            v_name = st.text_input("Vorname", value=user_data['vorname'])
            n_name = st.text_input("Nachname", value=user_data['nachname'])
            alter = st.number_input("Alter", value=int(user_data['alter_jahre']))
            
            if st.form_submit_button("Änderungen speichern"):
                if aktualisiere_profil(st.session_state.user, e_mail, v_name, n_name, alter, neues_emoji):
                    st.success("✅ Profil aktualisiert!")
                    st.rerun()
                else: st.error("Fehler beim Speichern.")

# --- HAUPTBEREICH: SUCHE ---
elif st.session_state.wahl == "📍 Suche":
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

# --- ADMIN BEREICH & RECHT ---
elif st.session_state.wahl == "🛠️ Admin":
    st.title("Admin-Cockpit")
    t1, t2, t3, t4 = st.tabs(["📥 Vorschläge", "👥 Nutzer", "💬 Feedback", "🏗️ Neu anlegen"])
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty: st.table(df_v)
    with t2:
        df_u = hole_df("nutzer")
        if not df_u.empty: st.dataframe(df_u[['id', 'benutzername', 'email', 'vorname', 'nachname', 'rolle']])
    with t3:
        df_f = hole_df("feedback")
        if not df_f.empty: st.table(df_f)
    with t4:
        with st.form("admin_add"):
            n, a = st.text_input("Name"), st.text_input("Adresse")
            if st.form_submit_button("Speichern"):
                gc = OpenCageGeocode(st.secrets["OPENCAGE_KEY"])
                r = gc.geocode(a + ", Deutschland")
                if r and speichere_spielplatz(n, r[0]['geometry']['lat'], r[0]['geometry']['lng'], "Alle"):
                    st.success("Drin!"); st.rerun()

elif st.session_state.wahl == "📄 Recht":
    st.write("Impressum & Datenschutz")
