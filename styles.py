import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. GRUNDGERÜST */
        [data-testid="stSidebar"] { display: none; }
        .stApp { background-color: #001220 !important; }
        
        /* 2. TEXT & ÜBERSCHRIFTEN */
        h1, h2, h3 { color: #ffffff !important; text-align: center; }
        p, span, label, .stMarkdown { color: #ffffff !important; }

        /* 3. BUTTONS (Standard & Datei-Upload) */
        div.stButton > button, 
        button[kind="primaryFormSubmit"], 
        button[kind="secondaryFormSubmit"] {
            background-color: #004a99 !important;
            color: white !important;
            border-radius: 10px !important;
            border: 1px solid #005fcc !important;
            font-weight: 800 !important;
            width: 100% !important;
            transition: 0.3s;
        }

        /* DER ORANGE UPLOAD-BUTTON */
        [data-testid="stFileUploader"] section button {
            background-color: #ff8c00 !important;
            color: white !important;
            border: none !important;
        }

        /* DAS WEISSE FELD (DROPZONE) DUNKELBLAU MACHEN */
        [data-testid="stFileUploadDropzone"] {
            background-color: #001f3f !important;
            border: 2px dashed #004a99 !important;
            color: white !important;
        }

        /* Text innerhalb des Uploaders weiß machen */
        [data-testid="stFileUploadDropzone"] div div span {
            color: white !important;
        }

        /* Hover-Effekte */
        div.stButton > button:hover, [data-testid="stFileUploader"] section button:hover {
            background-color: #ff8c00 !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(255, 140, 0, 0.3) !important;
        }

        /* 4. TABS & EINGABEFELDER (Bleiben gleich) */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, 
        div[data-baseweb="select"] > div {
            background-color: #001f3f !important;
            color: white !important;
            border: 2px solid #004a99 !important;
            border-radius: 8px !important;
        }
        
        .stTabs [aria-selected="true"] { 
            background-color: #ff8c00 !important; 
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)
