import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. GRUNDGERÜST */
        [data-testid="stSidebar"] { display: none; }
        .stApp { background-color: #001220 !important; }
        
        /* 2. TEXT & ÜBERSCHRIFTEN */
        h1, h2, h3, p, span, label { color: #ffffff !important; }

        /* 3. DAS DATEI-UPLOAD FELD (DROPZONE) */
        /* Wir nehmen hier das gesamte Element inklusive Rahmen */
        [data-testid="stFileUploader"] section {
            background-color: #001f3f !important;
            border: 2px dashed #004a99 !important;
            border-radius: 10px !important;
            color: white !important;
        }

        /* Die Schrift im Upload-Feld (Limit, Dateityp etc.) */
        [data-testid="stFileUploader"] section div div {
            color: white !important;
        }
        
        /* Der Button im Upload-Feld (Orange) */
        [data-testid="stFileUploader"] section button {
            background-color: #ff8c00 !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
        }

        /* 4. ALLGEMEINE BUTTONS */
        div.stButton > button, 
        button[kind="primaryFormSubmit"] {
            background-color: #004a99 !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: 800 !important;
            width: 100% !important;
        }

        /* 5. EINGABEFELDER (Input, Select, Textarea) */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, 
        div[data-baseweb="select"] > div {
            background-color: #001f3f !important;
            color: white !important;
            border: 2px solid #004a99 !important;
        }

        /* 6. TABS */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { background-color: #002244; border-radius: 8px; }
        .stTabs [aria-selected="true"] { background-color: #ff8c00 !important; }
        </style>
    """, unsafe_allow_html=True)

def show_header():
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        try:
            st.image("assets/Kopf_seite.png", use_container_width=True)
        except:
            st.title("WuselMap")
    st.divider()
