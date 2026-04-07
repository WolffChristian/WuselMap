import streamlit as st
import base64
from database_manager import get_all_playgrounds, sende_vorschlag, bestaetige_spot

def show_user_area():
    st.subheader("📍 Kletter-Spots")
    spots = get_all_playgrounds()
    if not spots:
        st.info("Keine Spots gefunden.")
        return
    for r in spots:
        with st.expander(f"📍 {r['name']} ({r['stadt']})"):
            if r.get('bild_data'):
                try:
                    st.image(f"data:image/jpeg;base64,{r['bild_data']}", use_container_width=True)
                except:
                    st.warning("Bild-Format Fehler")
            st.write(f"**Alter:** {r['alter_empf']}")
            if r.get('hat_wc'): st.info("Option: 🚻 WC vorhanden")
            
            datum = r.get('zuletzt_bestaetigt')
            st.caption(f"✅ Zuletzt geprüft: {datum if datum else 'Noch nicht bestätigt'}")
            if st.button("👍 Ich bin gerade hier", key=f"check_{r['id']}"):
                if bestaetige_spot(r['id']): st.rerun()

def show_proposal_area():
    st.subheader("💡 Spot für Sabrina")
    with st.form("main_v_form", clear_on_submit=True):
        n = st.text_input("Name des Spots*")
        ad = st.text_input("Straße & Hausnr.*")
        c1, c2 = st.columns(2)
        with c1: p = st.text_input("PLZ*")
        with c2: s = st.text_input("Stadt*", value="Varel")
        al = st.selectbox("Zielgruppe", ["0-3", "3-12", "Alle"])
        wc = st.checkbox("WC vorhanden?")
        img = st.file_uploader("Foto (Handy-Foto ok)", type=["jpg", "png", "jpeg"])
        
        if st.form_submit_button("Spot abschicken"):
            if n and ad and p:
                img_b64 = None
                if img:
                    img_b64 = base64.b64encode(img.read()).decode()
                
                # Wir schicken jetzt die 9 sauberen Werte
                if sende_vorschlag(n, ad, al, st.session_state.user_id, "Niedersachsen", p, s, img_b64, wc):
                    st.success("Moin! Dein Spot ist gespeichert.")
            else:
                st.error("Bitte die Pflichtfelder (*) ausfüllen.")
