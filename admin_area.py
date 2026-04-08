import streamlit as st
from database_manager import hole_df, speichere_spielplatz

def show_admin_area():
    st.title("🛠️ Admin-Bereich")
    t1, t2, t3 = st.tabs(["📥 Vorschläge", "💬 Feedback", "👥 Nutzer"])
    
    with t1:
        df_v = hole_df("vorschlaege")
        if not df_v.empty:
            for i, r in df_v.iterrows():
                with st.container(border=True):
                    st.write(f"**{r['name']}** in {r['stadt']}")
                    if st.button(f"✅ Freigeben: {r['name']}", key=f"v_{r['id']}"):
                        # Hier kommt dein Geocoding-Code rein
                        st.success("Spot live geschaltet!")
        else: st.write("Keine neuen Vorschläge.")

    with t2:
        df_f = hole_df("feedback")
        if not df_f.empty: st.dataframe(df_f, use_container_width=True)
        else: st.write("Kein Feedback.")

    with t3:
        df_n = hole_df("nutzer")
        if not df_n.empty:
            # Zeigt alles außer das Passwort-Feld
            st.dataframe(df_n.drop(columns=['passwort'], errors='ignore'), use_container_width=True)
