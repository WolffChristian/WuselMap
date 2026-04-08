import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. Globaler Look & Sidebar weg */
        [data-testid="stSidebar"] { display: none; }
        .main { background-color: #ffffff; }

        /* 2. Überschriften (Kräftiges, tiefes Blau) */
        h1, h2, h3 { 
            color: #003366 !important; /* Neues, kräftigeres Blau */
            text-align: center; 
            font-weight: 800; 
        }

        /* 3. Tab-System (WuselMap Branding) */
        .stTabs [data-baseweb="tab-list"] { 
            gap: 8px; 
            justify-content: center; 
        }
        .stTabs [data-baseweb="tab"] { 
            height: 40px; 
            background-color: #f8f9fa; 
            border-radius: 8px; 
            padding: 0px 20px;
            border: 1px solid #dee2e6;
        }
        /* Inaktiver Text */
        .stTabs [data-baseweb="tab"] p { 
            color: #495057 !important; 
            font-weight: 600; 
        }
        /* Aktiver Tab (Sattes Wusel-Orange) */
        .stTabs [aria-selected="true"] { 
            background-color: #ff8c00 !important; 
            border: none !important; 
        }
        .stTabs [aria-selected="true"] p { 
            color: #ffffff !important; 
        }

        /* 4. Buttons (Kräftiges Blau) */
        .stButton>button {
            border-radius: 10px;
            border: none;
            background-color: #003366; /* Hier auch das neue Blau */
            color: white;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #ff8c00; 
            color: white;
            transform: translateY(-1px); /* Kleiner Hover-Effekt */
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        /* 5. Input Felder & Karten-Look */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            border-radius: 8px;
            border: 1px solid #ced4da;
        }

        /* 6. Status-Meldungen */
        .stSuccess {
            background-color: #e8f5e9;
            color: #2e7d32;
            border: 1px solid #c8e6c9;
        }
        </style>
    """, unsafe_allow_html=True)
