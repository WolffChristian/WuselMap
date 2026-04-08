import streamlit as st
from database_manager import hole_df, sende_vorschlag, sende_feedback, optimiere_bild, aktualisiere_profil

# --- UNTER-FUNKTION 1: SUCHE ---
def show_user_area():
    st.markdown("### 📍 Kletter-Spots suchen")
    # Hier kommt dein Such-Code rein (Karte, Umkreis etc.)
    st.info("Hier kannst du Spots in deiner Nähe finden.")

# --- UNTER-FUNKTION 2: VORSCHLAG ---
def show_proposal_area():
    st.markdown("### 💡 Neuen Spot vorschlagen")
    # Hier kommt dein Formular-Code rein
    st.info("Sende uns einen neuen Kletter-Spot.")

# --- HAUPT-FUNKTION: PROFIL (Mit den Slidern/Tabs) ---
def show_profile_area():
    # Das ist der Bereich, in dem man nach dem Login landet
    st.title(f"Willkommen, {st.session_state.user}!")
    
    # HIER SIND DIE UNTER-KATEGORIEN (Slider)
    # Suche und Vorschlag sind jetzt TEIL des Profils
    unter_tabs = st.tabs(["⚙️ Meine Daten", "📍 Suche", "💡 Vorschlag"])
    
    with unter_tabs[0]:
        st.write("### Deine Profildaten")
        # Hier die Felder für E-Mail, Name etc. anzeigen
        st.write("Hier kannst du dein Profil verwalten.")
        
    with unter_tabs[1]:
        # Ruft die Suche innerhalb des Profils auf
        show_user_area()
        
    with unter_tabs[2]:
        # Ruft den Vorschlag innerhalb des Profils auf
        show_proposal_area()

# --- WEITERE HAUPT-BEREICHE ---
def show_feedback_area():
    st.title("💬 Dein Feedback")
    st.write("Was können wir verbessern?")

def show_legal_area():
    st.title("📄 Rechtliches")
    st.write("Impressum & Datenschutz")
