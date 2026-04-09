import streamlit as st

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

        **3. Rechte der Nutzer:** Du hast jederzeit das Recht auf Auskunft, Korrektur oder Löschung deiner gespeicherten Daten.
        """)

    with legal_tabs[2]: 
        st.subheader("Haftung & Wartung")
        st.warning("**Wichtiger Hinweis zur Verantwortlichkeit:**")
        st.write("""
        Die WuselMap ist eine reine **Informationsplattform**. 
        
        * **Kein Wartungsdienst:** Der Betreiber der App führt **keine Reparaturen, Instandsetzungen oder Sicherheitsprüfungen** an den gelisteten Spots durch. Verantwortlich für den Zustand und die Sicherheit der Geräte sind ausschließlich die jeweiligen Eigentümer (z.B. Kommunen, Städte oder private Betreiber).
        
        * **Nutzung auf eigene Gefahr:** Die Nutzung der Spots erfolgt ausdrücklich auf eigene Gefahr. Eine Haftung für Unfälle oder Schäden wird ausgeschlossen.
        
        * **Aufsichtspflicht:** Eltern haften für ihre Kinder. Die App ersetzt nicht die Aufsichtspflicht der Erziehungsberechtigten.
        
        * **Warnsystem:** Sollte ein Spot beschädigt sein, bitten wir um eine Nachricht über die Feedback-Funktion. Diese Information dient lediglich dazu, **andere Nutzer innerhalb der App zu warnen** oder den Spot temporär zu kennzeichnen. Meldungen zur Reparatur müssen von den Nutzern eigenständig an die zuständige Stadtverwaltung gerichtet werden.
        """)
