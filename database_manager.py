import pymysql
import pandas as pd
import hashlib
from PIL import Image
import io
import base64
import os
import certifi
import sys

# --- GLOBALER API KEY ---
OPENCAGE_KEY = "712b1c0ba9de4809898ffb646be05085"

# --- DATENBANK ZUGANG & VERBINDUNG ---

def get_db_creds():
    """Gibt die TiDB Cloud Zugangsdaten zurück"""
    return {
        "host": "gateway01.eu-central-1.prod.aws.tidbcloud.com",
        "port": 4000,
        "user": "rokiKLn3USmrdLy.root",
        "password": "JSDkSTRt28CdzRja",
        "database": "kletterdb"
    }

def get_db_connection():
    """Erstellt eine sichere SSL-Verbindung, optimiert für EXE und Cloud"""
    creds = get_db_creds()
    
    # PFAD-LOGIK FÜR DIE EXE: Findet das Zertifikat im internen Paket
    if hasattr(sys, '_MEIPASS'):
        ca_path = os.path.join(sys._MEIPASS, 'certifi', 'cacert.pem')
    else:
        ca_path = certifi.where()

    try:
        return pymysql.connect(
            host=creds["host"],
            port=int(creds["port"]),
            user=creds["user"],
            password=creds["password"],
            database=creds["database"],
            autocommit=True, 
            connect_timeout=20,
            ssl={"ca": ca_path}
        )
    except Exception as e:
        print(f"❌ Verbindung fehlgeschlagen: {e}")
        return None

# --- HILFSFUNKTIONEN ---

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
    except Exception as e: 
        print(f"⚠️ Bildfehler: {e}")
        return None

# --- CORE CRUD (UNIVERSAL) ---

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
    except Exception as e:
        print(f"❌ Fehler beim Laden von {tabelle}: {e}")
        return pd.DataFrame()
    finally: conn.close()

def aktualisiere_eintrag(tabelle, e_id, daten):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        # 1. Die ultimative Sicherheits-Liste für ALLE deine Tabellen
        ignore_list = [
            "id", "created_at", "updated_at", "datum", 
            "zeitpunkt", "last_login", "distance", 
            "zuletzt_bestaetigt", "erstellt_am" # <--- Jetzt sind beide Tabellen sicher!
        ]
        
        daten_copy = {}
        for k, v in daten.items():
            k_low = k.lower().strip()
            val_str = str(v).strip()
            
            # 2. Der Filter: Alles was System-Datum ist oder ein "?" hat, fliegt raus
            if k_low not in ignore_list:
                if val_str != "?" and val_str.lower() != "nan" and v is not None:
                    # Sicherstellen, dass wir bei Häkchen (tinyint) 0 oder 1 senden
                    if val_str.lower() in ["true", "false"]:
                        daten_copy[k] = 1 if val_str.lower() == "true" else 0
                    else:
                        daten_copy[k] = v

        if not daten_copy: return True
        
        # 3. Den SQL-Befehl dynamisch bauen
        set_clause = ", ".join([f"`{k}`=%s" for k in daten_copy.keys()])
        values = list(daten_copy.values())
        values.append(e_id)
        
        sql = f"UPDATE {tabelle} SET {set_clause} WHERE id = %s"
        
        cursor.execute(sql, tuple(values))
        conn.commit()
        return True
    except Exception as e:
        with open("fehlerlog.txt", "a") as f:
            f.write(f"Fehler bei ID {e_id} in {tabelle}: {str(e)}\n")
        return False
    finally: 
        cursor.close(); conn.close()
def loesche_eintrag(tabelle, e_id):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {tabelle} WHERE id = %s", (e_id,))
        conn.commit()
        return True
    except: return False
    finally: cursor.close(); conn.close()

# --- NUTZER MANAGEMENT ---

def registriere_nutzer(un, pw, em, vn, nn, al, agb):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    sql = "INSERT INTO nutzer (benutzername, passwort, email, vorname, nachname, alter_jahre, agb_akzeptiert, rolle) VALUES (%s,%s,%s,%s,%s,%s,%s,'user')"
    try:
        cursor.execute(sql, (un.strip().lower(), hash_passwort(pw), em.strip(), vn, nn, al, agb))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Registrierung fehlgeschlagen: {e}")
        return False
    finally: cursor.close(); conn.close()

def aktualisiere_profil(un, em, vn, nn, al, emo, pb=None):
    daten = {
        "email": str(em).strip(),
        "vorname": str(vn),
        "nachname": str(nn),
        "alter_jahre": int(al),
        "profil_emoji": str(emo),
        "profilbild": pb
    }
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    set_clause = ", ".join([f"`{k}`=%s" for k in daten.keys()])
    values = list(daten.values())
    values.append(un)
    sql = f"UPDATE nutzer SET {set_clause} WHERE benutzername = %s"
    try:
        cursor.execute(sql, tuple(values))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Profil-Fehler: {e}")
        return False
    finally: cursor.close(); conn.close()

# --- MESSAGING & CREW ---

def sende_nachricht(von, an, text, is_private=False, spot_name='Allgemein'):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO nachrichten (von_nutzer, recipient_id, nachricht, is_private, spot_name) VALUES (%s, %s, %s, %s, %s)"
    try: 
        cursor.execute(sql, (von, an, text, is_private, spot_name))
        conn.commit()
        return True
    except: return False
    finally: cursor.close(); conn.close()

