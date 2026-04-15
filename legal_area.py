import streamlit as st

def show_legal_area():
    st.title("📄 Rechtliches, Sicherheit & Datenschutz")
    
    # Vier Tabs für die volle Übersicht
    legal_tabs = st.tabs(["⚖️ Impressum", "🔒 Datenschutz", "🛡️ Nutzungshinweise", "🧒 Jugendschutz"])
    
    with legal_tabs[0]: 
        st.subheader("Impressum")
        st.write("**Betreiber der WuselMap:**")
        st.write("Christian Wolff")
        st.write("Büppeler Weg 18")
        st.write("26316 Varel")
        
        st.write("**Kontakt:**")
        st.write("E-Mail: info@wuselmap.de")
        st.write("Internet: www.wuselmap.de")
        st.divider()
        
        st.write("### Haftung für Inhalte")
        st.write("Die Inhalte unserer Seiten wurden mit größter Sorgfalt erstellt. Für die **Richtigkeit, Vollständigkeit und Aktualität** der Inhalte können wir jedoch keine Gewähr übernehmen. Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich.")
        
        st.write("### Haftung für Links")
        st.write("Unser Angebot enthält Links zu externen Webseiten Dritter, auf deren Inhalte wir keinen Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich.")
        
        st.caption("Verantwortlich für den Inhalt nach § 5 TMG / § 18 MStV: Christian Wolff")

    with legal_tabs[1]: 
        st.subheader("Datenschutzerklärung (DSGVO)")
        
        st.write("### 1. Allgemeine Hinweise")
        st.write("Diese Erklärung gibt dir einen Überblick darüber, was mit deinen personenbezogenen Daten passiert. **Personenbezogene Daten** sind alle Daten, mit denen du persönlich identifiziert werden kannst. Wir behandeln deine Daten vertraulich und entsprechend der gesetzlichen Datenschutzvorschriften.")

        st.write("### 2. Datenerfassung & Speicherdauer")
        st.write("➡️ **Registrierung:** Wir speichern deinen gewählten Benutzernamen, deine E-Mail-Adresse sowie freiwillige Profilangaben wie Vorname und Alter. Diese Daten werden gelöscht, sobald du deinen Account löschst.")
        st.write("➡️ **Zweck:** Die Verarbeitung erfolgt zur Bereitstellung der App-Funktionen und zur Personalisierung deines Nutzererlebnisses (Art. 6 Abs. 1 lit. b DSGVO).")
        st.write("➡️ **Sicherheit:** Deine Daten werden auf **europäischen Servern** gespeichert. Zur Sicherung deiner Daten verwenden wir moderne Verschlüsselungsverfahren (SSL/TLS) bei der Übertragung.")

        st.write("### 3. Weitergabe an Dritte")
        st.write("Um die Funktionen der WuselMap (Karte, Wetter, Adresssuche) bereitzustellen, nutzen wir folgende Dienste:")
        st.write("➡️ **OpenCage & OpenStreetMap:** Diese Dienste werden genutzt, um Adressen in Koordinaten umzuwandeln und die interaktive Karte anzuzeigen. Dabei wird deine IP-Adresse an deren Server übertragen.")
        st.write("➡️ **Open-Meteo:** Zur Anzeige des aktuellen Wetters werden die Koordinaten des gewählten Spielplatzes anonymisiert an Open-Meteo übertragen.")

        st.write("### 4. Deine Betroffenenrechte")
        st.write("Du hast jederzeit das Recht auf unentgeltliche **Auskunft** über Herkunft, Empfänger und Zweck deiner gespeicherten personenbezogenen Daten. Du hast außerdem ein Recht, die **Berichtigung, Sperrung oder Löschung** dieser Daten zu verlangen.")
        st.write("Zudem steht dir ein **Beschwerderecht** bei der zuständigen Aufsichtsbehörde zu, falls du eine Verletzung deiner Datenschutzrechte vermutest.")

    with legal_tabs[2]: 
        st.subheader("Nutzungs- & Sicherheitshinweise")
        
        st.write("### 1. Ausschluss der Gewährleistung")
        st.write("Die WuselMap ist ein reiner Informationsdienst für Familien. Wir übernehmen keine Garantie für die Existenz, Erreichbarkeit oder den Sicherheitszustand der in der App gelisteten Spielplätze.")

        st.write("### 2. Baulicher Zustand & Unfälle")
        st.write("**Der Betreiber der WuselMap ist nicht für den baulichen Zustand, die Wartung oder die Sicherheit der Spielplätze verantwortlich.**")
        st.write("Zuständig für die Verkehrssicherungspflicht sind ausschließlich die jeweiligen Eigentümer (z.B. Städte, Kommunen oder private Betreiber). Eine Haftung des App-Betreibers für **Körperschäden, Unfälle oder Sachschäden**, die durch die Nutzung der Spielgeräte entstehen, ist ausdrücklich ausgeschlossen.")

        st.write("### 3. Pflichten der Nutzer")
        st.write("➡️ Nutzer verpflichten sich, nur wahrheitsgetreue Angaben zu machen.")
        st.write("➡️ Das Hochladen von rechtswidrigen, beleidigenden oder pornografischen Inhalten ist untersagt.")
        st.write("➡️ Das Urheberrecht für hochgeladene Bilder muss beim Nutzer liegen. Mit dem Upload räumst du dem Betreiber ein einfaches Nutzungsrecht zur Darstellung innerhalb der App ein.")

        st.write("### 4. Hausrecht & Sperrung")
        st.write("Der Betreiber behält sich vor, Beiträge ohne Angabe von Gründen zu **löschen** oder Nutzer bei wiederholten Verstößen gegen diese Regeln dauerhaft zu **sperren**.")

    with legal_tabs[3]: 
        st.subheader("Jugendschutz & Kindersicherheit")
        
        st.write("### 1. Striktes Bilderverbot von Personen")
        st.write("Zum Schutz der Privatsphäre von Kindern gilt auf der gesamten WuselMap: **Keine erkennbaren Personen auf Fotos!**")
        st.write("Bilder, auf denen Kinder oder Erwachsene identifizierbar sind, werden sofort und ohne Vorwarnung gelöscht. Wiederholte Verstöße führen zur Sperrung des Accounts.")

        st.write("### 2. Moderation & Community-Standards")
        st.write("Alle neuen Spielplatz-Vorschläge werden händisch durch das Admin-Team geprüft. Wir moderieren die Inhalte aktiv, um eine familienfreundliche Umgebung zu gewährleisten. Dennoch übernehmen wir keine Haftung für die Inhalte von Nutzerbeiträgen im Wuselfunk.")

        st.write("### 3. Meldesystem für Gefahren")
        st.write("Solltest du über die WuselMap von einem **beschädigten oder gefährlichen Spielgerät** erfahren, melde dies bitte umgehend über die Feedback-Funktion in der App, um andere Familien zu warnen.")
        st.write("**Wichtig:** Die Meldung in der WuselMap dient nur der Information anderer Nutzer. Eine offizielle Meldung zur Reparatur muss eigenständig durch den Nutzer bei der zuständigen Stadtverwaltung erfolgen.")

        st.write("### 4. Kontaktaufnahme & Privatsphäre")
        st.write("Wir raten dringend davon ab, private Daten wie Telefonnummern oder Wohnanschriften im öffentlichen Wuselfunk zu teilen. Die Crew-Funktion sollte nur mit Personen genutzt werden, die man auch im realen Leben kennt.")