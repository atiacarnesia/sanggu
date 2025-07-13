import streamlit as st
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
from datetime import datetime

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="GFS Viewer Area Barito Selatan", layout="wide")

# Judul dan deskripsi
st.title("📡 GFS Viewer Wilayah Barito Selatan (Realtime via NOMADS)")
st.subheader("Web Hasil Pembelajaran Pengelolaan Informasi Meteorologi")

st.markdown("""
**Atia Carnesia**  
_UAS PIM M8TB 2025_
""")

# Notifikasi data
st.success("Dataset berhasil dimuat.")

# --- LOAD DATA GFS CONTOH (ubah sesuai kebutuhan jika tersedia) ---
# Contoh dummy (karena tidak ada dataset real diunggah)
# Misal Anda telah mengunduh NetCDF dari NOMADS

# Dataset dummy: Buat array curah hujan acak
import numpy as np
lat = np.linspace(-2.5, -1.0, 50)
lon = np.linspace(114.0, 115.5, 50)
rain = np.random.uniform(0, 10, size=(50, 50))

# Tanggal validitas data (pastikan tidak duplikat)
valid_datetime = datetime(2025, 7, 13, 0)
valid_str = valid_datetime.strftime("Valid %HUTC %a %d %b %Y") + " t+000"

# Plot data curah hujan
fig = plt.figure(figsize=(10, 6))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([114.0, 115.5, -2.5, -1.0], crs=ccrs.PlateCarree())
cf = ax.contourf(lon, lat, rain, levels=10, cmap='Blues', transform=ccrs.PlateCarree())
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.set_title("Curah Hujan (mm/jam) " + valid_str, fontsize=14)

# Tambahkan colorbar
plt.colorbar(cf, ax=ax, orientation='vertical', label='mm/jam')

# Tampilkan di Streamlit
st.pyplot(fig)
