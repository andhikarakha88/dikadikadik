import streamlit as st
import pandas as pd

# Judul di HP
st.set_page_config(page_title="Monitoring Logistik", layout="wide")
st.title("🚢 My Logistics Monitor")

# Fungsi ambil data dari GitHub kamu (Ganti USERNAME & REPO nanti)
USER = "username_github_kamu"
REPO = "nama_repo_kamu"

def get_url(filename):
    return f"https://raw.githubusercontent.com/{USER}/{REPO}/main/{filename}"

try:
    # 1. Baca Data
    df_vessel = pd.read_csv(get_url("vessel.csv"))
    df_cargo = pd.read_csv(get_url("cargo.csv"))
    df_tms = pd.read_csv(get_url("tms.csv"))

    # 2. Proses "Jahit" Data (Merge)
    # Gabung Cargo dengan Vessel berdasarkan nama Kapal & Voyage
    merged = pd.merge(df_cargo, df_vessel, on=['Vessel', 'Voyage'], how='left')
    # Gabung hasil tadi dengan Data TMS berdasarkan nomor DN
    final_df = pd.merge(merged, df_tms, on='DN_Number', how='left')

    # 3. Tampilan di HP
    st.subheader("Ringkasan Pengiriman")
    
    # Fitur Search/Filter
    search = st.text_input("Cari Nomor DN atau Kapal:")
    if search:
        final_df = final_df[final_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]

    # Tabel Utama
    st.dataframe(final_df, use_container_width=True)

    # Indikator Sederhana
    total_dn = len(final_df)
    pending = final_df['Status_TMS'].isna().sum()
    st.metric("Total DN", total_dn)
    st.metric("Belum di-Arrange (Pending TMS)", pending)

except Exception as e:
    st.warning("Menunggu data diupload ke GitHub... Pastikan nama file vessel.csv, cargo.csv, dan tms.csv sudah benar.")
