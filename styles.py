import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. HINTERGRUND & TEXT */
        [data-testid="stSidebar"] { display: none; }
        .stApp { background-color: #001220 !important; }
        h1, h2, h3 { color: #ffffff !important; text-align: center; font-weight: 800; }
        p, span, label, .stMarkdown { color: #eeeeee !important; }

        /* 2. EINGABEFELDER (Text, Zahlen, Auswahlmenüs) */
        /* Text-Inputs, Number-Inputs und Text-Areas */
        .stTextInput input, .stNumberInput input, .stTextArea textarea {
            background-color: #001f3f !important;
            color: white !important;
            border: 1px solid #004a99 !important;
            border-radius: 8px !important;
        }

        /* Auswahlmenüs (Selectbox) */
        div[data-baseweb="select"] > div {
            background-color: #001f3f !important;
            color: white !important;
            border: 1px solid #004a99 !important;
        }
        
        /* Dropdown-Liste der Auswahlmenüs */
        ul[role="listbox"] {
            background-color: #001f3f !important;
            color: white !important;
        }

        /* 3. DATEI-UPLOADER (Vorschlag-Bereich) */
        [data-testid="stFileUploader"] {
            background-color: #001f3f !important;
            border: 1px dashed #004a99 !important;
            border-radius: 8px !important;
            padding: 10px !important;
        }
        [data-testid="stFileUploader"] section {
            background-color: #001f3f !important;
        }

        /* 4. ALLE BUTTONS (Formulare & Normal) */
        /* Wir zwingen JEDEN Button in den Wusel-Look */
        div.stButton > button, 
        button[kind="primaryFormSubmit"], 
        button[kind="secondaryFormSubmit"] {
            background-color: #004a99 !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: bold !important;
            width: 100% !important;
            transition: 0.3s ease !important;
        }

        div.stButton > button:hover, 
        button[kind="primaryFormSubmit"]:hover {
            background-color: #ff8c00 !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(255, 140, 0, 0.4) !important;
        }

        /* 5. TABELLEN (Adminbereich) */
        /* Wir dunkeln die Tabellen-Hintergründe ab */
        [data-testid="stDataFrame"] {
            background-color: #001f3f !important;
            border-radius: 8px !important;
        }
        /* Tabellen-Zellen-Text anpassen */
        [data-testid="stTable"] td, [data-testid="stTable"] th {
            background-color: #001f3f !important;
            color: white !important;
        }

        /* 6. TABS */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { 
            background-color: #002244; 
            border-radius: 8px; border: 1px solid #003366;
        }
        .stTabs [aria-selected="true"] { background-color: #ff8c00 !important; }
        
        /* Divider & Linien */
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
