import streamlit as st
from database_manager import hole_df, get_db_connection, sende_feedback
from user_map import show_map_section
from user_proposal import show_proposal_section
from user_profile import show_profile_section
from legal_area import show_legal_area # Nutzt deine bestehende legal_area.py
from messaging import show_wuselfunk, show_wusel_crew

# Konstante für die Regeln
AKTUELL_AGB_VERSION = 2 

def check_agb_consent():
    """Sperrt die App, wenn die AGB nicht akzeptiert wurden"""
    df_u = hole_df("nutzer")
    u_data = df_u[df_u['benutzername'] == st.session_state.user].iloc[0]
    
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

def show_user_area():
    check_agb_consent()
    show_map_section()

def show_proposal_area():
    check_agb_consent()
    show_proposal_section()

def show_profile_area():
    st.title("Mein Bereich")
    tabs = st.tabs(["⚙️ Profil", "📍 Suche", "💡 Vorschlag", "🔒 Wuselfunk", "👥 Freunde"])
    
    with tabs[0]: show_profile_section()
    with tabs[2]: show_proposal_section()
    with tabs[3]: show_wuselfunk()
    with tabs[4]: show_wusel_crew()

def show_feedback_area():
    st.title("💬 Feedback")
    with st.form("f_form"):
        msg = st.text_area("Deine Nachricht an uns...")
        if st.form_submit_button("Feedback absenden"):
            if msg and sende_feedback(st.session_state.user, msg):
                st.success("Vielen Dank!"); st.rerun()
