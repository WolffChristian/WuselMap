import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import hashlib

# Passwort verschlüsseln
def hash_passwort(passwort):
    return hashlib.sha256(str.encode(passwort)).hexdigest()

# Verbindung zu Google Sheets
def get_conn():
    return st.connection("gsheets", type=GSheetsConnection)

# Daten aus einem Reiter lesen
def hole_daten(reiter_name):
    conn = get_conn()
    return conn.read(worksheet=reiter_name, ttl="0s")

# Neue Daten in einen Reiter schreiben
def neue_zeile_schreiben(reiter_name, daten_dict):
    conn = get_conn()
    df = hole_daten(reiter_name)
    neue_zeile = pd.DataFrame([daten_dict])
    updated_df = pd.concat([df, neue_zeile], ignore_index=True)
    conn.update(worksheet=reiter_name, data=updated_df)
    return True
