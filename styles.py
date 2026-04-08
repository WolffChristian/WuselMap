import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. Globaler Look & Sidebar weg */
        [data-testid="stSidebar"] { display: none; }
        .main { background-color: #ffffff; }

        /* 2. Überschriften (Dunkelblau) */
        h1, h2, h3 { 
            color: #001f3f !important; 
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
            background-color: #f0f2f6; 
            border-radius: 8px; 
            padding: 0px 20px;
            border: 1px solid #dfe1e5;
        }
        /* Inaktiver Text */
        .stTabs [data-baseweb="tab"] p { 
            color: #555555 !important; 
            font-weight: 600; 
        }
        /* Aktiver Tab (Orange wie die Route im Logo) */
        .stTabs [aria-selected="true"] { 
            background-color: #ff8c00 !important; 
            border: none !important; 
        }
        .stTabs [aria-selected="true"] p { 
            color: #ffffff !important; 
        }

        /* 4. Buttons (Dunkelblau) */
        .stButton>button {
            border-radius: 10px;
            border: none;
            background-color: #001f3f;
            color: white;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #ff8c00; /* Wechselt zu Orange beim Drüberfahren */
            color: white;
        }

        /* 5. Input Felder abrunden */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            border-radius: 8px;
        }

        /* 6. Info-Boxen & Erfolg (Erfolgsmeldung in Orange/Gelb) */
        .stSuccess {
            background-color: #fff3e0;
            color: #e65100;
            border: 1px solid #ffb74d;
        }
        </style>
    """, unsafe_allow_html=True)
