# assets_helper.py
import streamlit as st
import os

# --- KONFIGURATION DER PFADE ---
ASSETS_DIR = "assets"
PATH_SIDEBAR = os.path.join(ASSETS_DIR, "Kletterkompass_Logo.png")
PATH_HOME = os.path.join(ASSETS_DIR, "Kletterkompass.png")
PATH_HEADER = os.path.join(ASSETS_DIR, "Kletterkompass_Schrieftzug.png")

# --- FUNKTIONEN ZUM ANZEIGEN ---

def display_sidebar_logo():
    """Zeigt das runde Logo oben in der Sidebar an."""
    if os.path.exists(PATH_SIDEBAR):
        # width='stretch' ersetzt das veraltete use_container_width
        st.sidebar.image(PATH_SIDEBAR, width='stretch')
    else:
        st.sidebar.error(f"Datei fehlt: {PATH_SIDEBAR}")

def display_home_banner():
    """Zeigt das große Logo zentral auf der Startseite an."""
    if os.path.exists(PATH_HOME):
        # width='stretch' sorgt für die volle Breite im Hauptbereich
        st.image(PATH_HOME, width='stretch')
    else:
        st.error(f"Datei fehlt: {PATH_HOME}")

def display_page_header():
    """Zeigt nur den Schriftzug als Kopfzeile für andere Seiten an."""
    if os.path.exists(PATH_HEADER):
        # width=300 sorgt dafür, dass es dezent bleibt
        st.image(PATH_HEADER, width=300) 
    else:
        st.error(f"Datei fehlt: {PATH_HEADER}")
