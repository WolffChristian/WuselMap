import streamlit as st
import user_area

st.set_page_config(page_title="Kletter-Kompass", page_icon="🧗‍♂️", initial_sidebar_state="collapsed")

# CSS: Sidebar weg und Buttons stylen
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stRadio > div {flex-direction: row; justify-content: center; gap: 20px;}
    </style>
""", unsafe_allow_html=True)

def main():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    if st.session_state.user_id is None:
        st.title("🧗‍♂️ Login")
        u = st.text_input("Name")
        if st.button("Starten"):
            st.session_state.user_id = u
            st.rerun()
    else:
        # Navigation oben im Hauptfenster
        wahl = st.radio("Nav", ["📍 Spots", "💡 Vorschlag"], horizontal=True, label_visibility="collapsed")
        st.divider()

        if wahl == "📍 Spots":
            user_area.show_user_area()
        else:
            user_area.show_proposal_area()
        
        if st.button("Abmelden"):
            st.session_state.user_id = None
            st.rerun()

if __name__ == "__main__":
    main()
