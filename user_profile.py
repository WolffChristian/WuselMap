import streamlit as st
from database_manager import hole_df, aktualisiere_profil, optimiere_bild

def show_profile_section():
    # Daten laden
    df_n = hole_df("nutzer")
    user_row = df_n[df_n['benutzername'] == st.session_state.user].iloc[0]
    
    akt_pb = user_row.get('profilbild')
    akt_emo = user_row.get('profil_emoji', '👤')
    akt_vn = user_row.get('vorname', '')
    akt_nn = user_row.get('nachname', '')

    # --- PROFIL-KOPF ---
    c1, c2 = st.columns([1, 3])
    with c1:
        if akt_pb and len(str(akt_pb)) > 50:
            # Zeige das echte Foto rund an
            st.markdown(f"""
                <div style="display: flex; justify-content: center;">
                    <img src="data:image/jpeg;base64,{akt_pb}" 
                         style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover; border: 2px solid #0056b3;">
                </div>
                """, unsafe_allow_html=True)
        else:
            # Fallback auf Emoji
            st.markdown(f"<h1 style='text-align: center; font-size: 70px;'>{akt_emo}</h1>", unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"### {akt_vn} {akt_nn}")
        st.write(f"Nutzername: **{st.session_state.user}**")

    st.divider()

    # --- EDIT-FORMULAR ---
    with st.expander("⚙️ Profil & Foto ändern"):
        with st.form("edit_profile_form"):
            st.write("**Neues Profilbild hochladen:**")
            uploaded_file = st.file_uploader("Bild auswählen (JPG/PNG)", type=['jpg', 'jpeg', 'png'])
            
            st.write("**Oder Emoji & Daten anpassen:**")
            new_emoji = st.text_input("Profil-Emoji", value=akt_emo)
            
            col_a, col_b = st.columns(2)
            new_vn = col_a.text_input("Vorname", value=akt_vn)
            new_nn = col_b.text_input("Nachname", value=akt_nn)
            
            new_em = st.text_input("E-Mail", value=user_row.get('email', ''))
            new_al = st.number_input("Alter", min_value=0, max_value=120, value=int(user_row.get('alter_jahre', 25)))
            
            if st.form_submit_button("💾 Änderungen speichern", use_container_width=True):
                # Bild verarbeiten
                pb_final = akt_pb # Altes Bild behalten
                if uploaded_file:
                    pb_final = optimiere_bild(uploaded_file)
                
                # In DB speichern
                if aktualisiere_profil(st.session_state.user, new_em, new_vn, new_nn, new_al, new_emoji, pb_final):
                    st.success("Profil aktualisiert!")
                    st.rerun()
                else:
                    st.error("Fehler beim Speichern.")

    st.write(f"Rolle: `{st.session_state.role}` | Mitglied seit: {user_row.get('erstellt_am', '---')}")