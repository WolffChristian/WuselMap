import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. Global & Sidebar */
        [data-testid="stSidebar"] { display: none; }
        .main { background-color: #ffffff; }

        /* 2. Überschriften (Kräftiges Blau) */
        h1, h2, h3 { 
            color: #003366 !important; 
            text-align: center; 
            font-weight: 800; 
        }

        /* 3. Tab-System (WuselMap Orange) */
        .stTabs [data-baseweb="tab-list"] { gap: 8px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { 
            height: 40px; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;
        }
        .stTabs [aria-selected="true"] { 
            background-color: #ff8c00 !important; 
            border: none !important; 
        }
        .stTabs [aria-selected="true"] p { color: #ffffff !important; }

        /* 4. DIE BUTTON-KORREKTUR (Nuclear Option) */
        /* Wir zwingen JEDEN Button-Typ in unser Blau */
        button[kind="primary"], 
        button[kind="secondary"], 
        [data-testid="stBaseButton-primary"], 
        [data-testid="stBaseButton-secondary"],
        .stButton button {
            background-color: #003366 !important; 
            color: white !important;
            border-radius: 10px !important;
            border: 1px solid #003366 !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }

        /* Hover-Effekt für alle Buttons (Orange) */
        button[kind="primary"]:hover, 
        button[kind="secondary"]:hover,
        [data-testid="stBaseButton-primary"]:hover,
        [data-testid="stBaseButton-secondary"]:hover,
        .stButton button:hover {
            background-color: #ff8c00 !important; 
            border-color: #ff8c00 !important;
            color: white !important;
            transform: scale(1.02) !important;
        }

        /* Verhindert, dass der Text beim Klicken schwarz wird */
        button:focus, button:active {
            color: white !important;
            box-shadow: none !important;
        }

        /* 5. Input-Felder (Login etc.) */
        .stTextInput>div>div>input {
            border-radius: 8px !important;
            border: 1px solid #003366 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def show_header():
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        try:
            st.image("assets/Kopf_seite.png", use_container_width=True)
        except:
            st.title("WuselMap") 
    st.divider()
