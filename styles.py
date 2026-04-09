import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. GRUNDGERÜST */
        [data-testid="stSidebar"] { display: none; }
        .stApp { background-color: #001220 !important; }
        
        /* 2. TEXT & ÜBERSCHRIFTEN */
        h1, h2, h3, p, span, label { color: #ffffff !important; }

        /* 3. BUTTONS (Standard & Einsenden) */
        div.stButton > button, 
        button[kind="primaryFormSubmit"], 
        button[kind="secondaryFormSubmit"] {
            background-color: #004a99 !important;
            color: white !important;
            border-radius: 10px !important;
            border: 1px solid #005fcc !important;
            font-weight: 800 !important;
            width: 100% !important;
        }

        /* 4. DATEI-UPLOAD (Feld & Button) */
        [data-testid="stFileUploader"] section {
            background-color: #001f3f !important;
            border: 2px dashed #004a99 !important;
            color: white !important;
        }
        [data-testid="stFileUploader"] section button {
            background-color: #ff8c00 !important;
            color: white !important;
            border: none !important;
        }

        /* 5. HOVER-EFFEKTE */
        div.stButton > button:hover, 
        button[kind="primaryFormSubmit"]:hover,
        [data-testid="stFileUploader"] section button:hover {
            background-color: #ff8c00 !important;
            color: white !important;
            border-color: #ff8c00 !important;
        }

        /* 6. EINGABEFELDER & TABS */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, 
        div[data-baseweb="select"] > div {
            background-color: #001f3f !important;
            color: white !important;
            border: 2px solid #004a99 !important;
        }
        .stTabs [aria-selected="true"] { background-color: #ff8c00 !important; }

        /* 7. EXPANDER (Der Balken für die Crew-Anfragen & Suche) */
        /* Den kompletten Balken-Hintergrund auf Blau setzen */
        div[data-testid="stExpander"] {
            background-color: #001f3f !important;
            border: 1px solid #004a99 !important;
            border-radius: 8px !important;
            margin-bottom: 1rem !important;
        }

        /* Den Header (den klickbaren Teil) explizit einfärben */
        div[data-testid="stExpander"] summary {
            background-color: #001f3f !important;
            color: white !important;
        }

        /* Text im Header weiß machen */
        div[data-testid="stExpander"] summary p {
            color: white !important;
        }

        /* Den Pfeil weiß machen */
        div[data-testid="stExpander"] summary svg {
            fill: white !important;
        }

        /* Hover-Effekt für den Balken (wird Orange) */
        div[data-testid="stExpander"] summary:hover {
            background-color: #004a99 !important;
            border-radius: 8px !important;
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
