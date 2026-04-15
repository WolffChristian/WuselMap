import streamlit as st
from database_manager import hole_df, get_db_connection, sende_feedback
# Importe bleiben, aber wir nutzen sie nur dort, wo sie nicht doppelt sind
from user_profile import show_profile_section
from legal_area import show_legal_area 
from messaging import show_wuselfunk, show_wusel_crew
from user_proposal import show_proposal_section # Falls Vorschlag im Profil bleiben soll

# Konstante für die Regeln
AKTUELL_AGB_VERSION = 2 

def check_agb_consent():
    """Sperrt die App, wenn die AGB nicht akzeptiert wurden"""
    df_u = hole_df("nutzer")
    # Sicherheitscheck: Existiert der Nutzer im DF?
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
    st.title("👤 Mein Bereich")
    
    # 🚨 HIER WAR DER FEHLER: Suche wurde entfernt, da sie jetzt ein Haupt-Tab ist!
    # Ich habe "Wuselfunk" und "Freunde" gelassen, falls du die im Profil willst.
    tabs = st.tabs(["⚙️ Profil", "💡 Vorschlag einsenden", "👥 Wusel-Crew"])
    
    with tabs[0]: 
        show_profile_section()
        
    with tabs[1]: 
        # Vorschlag bleibt hier drin, da er (noch) kein Haupt-Tab ist
        show_proposal_section()
        
    with tabs[2]: 
        # Hier zeigen wir die Freunde / Crew
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
