import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Monitoring Logistik", layout="wide")
st.title("🚢 Logistik Dashboard (Final Version)")

USER = "andhikarakha88"
REPO = "dikadikadik"

def get_file_info():
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/"
    response = requests.get(url)
    return response.json()

try:
    files = get_file_info()
    url_delivery = [f['download_url'] for f in files if "DELIVERY" in f['name'].upper()][0]
    url_master = [f['download_url'] for f in files if "MASTER" in f['name'].upper()][0]
    url_vessel = [f['download_url'] for f in files if "VESSEL" in f['name'].upper()][0]

    # 1. BACA DELIVERY (Skip baris pertama karena kosong/judul di file lo)
    df_cargo = pd.read_excel(url_delivery, sheet_name='Shift 1', skiprows=1)
    
    # 2. BACA MASTER DATA (Skip baris pertama karena judul ganda)
    df_tms = pd.read_excel(url_master, sheet_name='Data', skiprows=1)
    
    # 3. BACA VESSEL
    df_vessel = pd.read_excel(url_vessel, sheet_name='MasterVesselData')

    # BERSINIHIN SPASI DI NAMA KOLOM
    for df in [df_cargo, df_tms, df_vessel]:
        df.columns = df.columns.astype(str).str.strip()

    # --- PROSES MERGE (Gue paksa namanya biar nyambung) ---
    
    # Samakan kolom Vessel
    df_vessel = df_vessel.rename(columns={'VESSEL_NAME': 'Vessel'})
    merged = pd.merge(df_cargo, df_vessel, on='Vessel', how='left')
    
    # Samakan kolom DN: 'Delivery' di Cargo vs 'Original Delivery' di TMS
    df_tms = df_tms.rename(columns={'Original Delivery': 'Delivery'})
    
    # Gabung semua
    final_df = pd.merge(merged, df_tms, on='Delivery', how='left')

    # --- TAMPILAN ---
    st.success("✅ Data Berhasil Gabung!")
    
    # Pilih kolom yang mau lo liat di HP biar gak pusing
    kolom_pilihan = ['Delivery', 'Vessel', 'Voyage', 'ETA', 'ETD', 'NO. FO', 'Customer (sebelum garis miring)']
    kolom_tersedia = [c for c in kolom_pilihan if c in final_df.columns]
    
    search = st.text_input("Cari DN atau Kapal:")
    if search:
        final_df = final_df[final_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]

    st.dataframe(final_df[kolom_tersedia], use_container_width=True)

except Exception as e:
    st.error(f"Waduh, ada masalah dikit: {e}")
    st.info("Coba cek apakah nama file di Github udah bener ada kata DELIVERY, MASTER, dan VESSEL.")
