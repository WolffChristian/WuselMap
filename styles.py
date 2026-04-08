import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* Hintergrund & Sidebar */
        [data-testid="stSidebar"] { display: none; }
        
        /* Titel-Farbe (Dunkelblau aus deinem Logo) */
        h1 { 
            color: #001f3f !important; 
            font-size: 24px !important; 
            text-align: center; 
            font-weight: 800;
        }
        
        /* Tabs Design */
        .stTabs [data-baseweb="tab-list"] { gap: 8px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { 
            height: 40px; 
            border-radius: 8px; 
            background-color: #f0f2f6;
        }
        
        /* Aktiver Tab (Orange aus deinem Logo) */
        .stTabs [aria-selected="true"] { 
            background-color: #ff8c00 !important; 
            border: none !important;
        }
        .stTabs [aria-selected="true"] p { color: white !important; }
        
        /* Buttons */
        .stButton>button {
            border-radius: 8px;
            border: none;
            background-color: #001f3f;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
