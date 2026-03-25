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
        st.sidebar.image(PATH_SIDEBAR, use_container_width=True)
    else:
        st.sidebar.error(f"Datei fehlt: {PATH_SIDEBAR}")

def display_home_banner():
    """Zeigt das große Logo zentral auf der Startseite an."""
    if os.path.exists(PATH_HOME):
        st.image(PATH_HOME, use_container_width=True)
    else:
        st.error(f"Datei fehlt: {PATH_HOME}")

def display_page_header():
    """Zeigt nur den Schriftzug als Kopfzeile für andere Seiten an."""
    if os.path.exists(PATH_HEADER):
        # width=300 sorgt dafür, dass es nicht riesig wird
        st.image(PATH_HEADER, width=300) 
    else:
        st.error(f"Datei fehlt: {PATH_HEADER}")