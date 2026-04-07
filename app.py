import streamlit as st
import user_area

st.set_page_config(page_title="Kletter-Kompass", page_icon="🧗‍♂️", initial_sidebar_state="collapsed")

# Sidebar verstecken & Menü stylen
st.markdown("""<style>[data-testid="stSidebar"] {display: none;} .stRadio > div {flex-direction: row; justify-content: center; gap: 30px;}</style>""", unsafe_allow_html=True)

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_id is None:
    st.title("🧗‍♂️ Kletter-Kompass Varel")
    with st.container():
        st.subheader("Login")
        user = st.text_input("Nutzername (z.B. Sabrina)")
        pw = st.text_input("Passwort", type="password")
        if st.button("Anmelden"):
            if user and pw: # Hier später echte Prüfung einbauen
                st.session_state.user_id = user
                st.rerun()
else:
    # Navigation oben
    menu = ["📍 Spots", "💡 Vorschlag"]
    wahl = st.radio("Nav", menu, horizontal=True, label_visibility="collapsed")
    st.divider()

    if wahl == "📍 Spots":
        user_area.show_user_area()
    elif wahl == "💡 Vorschlag":
        user_area.show_proposal_area()
    
    if st.button("Abmelden", use_container_width=True):
        st.session_state.user_id = None
        st.rerun()
