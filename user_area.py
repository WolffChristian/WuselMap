import streamlit as st
import base64
from database_manager import get_all_playgrounds, sende_vorschlag, bestaetige_spot

def show_user_area():
    st.title("🧗‍♂️ Kletter-Spots in Varel & Umgebung")

    # --- TEIL 1: SUCHEN & FINDEN ---
    st.subheader("Finde deinen nächsten Spot")
    
    spots = get_all_playgrounds()
    
    if not spots:
        st.info("Noch keine Spielplätze in der Datenbank.")
    else:
        for r in spots:
            # Name und Entfernung im Expander-Titel
            expander_title = f"📍 {r['name']} ({r['stadt']})"
            with st.expander(expander_title):
                # Bild anzeigen, falls vorhanden
                if r.get('bild_data'):
                    try:
                        st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
                    except:
                        st.error("Bild konnte nicht geladen werden.")

                # Infos zum Spot
                st.write(f"**Adresse:** {r['adresse']}, {r['plz']} {r['stadt']}")
                st.write(f"**Empfohlenes Alter:** {r['alter_empf']}")
                
                # WC-Info (nur anzeigen, wenn vorhanden)
                if r.get('hat_wc'):
                    st.info("🚻 WC in der Nähe vorhanden")
                
                # Bestätigungs-Datum anzeigen
                check_datum = r.get('zuletzt_bestaetigt')
                if check_datum:
                    st.caption(f"✅ Von der Community bestätigt am: {check_datum}")
                else:
                    st.caption("⚪ Noch keine aktuelle Bestätigung.")

                # DER "ICH BIN HIER"-BUTTON
                if st.button(f"👍 Ich bin hier!", key=f"check_{r['id']}"):
                    if bestaetige_spot(r['id']):
                        st.success("Bestätigt! Danke für deine Hilfe.")
                        st.rerun()

    st.divider()

    # --- TEIL 2: NEUEN SPOT VORSCHLAGEN (Sabrinas Bereich) ---
    st.subheader("Neuen Kletter-Spot vorschlagen")
    
    with st.form("vorschlag_form", clear_on_submit=True):
        v_name = st.text_input("Name des Spielplatzes")
        v_adresse = st.text_input("Straße & Hausnummer")
        col1, col2 = st.columns(2)
        with col1: v_plz = st.text_input("PLZ")
        with col2: v_stadt = st.text_input("Stadt", value="Varel")
        
        v_bundesland = st.selectbox("Bundesland", ["Niedersachsen", "Bremen", "Anderes"])
        v_alter = st.selectbox("Altersempfehlung", ["0-3 Jahre", "3-12 Jahre", "Alle Altersgruppen"])
        
        # Das einzige Zusatz-Feature, das wir behalten haben:
        v_wc = st.checkbox("Gibt es ein WC in der Nähe?")
        
        v_bild = st.file_uploader("Foto hochladen", type=["jpg", "jpeg", "png"])
        
        submit = st.form_submit_button("Vorschlag einsenden")

        if submit:
            if v_name and v_adresse:
                # Bild in Base64 umwandeln
                img_base64 = None
                if v_bild:
                    img_base64 = base64.b64encode(v_bild.read()).decode()
                
                # Ab ans Backend
                erfolg = sende_vorschlag(
                    v_name, v_adresse, v_alter, st.session_state.user_id,
                    v_bundesland, v_plz, v_stadt, img_base64, v_wc
                )
                
                if erfolg:
                    st.success("Super! Dein Vorschlag wird jetzt vom Admin (Christian) geprüft.")
                else:
                    st.error("Fehler beim Speichern. Hast du die Datenbank-Spalten erstellt?")
            else:
                st.warning("Bitte mindestens Name und Adresse ausfüllen.")
