import streamlit as st

def show_legal_page():
    st.title("📄 Rechtliche Hinweise")
    
    # Tabs für bessere Übersicht
    tab1, tab2 = st.tabs(["Allgemeine Geschäftsbedingungen", "Datenschutzerklärung"])
    
    with tab1:
        st.header("Allgemeine Geschäftsbedingungen (AGB)")
        st.markdown("""
        **1. Geltungsbereich** Diese AGB gelten für die Nutzung der App *KletterKompass*.
        
        **2. Leistungen** Die App dient der Information über Spielplätze. Alle Angaben sind ohne Gewähr.
        
        **3. Registrierung** Mit der Registrierung erklärt sich der Nutzer bereit, seine Daten für die App-Funktionen (Bewertungen etc.) zur Verfügung zu stellen.
        """)
        
    with tab2:
        st.header("Datenschutzerklärung")
        st.markdown("""
        **Verantwortlicher:** [Dein Name/Projektname]  
        **Daten:** Wir speichern Nutzername, E-Mail und Namen in einer MySQL-Datenbank (Aiven).  
        **Zweck:** Bereitstellung der Community-Funktionen.  
        **Rechte:** Du hast jederzeit das Recht auf Auskunft und Löschung deiner Daten.
        """)
    
    if st.button("⬅️ Zurück zur Suche"):
        st.session_state.wahl = "📍 Suche"
        st.rerun()
