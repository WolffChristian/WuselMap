import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. HINTERGRUND (Tiefes Midnight-Navy) */
        [data-testid="stSidebar"] { display: none; }
        
        .stApp { 
            background-color: #001220 !important; /* Fast schwarz, sehr edel */
        }

        /* 2. TEXT-FARBEN (Hell für Kontrast) */
        h1, h2, h3 { 
            color: #ffffff !important; 
            text-align: center; 
            font-weight: 800; 
        }
        
        p, span, label, .stMarkdown { 
            color: #eeeeee !important; 
        }

        /* 3. TABS (Dark Branding) */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { 
            background-color: #002244; 
            border-radius: 8px; 
            border: 1px solid #003366;
            padding: 5px 20px;
        }
        .stTabs [aria-selected="true"] { 
            background-color: #ff8c00 !important; 
            color: white !important;
            border: none !important;
        }
        .stTabs [data-baseweb="tab"] p { color: #cccccc !important; }

        /* 4. BUTTONS (Blau mit Orange-Hover) */
        div.stButton > button {
            background-color: #004a99 !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: bold !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
        }

        div.stButton > button:hover {
            background-color: #ff8c00 !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(255, 140, 0, 0.4) !important;
        }

        /* 5. INPUT FELDER (Dark Look) */
        .stTextInput input {
            background-color: #001f3f !important;
            color: white !important;
            border: 1px solid #004a99 !important;
            border-radius: 8px !important;
        }
        
        /* Trennlinien */
        hr { border-color: #003366 !important; }

        </style>
    """, unsafe_allow_html=True)

def show_header():
    # KORREKTUR: Variablen-Namen vereinheitlicht (c1, c2, c3)
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        try:
            st.image("assets/Kopf_seite.png", use_container_width=True)
        except:
            st.title("WuselMap")
    st.divider()
