import streamlit as st

def show_legal_page():
    st.title("📄 Rechtliche Informationen")
    
    tab1, tab2 = st.tabs(["AGB", "Datenschutz"])
    
    with tab1:
        st.header("Allgemeine Geschäftsbedingungen")
        st.markdown("""
        1. **Nutzung:** Der KletterKompass dient der Information über öffentliche Spielplätze.
        2. **Inhalte:** Alle Angaben (Standorte, Auslastung) sind ohne Gewähr.
        3. **Account:** Du bist für die Sicherheit deines Passworts selbst verantwortlich.
        """)
        
    with tab2:
        st.header("Datenschutzerklärung")
        st.markdown("""
        **Datenverarbeitung:** Wir speichern deinen Nutzernamen und deine E-Mail bei unserem Partner Aiven (MySQL). 
        Diese Daten werden niemals an Dritte weitergegeben.
        
        **Cookies:** Wir nutzen nur technisch notwendige Cookies von Streamlit.
        """)
    
    if st.button("⬅️ Zurück zur Suche"):
        st.session_state.wahl = "📍 Suche"
        st.rerun()
