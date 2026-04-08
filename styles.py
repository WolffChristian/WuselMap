import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none; }
        .main { background-color: #ffffff; }
        h1, h2, h3 { color: #003366 !important; text-align: center; font-weight: 800; }
        
        .stTabs [data-baseweb="tab-list"] { gap: 8px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { 
            height: 40px; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;
        }
        .stTabs [aria-selected="true"] { background-color: #ff8c00 !important; border: none !important; }
        .stTabs [aria-selected="true"] p { color: #ffffff !important; }

        .stButton>button {
            border-radius: 10px; border: none; background-color: #003366; color: white; transition: all 0.3s;
        }
        .stButton>button:hover { background-color: #ff8c00; transform: translateY(-1px); }
        </style>
    """, unsafe_allow_html=True)

def show_header():
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        try:
            # Pfad auf assets/ geändert
            st.image("assets/Kopf_seite.png", use_container_width=True)
        except:
            st.title("WuselMap") 
    st.divider()
