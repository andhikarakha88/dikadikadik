import streamlit as st
import pandas as pd
import requests

# Setting Tampilan Mobile
st.set_page_config(page_title="Monitoring Logistik", layout="wide")
st.title("🚢 Logistics Live Monitor")

# CONFIG (PASTIIN USER & REPO BENER)
USER = "andhikarakha88"
REPO = "dikadikadik"

def get_raw_url(filename):
    return f"https://raw.githubusercontent.com/{USER}/{REPO}/main/{filename}"

try:
    # 1. AMBIL DATA (Gue pake nama file asli lo biar gak bingung)
    # Ganti nama file di bawah ini sesuai yang ada di GitHub lo sekarang!
    url_vessel = get_raw_url("Master_Vessel_Schedule_2026-03-17.xlsx")
    url_cargo = get_raw_url("12.03.26%20DELIVERY,%20CARGO,%20STUFFING%20(PAGI)%20(1).xls")
    url_tms = get_raw_url("MASTER%20DATA2.xlsx")

    # 2. BACA EXCEL (Gue setting header & sheet sesuai file lo)
    df_vessel = pd.read_excel(url_vessel, sheet_name='MasterVesselData')
    df_cargo = pd.read_excel(url_cargo, sheet_name='Sheet1', skiprows=1) # Skip baris kosong atas
    df_tms = pd.read_excel(url_tms, sheet_name='Data', skiprows=1) # Skip header ganda

    # 3. BERSIHIN NAMA KOLOM
    df_vessel.columns = df_vessel.columns.astype(str).str.strip()
    df_cargo.columns = df_cargo.columns.astype(str).str.strip()
    df_tms.columns = df_tms.columns.astype(str).str.strip()

    # 4. PROSES GABUNG (MERGE)
    # Gabung Cargo + Vessel (Berdasarkan kolom 'Vessel' vs 'VESSEL_NAME')
    df_vessel = df_vessel.rename(columns={'VESSEL_NAME': 'Vessel'})
    merged = pd.merge(df_cargo, df_vessel, on='Vessel', how='left')

    # Gabung + TMS (Berdasarkan kolom 'Delivery' vs 'Original Delivery')
    df_tms = df_tms.rename(columns={'Original Delivery': 'Delivery'})
    final_df = pd.merge(merged, df_tms, on='Delivery', how='left')

    # 5. TAMPILIN DI WEB
    st.success("✅ Data Terupdate dari Kantor")
    
    # Filter kolom biar gak menuhin layar HP
    cols = ['Delivery', 'Vessel', 'Voyage', 'ETA', 'ETD', 'Execution Document', 'Ship-to Party Address']
    available_cols = [c for c in cols if c in final_df.columns]
    
    # Fitur Search
    search = st.text_input("Cari No Delivery / Kapal:")
    if search:
        final_df = final_df[final_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]

    st.dataframe(final_df[available_cols], use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Pastiin nama file di kodingan (baris 18-20) sama persis ama nama file di GitHub lo!")
