import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from scipy.ndimage import gaussian_filter

# -----------------------------
# 1. Define domain over Southern Norway
# -----------------------------
lat_min, lat_max = 57, 64  # degrees North
lon_min, lon_max = 4, 12   # degrees East

# High-resolution grid
num_lat = 80
num_lon = 100

lat = np.linspace(lat_min, lat_max, num_lat)
lon = np.linspace(lon_min, lon_max, num_lon)
LON, LAT = np.meshgrid(lon, lat)

# -----------------------------
# 2. Create synthetic rainfall with more structure
# -----------------------------
np.random.seed(42)

# (A) Random field
random_field = np.random.rand(num_lat, num_lon)

# (B) Sinusoidal wave pattern
wave_pattern = (
    10 * np.sin(2 * np.pi * (LAT - lat_min) / (lat_max - lat_min)) *
    np.cos(2 * np.pi * (LON - lon_min) / (lon_max - lon_min))
)

# (C) Gaussian "lumps" for localized heavy rain
lumps = np.zeros_like(LAT)

# Lump #1
center1_lat, center1_lon = 60.0, 7.0
# A fairly tight lump
lump1 = 15.0 * np.exp(-((LAT - center1_lat)**2 + (LON - center1_lon)**2) / 0.5)
lumps += lump1

# Lump #2
center2_lat, center2_lon = 62.0, 10.0
# A slightly broader lump
lump2 = 25.0 * np.exp(-((LAT - center2_lat)**2 + (LON - center2_lon)**2) / 0.7)
lumps += lump2

# Combine everything (+ some offset to keep positive)
rain_data_original = 10 + 10 * random_field + wave_pattern + lumps

# -----------------------------
# 3. Apply spatial smoothing
# -----------------------------
sigma = 3.0  # Increase for more blurring
rain_data_smoothed = gaussian_filter(rain_data_original, sigma=sigma)

# -----------------------------
# 4. Define a bigger, irregular watershed fully over land
#    (in the middle of the domain)
# -----------------------------
watershed_lon = [6.0, 6.8, 7.5, 7.2, 6.3, 6.0]
watershed_lat = [59.7, 60.1, 60.3, 60.5, 60.4, 59.7]
# Note: The last point repeats the first for closure in plotting.

# -----------------------------
# 5. Plot the results
# -----------------------------
fig = plt.figure(figsize=(12, 6))
projection = ccrs.PlateCarree()

# Match the color scale on both subplots
vmin = rain_data_original.min()
vmax = rain_data_original.max()

# -----------------------------
# Subplot A: Original (High-Resolution) Data
# -----------------------------
ax1 = fig.add_subplot(1, 2, 1, projection=projection)
ax1.set_extent([lon_min, lon_max, lat_min, lat_max], crs=projection)

ax1.coastlines(resolution='50m')

# Remove lat/lon labels
gl1 = ax1.gridlines(draw_labels=False, linewidth=0.5, color='gray', alpha=0.5)

pcm1 = ax1.pcolormesh(
    lon, lat, rain_data_original,
    cmap='Blues', shading='auto',
    vmin=vmin, vmax=vmax
)

# Watershed boundary in red
ax1.plot(watershed_lon, watershed_lat,
         color='red', linewidth=2,
         transform=ccrs.PlateCarree())

cbar1 = plt.colorbar(pcm1, ax=ax1, orientation='vertical', fraction=0.04, pad=0.05)
cbar1.set_label('Rainfall (mm/day)')

ax1.set_title('Original (High-Res) Rainfall')

# -----------------------------
# Subplot B: Smoothed Data
# -----------------------------
ax2 = fig.add_subplot(1, 2, 2, projection=projection)
ax2.set_extent([lon_min, lon_max, lat_min, lat_max], crs=projection)

ax2.coastlines(resolution='50m')

# Remove lat/lon labels
gl2 = ax2.gridlines(draw_labels=False, linewidth=0.5, color='gray', alpha=0.5)

pcm2 = ax2.pcolormesh(
    lon, lat, rain_data_smoothed,
    cmap='Blues', shading='auto',
    vmin=vmin, vmax=vmax
)

# Same watershed boundary
ax2.plot(watershed_lon, watershed_lat,
         color='red', linewidth=2,
         transform=ccrs.PlateCarree())

cbar2 = plt.colorbar(pcm2, ax=ax2, orientation='vertical', fraction=0.04, pad=0.05)
cbar2.set_label('Rainfall (mm/day)')

ax2.set_title('Smoothed Rainfall')

plt.tight_layout()
plt.show()
