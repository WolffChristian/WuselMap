import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. Hintergrund & Sidebar */
        [data-testid="stSidebar"] { display: none; }
        .stApp { background-color: #ffffff; }

        /* 2. Überschriften (Midnight Blue) */
        h1, h2, h3, p { color: #003366; }
        
        /* 3. Tabs Branding */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { 
            background-color: #f0f2f6; 
            border-radius: 8px; 
            border: 1px solid #dee2e6;
            padding: 5px 20px;
        }
        .stTabs [aria-selected="true"] { 
            background-color: #ff8c00 !important; 
            color: white !important;
        }

        /* 4. DER BUTTON-FIX (Erzwungenes Blau) */
        /* Wir greifen jeden Button-Typ ab, den Streamlit generiert */
        div.stButton > button, 
        div.stBaseButton-secondary > button,
        div.stBaseButton-primary > button {
            background-color: #003366 !important;
            color: white !important;
            border: 2px solid #003366 !important;
            border-radius: 10px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: bold !important;
            width: 100% !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            display: inline-flex !important;
            justify-content: center !important;
            align-items: center !important;
        }

        /* Hover-Zustand (Orange) */
        div.stButton > button:hover {
            background-color: #ff8c00 !important;
            border-color: #ff8c00 !important;
            color: white !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        }

        /* Verhindert, dass der Button beim Klicken wieder weiß/grau wird */
        div.stButton > button:focus, 
        div.stButton > button:active {
            background-color: #003366 !important;
            color: white !important;
        }

        /* 5. Eingabefelder */
        .stTextInput input {
            border: 1px solid #003366 !important;
            border-radius: 8px !important;
        }
        </style>
    """, unsafe_allow_html=True)

def show_header():
    # Zentrierter Header mit dem Bild aus dem assets-Ordner
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        try:
            st.image("assets/Kopf_seite.png", use_container_width=True)
        except:
            st.title("WuselMap")
    st.divider()
