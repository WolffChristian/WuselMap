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

        /* 3. BUTTONS (Blau mit weißem Text / Orange mit weißem Text) */
        div.stButton > button, 
        button[kind="primaryFormSubmit"], 
        button[kind="secondaryFormSubmit"] {
            background-color: #004a99 !important;
            color: white !important; /* IMMER WEISS */
            border-radius: 10px !important;
            border: 1px solid #005fcc !important;
            font-weight: 800 !important;
            width: 100% !important;
            transition: 0.3s;
        }

        /* Hover & Aktiv (Orange mit weißem Text) */
        div.stButton > button:hover, 
        div.stButton > button:active,
        div.stButton > button:focus,
        button[kind="primaryFormSubmit"]:hover {
            background-color: #ff8c00 !important;
            color: white !important; /* BLEIBT WEISS */
            border-color: #ff8c00 !important;
            box-shadow: 0 4px 15px rgba(255, 140, 0, 0.3) !important;
        }

        /* 4. TABELLEN (HOCH-KONTRAST) */
        [data-testid="stTable"], .stTable {
            background-color: #001f3f !important;
            color: white !important;
        }
        /* Zellen-Text in Tabellen explizit weiß machen */
        [data-testid="stTable"] td, [data-testid="stTable"] th {
            color: white !important;
            background-color: #001f3f !important;
            border: 1px solid #004a99 !important;
        }

        /* 5. EINGABEFELDER */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, 
        div[data-baseweb="select"] > div {
            background-color: #001f3f !important;
            color: white !important;
            border: 2px solid #004a99 !important;
            border-radius: 8px !important;
        }

        /* 6. TABS */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { 
            background-color: #002244; 
            border-radius: 8px; border: 1px solid #003366;
        }
        .stTabs [aria-selected="true"] { 
            background-color: #ff8c00 !important; 
            color: white !important;
        }
        
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
