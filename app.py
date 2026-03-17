import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Monitoring Logistik", layout="wide")
st.title("🚢 Logistik Dashboard (Mobile View)")

# --- CONFIGURATION (GANTI INI) ---
USER = "andhikarakha88"
REPO = "dikadikadik"

def get_file_info():
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/"
    response = requests.get(url)
    return response.json()

try:
    files = get_file_info()
    
    # Mencari download link file secara otomatis berdasarkan kata kunci nama file
    url_delivery = [f['download_url'] for f in files if "DELIVERY" in f['name'].upper()][0]
    url_master = [f['download_url'] for f in files if "MASTER DATA" in f['name'].upper()][0]
    url_vessel = [f['download_url'] for f in files if "VESSEL" in f['name'].upper()][0]

    # --- BACA EXCEL DENGAN NAMA SHEET SESUAI INFO KAMU ---
    # Delivery Cargo -> Sheet: Shift 1
    df_cargo = pd.read_excel(url_delivery, sheet_name='Shift 1')
    
    # Master Data TMS -> Sheet: Data
    df_tms = pd.read_excel(url_master, sheet_name='Data')
    
    # Vessel Schedule -> Sheet: MasterVesselData (Sesuai file yang kamu upload)
    df_vessel = pd.read_excel(url_vessel, sheet_name='MasterVesselData')

    # --- PROSES GABUNG DATA (JOIN) ---
    # Pastikan nama kolom 'Vessel' dan 'DN Number' sama persis di file kamu
    # Jika di file kamu namanya 'DN_Number' atau 'Nomor DN', ganti tulisan di bawah ini
    
    # Gabung Cargo dengan Jadwal Kapal
    merged = pd.merge(df_cargo, df_vessel, on=['Vessel'], how='left')
    
    # Gabung dengan status TMS
    # Saya asumsikan kolom kunci di Cargo dan TMS adalah "DN Number"
    final_df = pd.merge(merged, df_tms, on='DN Number', how='left')

    # --- TAMPILAN DI HP ---
    st.subheader("Data Pengiriman Terkini")
    
    # Kotak Pencarian
    search_query = st.text_input("Cari Kapal, DN, atau Customer:")
    if search_query:
        final_df = final_df[final_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

    # Tabel interaktif (bisa digeser di HP)
    st.dataframe(final_df, use_container_width=True)

    # Indikator Tambahan
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Order", len(final_df))
    with col2:
        # Menghitung berapa yang kolom Freight Order-nya masih kosong
        pending_fo = final_df['Freight Order'].isna().sum() if 'Freight Order' in final_df.columns else 0
        st.metric("Pending FO", pending_fo)

except Exception as e:
    st.error(f"Sistem belum siap. Pastikan file sudah di-upload ke GitHub dan nama kolom sesuai. Error: {e}")
