import streamlit as st
from database_manager import hole_df, get_db_connection, sende_feedback
from user_profile import show_profile_section
from user_proposal import show_proposal_section
from legal_area import show_legal_area 
from messaging import show_wuselfunk, show_wusel_crew

# Konstante für die Regeln
AKTUELL_AGB_VERSION = 2 

def check_agb_consent():
    """Sperrt die App, wenn die AGB nicht akzeptiert wurden"""
    df_u = hole_df("nutzer")
    user_row = df_u[df_u['benutzername'] == st.session_state.user]
    
    if user_row.empty:
        st.error("Nutzer nicht gefunden.")
        st.stop()
        
    u_data = user_row.iloc[0]
    
    if u_data.get('agb_version', 0) < AKTUELL_AGB_VERSION:
        st.warning("### 📢 Neue Regeln & Datenschutz")
        with st.expander("📄 Bestimmungen lesen"):
            show_legal_area()

        c1 = st.checkbox("Ich akzeptiere AGB, Datenschutz und Jugendschutz.")
        c2 = st.checkbox("Ich bestätige: Keine Personen auf meinen Fotos.")

        if st.button("Bestätigen & WuselMap öffnen"):
            if c1 and c2:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE nutzer SET agb_version = %s WHERE benutzername = %s", 
                               (AKTUELL_AGB_VERSION, st.session_state.user))
                conn.commit()
                conn.close()
                st.rerun()
            else:
                st.error("Bitte beide Haken setzen.")
        st.stop()

def show_profile_area():
    check_agb_consent()
    
    # --- PERSONALISIERUNG DER ÜBERSCHRIFT ---
    df_n = hole_df("nutzer")
    user_row = df_n[df_n['benutzername'] == st.session_state.user]
    
    # Standardwerte, falls nichts in der DB steht
    titel_text = "Mein Bereich"
    mein_emoji = "👤"
    
    if not user_row.empty:
        u_data = user_row.iloc[0]
        # Emoji laden
        mein_emoji = u_data.get('profil_emoji') or "👤"
        
        # Vornamen-Logik für den Titel
        vn = u_data.get('vorname')
        if vn and str(vn).strip():
            vn = vn.strip()
            # Grammatik-Check für s, x, z am Ende
            if vn.lower().endswith(('s', 'x', 'z')):
                titel_text = f"{vn}' Bereich"
            else:
                titel_text = f"{vn}s Bereich"

    # Jetzt wird der Titel dynamisch angezeigt
    st.title(f"{mein_emoji} {titel_text}")
    
    # Tabs für die verschiedenen Unterbereiche
    tabs = st.tabs(["⚙️ Profil", "💡 Vorschlag", "🔒 Wuselfunk", "👥 Wusel-Crew"])
    
    with tabs[0]: 
        show_profile_section() 
        
    with tabs[1]: 
        show_proposal_section() 
        
    with tabs[2]: 
        show_wuselfunk() 
        
    with tabs[3]: 
        show_wusel_crew()

def show_feedback_area():
    st.title("💬 Feedback")
    with st.form("f_form"):
        msg = st.text_area("Deine Nachricht an uns...")
        if st.form_submit_button("Feedback absenden"):
            if msg:
                if sende_feedback(st.session_state.user, msg):
                    st.success("Vielen Dank!"); st.rerun()
            else:
                st.warning("Bitte gib eine Nachricht ein.")