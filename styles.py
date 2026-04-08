import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. HINTERGRUND (Dunkelblau/Schwarz-Mix) */
        [data-testid="stSidebar"] { display: none; }
        
        /* Die gesamte App bekommt den dunklen Boden */
        .stApp { 
            background-color: #001a33 !important; 
        }

        /* 2. TEXT-FARBEN (Auf Weiß/Hellgrau umstellen) */
        h1, h2, h3 { 
            color: #ffffff !important; 
            text-align: center; 
            font-weight: 800; 
        }
        
        /* Normaler Text, Labels und Captions auf Weiß */
        p, span, label, .stMarkdown { 
            color: #e0e0e0 !important; 
        }

        /* 3. TABS (Für dunklen Hintergrund optimiert) */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { 
            background-color: #003366; /* Etwas helleres Blau als der Boden */
            border-radius: 8px; 
            border: 1px solid #004a99;
            padding: 5px 20px;
        }
        .stTabs [aria-selected="true"] { 
            background-color: #ff8c00 !important; 
            color: white !important;
            border: none !important;
        }
        /* Inaktiver Tab-Text */
        .stTabs [data-baseweb="tab"] p { color: #bbbbbb !important; }

        /* 4. BUTTONS (Bleiben kräftig Blau, Hover Orange) */
        div.stButton > button {
            background-color: #004a99 !important; /* Kräftiges Blau */
            color: white !important;
            border: 1px solid #005fcc !important;
            border-radius: 10px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: bold !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
        }

        div.stButton > button:hover {
            background-color: #ff8c00 !important;
            border-color: #ff8c00 !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(255, 140, 0, 0.3) !important;
        }

        /* 5. EINGABEFELDER (Dunkler Look) */
        .stTextInput input {
            background-color: #002b55 !important;
            color: white !important;
            border: 1px solid #004a99 !important;
            border-radius: 8px !important;
        }
        
        /* Divider Farbe anpassen */
        hr { border-color: #003366 !important; }

        </style>
    """, unsafe_allow_html=True)

def show_header():
    # Header bleibt wie gehabt, das Bild kommt aus assets
    c1, c2, c3 = st.columns([1, 4, 1])
    with col2:
        try:
            st.image("assets/Kopf_seite.png", use_container_width=True)
        except:
            st.title("WuselMap")
    st.divider()
