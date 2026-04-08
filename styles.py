import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. GRUNDGERÜST */
        [data-testid="stSidebar"] { display: none; }
        .stApp { background-color: #001220 !important; }
        h1, h2, h3 { color: #ffffff !important; text-align: center; }
        p, span, label, .stMarkdown { color: #eeeeee !important; }

        /* 2. DATEI-UPLOADER BUTTON FIX */
        /* Wir zielen direkt auf den Knopf im Uploader */
        [data-testid="stFileUploader"] section button {
            background-color: #004a99 !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
        }
        [data-testid="stFileUploader"] section button:hover {
            background-color: #ff8c00 !important;
        }
        /* Der Text "Browse files" oder "Dateien durchsuchen" */
        [data-testid="stFileUploader"] section button div p {
            color: white !important;
        }

        /* 3. TABELLEN-FIX (ADMIN-BEREICH) */
        /* Das macht die klassischen HTML-Tabellen dunkel */
        .stTable, [data-testid="stTable"] {
            background-color: #001f3f !important;
            color: white !important;
            border-radius: 8px;
        }
        [data-testid="stTable"] th {
            background-color: #003366 !important;
            color: #ff8c00 !important; /* Spaltenköpfe in Orange */
        }
        [data-testid="stTable"] td {
            background-color: #001f3f !important;
            color: white !important;
        }

        /* Falls du st.dataframe nutzt: Das ist ein Iframe/Canvas. 
           Wir versuchen den Container abzudunkeln */
        [data-testid="stDataFrame"] {
            background-color: #001f3f !important;
        }

        /* 4. ALLE ANDEREN BUTTONS */
        div.stButton > button, 
        button[kind="primaryFormSubmit"], 
        button[kind="secondaryFormSubmit"] {
            background-color: #004a99 !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
            font-weight: bold !important;
            width: 100% !important;
        }
        div.stButton > button:hover {
            background-color: #ff8c00 !important;
        }

        /* 5. FORMULARFELDER */
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
            background-color: #001f3f !important;
            color: white !important;
            border: 1px solid #004a99 !important;
        }
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
