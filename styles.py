import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. DER BODEN & ALLGEMEINER TEXT */
        [data-testid="stSidebar"] { display: none; }
        .stApp { background-color: #001220 !important; }
        h1, h2, h3 { color: #ffffff !important; text-align: center; font-weight: 800; }
        p, span, label, .stMarkdown { color: #eeeeee !important; }

        /* 2. EINGABEFELDER (Vorname, Nachname, Alter, Emojis, Altersgruppe) */
        /* Text-Inputs, Number-Inputs (Alter) und Text-Areas */
        .stTextInput input, .stNumberInput input, .stTextArea textarea {
            background-color: #001f3f !important;
            color: white !important;
            border: 1px solid #004a99 !important;
            border-radius: 8px !important;
        }

        /* Auswahlmenüs (Altersgruppe & Emojis) */
        div[data-baseweb="select"] > div {
            background-color: #001f3f !important;
            color: white !important;
            border: 1px solid #004a99 !important;
            border-radius: 8px !important;
        }
        
        /* Dropdown-Inhalt der Auswahlmenüs */
        div[data-baseweb="popover"] ul {
            background-color: #001f3f !important;
            color: white !important;
        }

        /* 3. FOTO-UPLOAD BEREICH */
        [data-testid="stFileUploader"] {
            background-color: #001f3f !important;
            border: 1px dashed #004a99 !important;
            border-radius: 8px !important;
            padding: 10px !important;
        }
        /* Der Text im Upload-Bereich */
        [data-testid="stFileUploader"] section div div p { color: white !important; }
        
        /* Der Upload-Button im Feld */
        [data-testid="stFileUploader"] section button {
            background-color: #004a99 !important;
            color: white !important;
            border: none !important;
        }

        /* 4. ALLE BUTTONS (Speichern, Suchen, Einsenden, etc.) */
        div.stButton > button, 
        button[kind="primaryFormSubmit"], 
        button[kind="secondaryFormSubmit"] {
            background-color: #004a99 !important; /* Kräftiges Blau */
            color: white !important;
            border-radius: 10px !important;
            border: 1px solid #005fcc !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: bold !important;
            width: 100% !important;
            transition: 0.3s ease !important;
        }

        /* Hover-Zustand für Buttons (Orange) */
        div.stButton > button:hover, 
        button[kind="primaryFormSubmit"]:hover {
            background-color: #ff8c00 !important; /* Wusel-Orange */
            border-color: #ff8c00 !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(255, 140, 0, 0.4) !important;
        }

        /* 5. TABELLEN (ADMIN NUTZER-LISTE) */
        /* Wir versuchen alle Tabellen-Container abzudunkeln */
        [data-testid="stDataFrame"], [data-testid="stTable"], .stTable {
            background-color: #001f3f !important;
            border: 1px solid #004a99 !important;
            border-radius: 8px !important;
        }
        /* Tabellen-Zellen */
        [data-testid="stTable"] td, [data-testid="stTable"] th {
            background-color: #001f3f !important;
            color: white !important;
            border: 1px solid #003366 !important;
        }

        /* 6. TABS (Oben im Menü) */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { 
            background-color: #002244; 
            border-radius: 8px; border: 1px solid #003366;
            padding: 5px 20px;
        }
        .stTabs [aria-selected="true"] { 
            background-color: #ff8c00 !important; 
            color: white !important;
        }
        /* Textfarbe in inaktiven Tabs */
        .stTabs [data-baseweb="tab"] p { color: #cccccc !important; }

        /* Linien */
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
