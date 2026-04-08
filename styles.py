import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. Global & Hintergrund */
        [data-testid="stSidebar"] { display: none; }
        .stApp { background-color: #001220 !important; }
        
        /* 2. TEXT & LABELS (Hellweiß für beste Lesbarkeit) */
        h1, h2, h3 { color: #ffffff !important; text-align: center; font-weight: 800; }
        
        /* Das hier fixiert die Beschriftungen über den Suchfeldern */
        label, .stMarkdown p, .stSlider label { 
            color: #ffffff !important; 
            font-weight: 600 !important;
            font-size: 1.1rem !important;
        }

        /* 3. EINGABEFELDER (Kontrastreichere Ränder) */
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
            background-color: #001f3f !important;
            color: white !important;
            border: 2px solid #004a99 !important; /* Dickerer, blauer Rand */
            border-radius: 8px !important;
        }

        /* 4. BUTTONS */
        div.stButton > button {
            background-color: #004a99 !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: bold !important;
        }
        div.stButton > button:hover {
            background-color: #ff8c00 !important;
            box-shadow: 0 0 15px rgba(255, 140, 0, 0.5) !important;
        }

        /* 5. TABELLEN (Dunkel & sauber) */
        .stTable, [data-testid="stTable"] {
            background-color: #001f3f !important;
            color: white !important;
        }

        /* 6. TABS */
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
