import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(page_title="Monitoring Logistik", layout="wide")
st.title("🚢 Logistik Dashboard (Auto-Sync)")

# Setting GitHub (Ganti dengan Username & Repo kamu)
USER = "username_kamu"
REPO = "nama_repo_kamu"
TOKEN = "isi_token_kalau_repo_private" # Opsional

def get_file_list():
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/"
    response = requests.get(url)
    return response.json()

try:
    files = get_file_list()
    
    # Cari file berdasarkan keyword nama
    file_delivery = [f['download_url'] for f in files if "DELIVERY" in f['name'].upper()][0]
    file_master = [f['download_url'] for f in files if "MASTER DATA" in f['name'].upper()][0]
    file_vessel = [f['download_url'] for f in files if "VESSEL" in f['name'].upper()][0]

    # Baca Excel langsung (Tanpa CSV)
    df_cargo = pd.read_excel(file_delivery)
    df_tms = pd.read_excel(file_master)
    df_vessel = pd.read_excel(file_vessel)

    # --- BAGIAN JOIN DATA ---
    # Sesuaikan nama kolom di bawah ini dengan isi Excel kamu!
    # Misal: df_cargo punya kolom 'DN', df_tms punya 'DN Number'
    merged = pd.merge(df_cargo, df_vessel, on='Vessel', how='left')
    final_df = pd.merge(merged, df_tms, on='DN Number', how='left')

    st.success("Data Berhasil Terupdate!")
    st.dataframe(final_df)

except Exception as e:
    st.error(f"Gagal baca data. Pastikan file Excel sudah di-upload ke GitHub. Error: {e}")
