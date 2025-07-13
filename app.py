import streamlit as st
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
from datetime import datetime
import io

# Konfigurasi halaman
st.set_page_config(page_title="Prakiraan Cuaca Barito Selatan", layout="wide")

# Judul dan informasi
st.title("🌧️ GFS Viewer Wilayah Barito Selatan (Realtime via NOMADS)")
st.header("Web Hasil Pembelajaran Pengelolaan Informasi Meteorologi")
st.markdown("**Atia Carnesia**  \n*UAS PIM M8TB 2025*")

# Fungsi untuk memuat dataset GFS dari NOMADS
@st.cache_data
def load_dataset(run_date, run_hour):
    base_url = f"https://nomads.ncep.noaa.gov/dods/gfs_0p25_1hr/gfs{run_date}/gfs_0p25_1hr_{run_hour}z"
    ds = xr.open_dataset(base_url)
    return ds

# Sidebar untuk input pengguna
st.sidebar.title("⚙️ Pengaturan")
today = datetime.utcnow()
run_date = st.sidebar.date_input("Tanggal Run GFS (UTC)", today.date())
run_hour = st.sidebar.selectbox("Jam Run GFS (UTC)", ["00", "06", "12", "18"])
forecast_hour = st.sidebar.slider("Jam ke depan", 0, 240, 0, step=1)
parameter = st.sidebar.selectbox("Parameter", [
    "Curah Hujan per jam (pratesfc)",
    "Suhu Permukaan (tmp2m)",
    "Angin Permukaan (ugrd10m & vgrd10m)",
    "Tekanan Permukaan Laut (prmslmsl)"
])

# Tombol proses
if st.sidebar.button("🔎 Tampilkan Visualisasi"):
    try:
        ds = load_dataset(run_date.strftime("%Y%m%d"), run_hour)
        if forecast_hour >= len(ds.time):
            st.error(f"Data untuk jam ke-{forecast_hour} belum tersedia.")
            st.stop()
        st.success("Dataset berhasil dimuat.")
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        st.stop()

    is_contour = False
    is_vector = False

    # Pemilihan parameter
    if "pratesfc" in parameter:
        var = ds["pratesfc"][forecast_hour, :, :] * 3600
        label = "Curah Hujan (mm/jam)"
        cmap = "Blues"
        vmin, vmax = 0, 10
    elif "tmp2m" in parameter:
        var = ds["tmp2m"][forecast_hour, :, :] - 273.15
        label = "Suhu (°C)"
        cmap = "coolwarm"
        vmin, vmax = 20, 35
    elif "ugrd10m" in parameter:
        u = ds["ugrd10m"][forecast_hour, :, :]
        v = ds["vgrd10m"][forecast_hour, :, :]
        speed = (u**2 + v**2)**0.5 * 1.94384  # m/s ke knot
        var = speed
        label = "Kecepatan Angin (knot)"
        cmap = plt.cm.get_cmap("RdYlGn_r", 10)
        vmin, vmax = 0, 20
        is_vector = True
    elif "prmsl" in parameter:
        var = ds["prmslmsl"][forecast_hour, :, :] / 100
        label = "Tekanan Permukaan Laut (hPa)"
        cmap = "cool"
        vmin, vmax = 1000, 1020
        is_contour = True
    else:
        st.warning("Parameter tidak dikenali.")
        st.stop()

    # Fokus ke wilayah Barito Selatan
    lat_min, lat_max = -2.5, -1.0
    lon_min, lon_max = 114.0, 115.5
    var = var.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

    if is_vector:
        u = u.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
        v = v.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

    # Waktu valid dan lead time
    valid_time = ds.time[forecast_hour].values
    valid_dt = pd.to_datetime(str(valid_time))
    valid_str = valid_dt.strftime("%HUTC %a %d %b %Y")
    tstr = f"t+{forecast_hour:03d}"

    # Plot peta
    fig = plt.figure(figsize=(8, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])

    # Perbaikan Judul
    ax.set_title(f"{label}\nValid {valid_str}  |  GFS {tstr}", fontsize=11, fontweight="bold")

    # Visualisasi sesuai parameter
    if is_contour:
        cs = ax.contour(var.lon, var.lat, var.values, levels=15, colors='black', linewidths=0.8, transform=ccrs.PlateCarree())
        ax.clabel(cs, fmt="%d", colors='black', fontsize=8)
    else:
        im = ax.pcolormesh(var.lon, var.lat, var.values,
                           cmap=cmap, vmin=vmin, vmax=vmax,
                           transform=ccrs.PlateCarree())
        cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.02)
        cbar.set_label(label)
        if is_vector:
            ax.quiver(var.lon[::1], var.lat[::1],
                      u.values[::1, ::1], v.values[::1, ::1],
                      transform=ccrs.PlateCarree(), scale=500, width=0.002, color='black')

    # Tambahan fitur geospasial
    ax.coastlines(resolution='10m', linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, facecolor='lightgray')

    # Lokasi Buntok - Barito Selatan
    lon_kota, lat_kota = 114.845, -1.735
    ax.plot(lon_kota, lat_kota, marker='o', color='red', markersize=6, transform=ccrs.PlateCarree())
    ax.text(lon_kota + 0.1, lat_kota + 0.1, "Buntok", fontsize=9, fontweight='bold', color='black',
            transform=ccrs.PlateCarree(), bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2'))

    # Tampilkan ke Streamlit
    st.pyplot(fig)

    # Download button
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    st.download_button("📥 Download Gambar", buf.getvalue(), file_name="gfs_barito_selatan.png", mime="image/png")
