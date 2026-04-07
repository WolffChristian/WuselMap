import streamlit as st
import base64
from database_manager import get_all_playgrounds, sende_vorschlag, bestaetige_spot

def show_proposal_area():
    st.subheader("💡 Neuen Kletter-Spot vorschlagen")
    
    with st.form("vorschlag_form", clear_on_submit=True):
        v_name = st.text_input("Name des Spielplatzes*")
        v_adresse = st.text_input("Straße & Hausnummer*")
        
        col1, col2 = st.columns(2)
        with col1: v_plz = st.text_input("PLZ*")
        with col2: v_stadt = st.text_input("Stadt*", value="Varel")
        
        v_bundesland = st.selectbox("Bundesland", ["Niedersachsen", "Bremen", "Anderes"])
        v_alter = st.selectbox("Alter", ["0-3", "3-12", "Alle"])
        
        # Wir lassen nur WC drin, weil du den Rest Quatsch fandest
        v_wc = st.checkbox("WC vorhanden?")
        
        v_bild = st.file_uploader("Foto hochladen (Max. 2MB empfohlen)", type=["jpg", "jpeg", "png"])
        
        submit = st.form_submit_button("Vorschlag absenden")

        if submit:
            if v_name and v_adresse and v_plz:
                img_base64 = None
                if v_bild:
                    # Kleiner Check: Bilder über 3MB können die Datenbank sprengen
                    if v_bild.size > 3 * 1024 * 1024:
                        st.error("Das Bild ist zu groß (max. 3MB). Bitte kleineres Foto nehmen.")
                        return
                    img_base64 = base64.b64encode(v_bild.read()).decode()
                
                # Sende genau die 9 Werte
                erfolg = sende_vorschlag(
                    v_name, v_adresse, v_alter, st.session_state.user_id,
                    v_bundesland, v_plz, v_stadt, img_base64, v_wc
                )
                
                if erfolg:
                    st.success("Moin! Vorschlag ist raus an Christian.")
                else:
                    st.error("Fehler: Hast du den SQL-Befehl aus Schritt 1 ausgeführt?")
            else:
                st.warning("Bitte alle Felder mit * ausfüllen.")

# Diese Funktion wird für die Anzeige der Liste genutzt
def show_user_area():
    st.subheader("📍 Entdecke Varel")
    spots = get_all_playgrounds()
    for r in spots:
        with st.expander(f"📍 {r['name']} ({r['stadt']})"):
            if r.get('bild_data'):
                st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
            st.write(f"Alter: {r['alter_empf']}")
            if r.get('hat_wc'): st.info("🚻 WC vor Ort")
            
            if st.button("👍 Ich bin hier!", key=f"btn_{r['id']}"):
                if bestaetige_spot(r['id']): st.rerun()
