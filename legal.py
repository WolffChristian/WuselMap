import streamlit as st

def show_legal_page():
    st.title("📄 AGB & Datenschutz")
    st.write("---")
    
    st.header("1. Datenschutz & Fotos")
    st.info("""
    **Besondere Regelung für Bildmaterial:**
    Beim Hochladen von Fotos verpflichtet sich der Nutzer, keine Personen (insbesondere Kinder) erkennbar darzustellen. 
    Fotos dürfen lediglich Spielgeräte, Gelände und öffentliche Parkanlagen zeigen.
    """)
    
    st.header("2. Prüfungsvorbehalt")
    st.write("""
    Alle eingereichten Vorschläge und Fotos werden durch das Admin-Team manuell geprüft. 
    Wir behalten uns vor, Bilder bei Verstößen gegen das Persönlichkeitsrecht oder bei unzureichender Qualität ohne Rücksprache zu löschen.
    """)
    
    st.header("3. Haftung")
    st.write("Die Nutzung der App erfolgt auf eigene Gefahr. Für die Richtigkeit der Standortdaten übernehmen wir keine Gewähr.")
