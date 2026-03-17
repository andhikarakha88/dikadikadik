import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Monitoring Logistik", layout="wide")
st.title("🚢 Logistik Dashboard (Mobile View)")

# --- CONFIGURATION ---
USER = "andhikarakha88"
REPO = "dikadikadik"

def get_file_info():
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/"
    response = requests.get(url)
    return response.json()

try:
    files = get_file_info()
    
    # Cari download link berdasarkan keyword nama file
    url_delivery = [f['download_url'] for f in files if "DELIVERY" in f['name'].upper()][0]
    url_master = [f['download_url'] for f in files if "MASTER DATA" in f['name'].upper()][0]
    url_vessel = [f['download_url'] for f in files if "VESSEL" in f['name'].upper()][0]

    # --- BACA EXCEL ---
    # Delivery -> Kolom DN namanya 'Delivery'
    df_cargo = pd.read_excel(url_delivery, sheet_name='Shift 1', header=1) 
    
    # Master Data TMS -> Kolom DN namanya 'Original Delivery'
    df_tms = pd.read_excel(url_master, sheet_name='Data')
    
    # Vessel Schedule
    df_vessel = pd.read_excel(url_vessel, sheet_name='MasterVesselData')

    # Bersihkan spasi di nama kolom biar gak error
    df_cargo.columns = df_cargo.columns.str.strip()
    df_tms.columns = df_tms.columns.str.strip()
    df_vessel.columns = df_vessel.columns.str.strip()

    # --- PROSES GABUNG DATA (JOIN) ---
    
    # 1. Gabung Cargo & Vessel (Berdasarkan kolom 'Vessel')
    # Di file delivery lo kolomnya 'Vessel', di Master Vessel juga 'VESSEL_NAME'
    # Kita coba samakan dulu nama kolomnya
    df_vessel = df_vessel.rename(columns={'VESSEL_NAME': 'Vessel'})
    merged = pd.merge(df_cargo, df_vessel, on='Vessel', how='left')
    
    # 2. Gabung dengan Status TMS
    # Di Cargo namanya 'Delivery', di TMS namanya 'No. DN' atau 'Original Delivery'
    # Berdasarkan file yang lo kirim, di TMS kolomnya 'No. DN' atau 'Original Delivery'
    # Kita samakan namanya jadi 'Delivery' biar bisa digabung
    df_tms = df_tms.rename(columns={'Original Delivery': 'Delivery'})
    
    # Gabungkan
    final_df = pd.merge(merged, df_tms, on='Delivery', how='left')

    # --- TAMPILAN ---
    st.subheader("Monitoring Delivery")
    
    # Kolom yang mau ditampilkan (biar gak kepanjangan di HP)
    # Pilih kolom yang paling penting saja
    cols_to_show = ['Delivery', 'Vessel', 'Voyage', 'ETA', 'ETD', 'NO. FO', 'Customer (sebelum garis miring)']
    # Filter hanya kolom yang beneran ada
    actual_cols = [c for c in cols_to_show if c in final_df.columns]
    
    st.dataframe(final_df[actual_cols], use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Cek lagi: Pastikan nama kolom 'Delivery' di file Cargo dan 'Original Delivery' di file Master sudah benar.")
