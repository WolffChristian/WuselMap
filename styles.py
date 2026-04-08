import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. GRUND-DESIGN */
        [data-testid="stSidebar"] { display: none; }
        .stApp { background-color: #001220 !important; }
        h1, h2, h3 { color: #ffffff !important; text-align: center; font-weight: 800; }
        p, span, label, .stMarkdown { color: #eeeeee !important; }

        /* 2. TABELLEN-FIX (ADMIN-BEREICH) */
        /* Wir machen den Hintergrund für Dataframes dunkel */
        [data-testid="stDataFrame"] {
            background-color: #001f3f !important;
            border: 1px solid #004a99 !important;
            border-radius: 8px !important;
        }
        /* Falls du st.table nutzt, greift das hier: */
        .stTable, [data-testid="stTable"] {
            background-color: #001f3f !important;
            color: white !important;
        }

        /* 3. FOTO-UPLOAD (WEISSER BALKEN FIX) */
        /* Wir färben den weißen Hintergrund der Dropzone ein */
        [data-testid="stFileUploaderDropzone"] {
            background-color: #001f3f !important; /* Dunkelblau statt Weiß */
            border: 1px dashed #004a99 !important;
            color: white !important;
        }
        /* Text im Uploader */
        [data-testid="stFileUploaderDropzone"] div div span {
            color: #bbbbbb !important;
        }

        /* 4. ALLE BUTTONS (Blau, Hover Orange) */
        /* Wir zwingen JEDEN Button-Typ in den Wusel-Look */
        button, div.stButton > button, 
        button[kind="primaryFormSubmit"], 
        button[kind="secondaryFormSubmit"] {
            background-color: #004a99 !important;
            color: white !important;
            border-radius: 10px !important;
            border: 1px solid #005fcc !important;
            font-weight: bold !important;
            transition: 0.3s ease !important;
        }
        button:hover, div.stButton > button:hover {
            background-color: #ff8c00 !important;
            border-color: #ff8c00 !important;
            transform: translateY(-2px);
        }

        /* 5. EINGABEFELDER & SELECTBOXEN */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, 
        div[data-baseweb="select"] > div {
            background-color: #001f3f !important;
            color: white !important;
            border: 1px solid #004a99 !important;
            border-radius: 8px !important;
        }

        /* 6. TABS */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { 
            background-color: #002244; 
            border-radius: 8px; border: 1px solid #003366;
        }
        .stTabs [aria-selected="true"] { background-color: #ff8c00 !important; }
        
        hr { border-color: #003366 !important; }
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
