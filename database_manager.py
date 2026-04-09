import streamlit as st
import mysql.connector
import pandas as pd
import hashlib
from PIL import Image
import io
import base64

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            port=st.secrets["DB_PORT"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            ssl_verify_cert=False, 
            use_pure=True
        )
    except Exception as e:
        st.error(f"Datenbank-Fehler: {e}")
        return None

def hash_passwort(pw):
    return hashlib.sha256(str.encode(pw.strip())).hexdigest()

def optimiere_bild(bild_file):
    if bild_file is None: return None
    try:
        img = Image.open(bild_file)
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        img.thumbnail((800, 800))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=70)
        return base64.b64encode(buffer.getvalue()).decode()
    except: return None

def hole_df(tabelle="spielplaetze"):
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        df = pd.read_sql(f"SELECT * FROM {tabelle}", conn)
        if not df.empty:
            df.columns = [c.lower() for c in df.columns]
            if 'standort' in df.columns: 
                df = df.rename(columns={'standort': 'Standort'})
        return df
    finally: conn.close()

def registriere_nutzer(un, pw, em, vn, nn, al, agb):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, alter_jahre, agb_akzeptiert, rolle) VALUES (%s,%s,%s,%s,%s,%s,%s,'user')"
    try:
        cursor.execute(sql, (un.strip().lower(), hash_passwort(pw), em.strip(), vn, nn, al, agb))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def aktualisiere_profil(un, em, vn, nn, al, emo):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "UPDATE nutzer SET email=%s, vorname=%s, nachname=%s, alter_jahre=%s, profil_emoji=%s WHERE benutzername=%s"
    try:
        cursor.execute(sql, (em.strip(), vn, nn, al, emo, un))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def sende_vorschlag(n, ad, al, us, bund, plz, stadt, bild, ds):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    sql = """INSERT INTO vorschlaege 
             (standort, adresse, altersfreigabe, bundesland, plz, stadt, bild_data, foto_datenschutz) 
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
    try:
        cursor.execute(sql, (n, ad, al, bund, plz, stadt, bild, ds))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
        return False
    finally:
        cursor.close(); conn.close()

def sende_feedback(us, ms):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO feedback (nutzername, nachricht) VALUES (%s, %s)"
    try:
        cursor.execute(sql, (us, ms)); conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def speichere_spielplatz(n, lat, lon, al, bund, plz, stadt, bild, ds):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = """INSERT INTO spielplaetze 
             (standort, lat, lon, altersfreigabe, bundesland, plz, stadt, bild_data, foto_datenschutz) 
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    try:
        cursor.execute(sql, (n, lat, lon, al, bund, plz, stadt, bild, ds))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def loesche_vorschlag(v_id):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM vorschlaege WHERE id = %s", (v_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Fehler beim Löschen des Vorschlags: {e}")
        return False
    finally:
        cursor.close(); conn.close()

def loesche_feedback(f_id):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        # Löscht das Feedback anhand der ID
        cursor.execute("DELETE FROM feedback WHERE id = %s", (f_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Fehler beim Löschen des Feedbacks: {e}")
        return False
    finally:
        cursor.close(); conn.close()

def sende_nachricht(von, an, text):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO nachrichten (von_nutzer, an_nutzer, nachricht) VALUES (%s, %s, %s)"
    try:
        cursor.execute(sql, (von, an, text))
        conn.commit(); return True
    except: return False
    finally: cursor.close(); conn.close()

def hole_nachrichten(nutzername):
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        # Holt Nachrichten, die AN den Nutzer gehen
        return pd.read_sql(f"SELECT * FROM nachrichten WHERE an_nutzer = '{nutzername}' ORDER BY zeitpunkt DESC", conn)
    finally: conn.close()

def show_wusel_crew():
    st.subheader("👥 Wusel-Crew")
    
    # --- 1. Offene Anfragen (Neu!) ---
    anfragen = hole_crew_anfragen(st.session_state.user)
    if anfragen:
        with st.expander(f"🔔 Du hast {len(anfragen)} neue Crew-Anfragen!", expanded=True):
            for absender in anfragen:
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"**{absender}** möchte in deine Crew.")
                if c2.button("✅ Ja", key=f"yes_{absender}"):
                    if bestaetige_anfrage(absender, st.session_state.user):
                        st.success("Bestätigt!"); st.rerun()
                if c3.button("❌ Nein", key=f"no_{absender}"):
                    if lehne_anfrage_ab(absender, st.session_state.user):
                        st.rerun()
        st.divider()

    # --- 2. Neue Leute suchen ---
    with st.expander("🔍 Neue Leute zur Crew hinzufügen"):
        suche = st.text_input("Nutzername eingeben").strip()
        if st.button("Anfrage senden"):
            df_u = hole_df("nutzer")
            if suche.lower() in df_u['benutzername'].str.lower().values:
                if suche.lower() != st.session_state.user.lower():
                    if fuege_freund_hinzu(st.session_state.user, suche):
                        st.info(f"Anfrage an {suche} wurde gesendet! Warte auf Bestätigung.")
                else: st.warning("Das bist du selbst!")
            else: st.error("Nutzer nicht gefunden.")
    
    st.divider()

    # --- 3. Liste der bestätigten Crew-Mitglieder ---
    crew = hole_freundesliste(st.session_state.user)
    if crew:
        st.write("Deine Crew:")
        for f in crew:
            c1, c2 = st.columns([3, 1])
            with c1: st.write(f"🧗 **{f}**")
            with c2:
                if st.button("📩 Funk", key=f"btn_{f}"):
                    st.session_state.msg_target = f
                    st.info(f"Geh zum Tab 'Wuselfunk' um {f} zu schreiben.")
    else:
        st.caption("Deine Crew ist noch leer oder wartet auf Bestätigungen.")
