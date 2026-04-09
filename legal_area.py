import streamlit as st  # <-- Das hat gefehlt!

def show_legal_area():
    st.title("📄 Rechtliches & Sicherheit")
    legal_tabs = st.tabs(["⚖️ Impressum", "🔒 Datenschutz", "🛡️ Nutzungshinweise"])
    
    with legal_tabs[0]: 
        st.subheader("Impressum")
        st.write("**Betreiber der Webseite:**")
        st.write("""
        Christian Wolff  
        Büppeler Weg 18  
        26316 Varel  
        """)
        st.write("**Kontakt:**")
        st.write("E-Mail: info@wuselmap.de")
        st.write("Internet: www.wuselmap.de")
        st.divider()
        st.caption("Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV: Christian Wolff")

    with legal_tabs[1]: 
        st.subheader("Datenschutzerklärung")
        st.write("""
        **1. Datenverarbeitung:** Wir erheben und speichern Daten, die zur Nutzung der App notwendig sind (Benutzername, E-Mail, Vorname, Nachname, Alter). 
        Passwörter werden ausschließlich als kryptografische Hash-Werte gespeichert und sind für uns nicht im Klartext lesbar.

        **2. Fotos & Standorte:** Beim Hochladen von Fotos für Spielplatz-Vorschläge bestätigt der Nutzer, dass keine Personen auf den Bildern erkennbar sind. 
        Die Standortdaten dienen lediglich der Kartendarstellung.

        **3. Rechte der Nutzer:** Du hast jederzeit das Recht auf Auskunft, Korrektur oder Löschung deiner gespeicherten Daten. Kontaktiere uns dazu einfach per E-Mail.
        """)

    with legal_tabs[2]: 
        st.subheader("Haftung & Jugendschutz")
        st.warning("**Wichtiger Hinweis zur Sicherheit:**")
        st.write("""
        Die WuselMap ist eine Informationsplattform. Die Nutzung der hier gelisteten Spielplätze und Kletter-Spots erfolgt **ausdrücklich auf eigene Gefahr**. 
        
        * **Aufsichtspflicht:** Eltern haften für ihre Kinder. Die App ersetzt nicht die Aufsichtspflicht der Erziehungsberechtigten.
        * **Aktualität:** Wir bemühen uns um korrekte Daten, übernehmen aber keine Gewähr für die aktuelle Beschaffenheit oder Sicherheit der vor Ort befindlichen Geräte.
        * **Meldepflicht:** Sollte ein Spot beschädigt oder gefährlich sein, bitten wir um eine kurze Nachricht über die Feedback-Funktion.
        """)