def hole_nachrichten(nutzername, nur_privat=False):
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        if nur_privat:
            sql = f"SELECT * FROM nachrichten WHERE is_private = TRUE AND (recipient_id = %s OR von_nutzer = %s) ORDER BY zeitpunkt DESC"
            return pd.read_sql(sql, conn, params=(nutzername, nutzername))
        else:
            sql = "SELECT * FROM nachrichten WHERE is_private = FALSE ORDER BY zeitpunkt DESC"
            return pd.read_sql(sql, conn)
    finally: conn.close()
def loesche_oeffentliche_nachrichten():
    """Löscht alle öffentlichen Nachrichten aus dem Wuselfunk (Admin-Funktion)"""
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        # Wir löschen nur Nachrichten, die nicht privat sind
        sql = "DELETE FROM nachrichten WHERE is_private = FALSE"
        cursor.execute(sql)
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Fehler beim Löschen der öffentlichen Nachrichten: {e}")
        return False
    finally:
        cursor.close()
        conn.close()



def fuege_freund_hinzu(nutzer, freund_name):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT IGNORE INTO freunde (nutzer, freund, status) VALUES (%s, %s, 'offen')"
    try: 
        cursor.execute(sql, (nutzer, freund_name))
        conn.commit()
        return True
    except: return False
    finally: cursor.close(); conn.close()

def hole_freundesliste(nutzer):
    conn = get_db_connection()
    if conn is None: return []
    try:
        df = pd.read_sql("SELECT freund FROM freunde WHERE nutzer = %s AND status = 'bestätigt'", conn, params=(nutzer,))
        return df['freund'].tolist() if not df.empty else []
    finally: conn.close()

def hole_crew_anfragen(nutzername):
    conn = get_db_connection()
    if conn is None: return []
    try:
        df = pd.read_sql("SELECT nutzer FROM freunde WHERE freund = %s AND status = 'offen'", conn, params=(nutzername,))
        return df['nutzer'].tolist() if not df.empty else []
    finally: conn.close()

def bestaetige_anfrage(absender, ich):
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("UPDATE freunde SET status = 'bestätigt' WHERE nutzer = %s AND freund = %s", (absender, ich))
        cursor.execute("INSERT IGNORE INTO freunde (nutzer, freund, status) VALUES (%s, %s, 'bestätigt')", (ich, absender))
        conn.commit()
        return True
    except: return False
    finally: cursor.close(); conn.close()

def lehne_anfrage_ab(absender, ich):
    conn = get_db_connection(); cursor = conn.cursor()
    try: 
        cursor.execute("DELETE FROM freunde WHERE nutzer = %s AND freund = %s", (absender, ich))
        conn.commit()
        return True
    except: return False
    finally: cursor.close(); conn.close()

# --- SPIELPLATZ & VORSCHLAG ---

def speichere_spielplatz(standort, lat, lon, altersfreigabe, bundesland, plz, stadt, bild_data, status, ausstattung, schatten, sitze, wc, adresse, parken):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    sql = """INSERT INTO spielplaetze 
             (Standort, lat, lon, altersfreigabe, bundesland, plz, stadt, bild_data, status, ausstattung, hat_schatten, hat_sitze, hat_wc, adresse, hat_parkplatz) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    try:
        cursor.execute(sql, (standort, lat, lon, altersfreigabe, bundesland, plz, stadt, bild_data, status, ausstattung, schatten, sitze, wc, adresse, parken))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Speicherfehler: {e}")
        return False
    finally: cursor.close(); conn.close()

def sende_vorschlag(n, ad, al, us, bund, plz, stadt, bild, ds, ausst="", sch=0, sitz=0, wc=0, lat=None, lon=None, parken=0):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    sql = """INSERT INTO vorschlaege (standort, adresse, altersfreigabe, bundesland, plz, stadt, bild_data, foto_datenschutz, ausstattung, hat_schatten, hat_sitze, hat_wc, status, lat, lon, hat_parkplatz) 
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, 'neu', %s, %s, %s)"""
    try:
        cursor.execute(sql, (n, ad, al, bund, plz, stadt, bild, ds, ausst, sch, sitz, wc, lat, lon, parken))
        conn.commit()
        return True
    except: return False
    finally: cursor.close(); conn.close()

def nehme_vorschlag_an(v_id):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM vorschlaege WHERE id = %s", (v_id,))
        v = cursor.fetchone()
        if not v: return False
        sql = """INSERT INTO spielplaetze 
                 (Standort, adresse, altersfreigabe, bundesland, plz, stadt, bild_data, status, ausstattung, hat_schatten, hat_sitze, hat_wc, lat, lon, hat_parkplatz) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, 'aktiv', %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[9], v[10], v[11], v[12], v[14], v[15], v[16]))
        cursor.execute("DELETE FROM vorschlaege WHERE id = %s", (v_id,))
        conn.commit()
        return True
    except: return False
    finally: cursor.close(); conn.close()

def sende_feedback(us, ms):
    conn = get_db_connection(); cursor = conn.cursor()
    sql = "INSERT INTO feedback (nutzername, nachricht) VALUES (%s, %s)"
    try: 
        cursor.execute(sql, (us, ms))
        conn.commit()
        return True
    except: return False
    finally: cursor.close(); conn.close()

# --- ALIASE FÜR DIE APP ---
def loesche_spielplatz(s_id): return loesche_eintrag("spielplaetze", s_id)
def loesche_nutzer(n_id): return loesche_eintrag("nutzer", n_id)
def loesche_vorschlag(v_id): return loesche_eintrag("vorschlaege", v_id)
def loesche_feedback(f_id): return loesche_eintrag("feedback", f_id)