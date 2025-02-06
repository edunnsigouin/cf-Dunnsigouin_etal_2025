import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from scipy.ndimage import gaussian_filter

# Activate XKCD style
plt.xkcd()

# -----------------------------
# 1. Zoomed-in domain
# -----------------------------
lat_min, lat_max = 58, 62
lon_min, lon_max = 5, 9

num_lat = 40
num_lon = 60

lat = np.linspace(lat_min, lat_max, num_lat)
lon = np.linspace(lon_min, lon_max, num_lon)
LON, LAT = np.meshgrid(lon, lat)

# -----------------------------
# 2. Create synthetic rainfall
# -----------------------------
np.random.seed(42)
random_field = np.random.rand(num_lat, num_lon)

wave_pattern = (
    8 * np.sin(2 * np.pi * (LAT - lat_min) / (lat_max - lat_min)) *
    np.cos(2 * np.pi * (LON - lon_min) / (lon_max - lon_min))
)

lumps = np.zeros_like(LAT)
center1_lat, center1_lon = 60.0, 7.0
lump1 = 15.0 * np.exp(-((LAT - center1_lat)**2 + (LON - center1_lon)**2) / 0.5)
lumps += lump1

center2_lat, center2_lon = 60.3, 6.7
lump2 = 25.0 * np.exp(-((LAT - center2_lat)**2 + (LON - center2_lon)**2) / 0.6)
lumps += lump2

rain_data_original = 10 + 10 * random_field + wave_pattern + lumps

# -----------------------------
# 3. Apply spatial smoothing
# -----------------------------
sigma = 4.0
rain_data_smoothed = gaussian_filter(rain_data_original, sigma=sigma)

# -----------------------------
# 4. Define watershed
# -----------------------------
watershed_lon = [6.0, 6.8, 7.5, 7.2, 6.3, 6.0]
watershed_lat = [59.7, 60.1, 60.3, 60.5, 60.4, 59.7]

# -----------------------------
# 5. Plotting
# -----------------------------
fig = plt.figure(figsize=(12, 6))
projection = ccrs.PlateCarree()

# Common color scale
vmin = rain_data_original.min()
vmax = rain_data_original.max()

# Subplot A: Original Data
ax1 = fig.add_subplot(1, 2, 1, projection=projection)
ax1.set_extent([lon_min, lon_max, lat_min, lat_max], crs=projection)
ax1.coastlines(resolution='50m')
ax1.gridlines(draw_labels=False, linewidth=0.5, color='gray', alpha=0.5)

pcm1 = ax1.pcolormesh(
    lon, lat, rain_data_original,
    cmap='Blues', shading='auto',
    vmin=vmin, vmax=vmax
)
ax1.plot(
    watershed_lon, watershed_lat,
    color='red', linewidth=2,
    transform=ccrs.PlateCarree()
)
ax1.set_title('Original (High-Res) Rainfall')

# Subplot B: Smoothed Data
ax2 = fig.add_subplot(1, 2, 2, projection=projection)
ax2.set_extent([lon_min, lon_max, lat_min, lat_max], crs=projection)
ax2.coastlines(resolution='50m')
ax2.gridlines(draw_labels=False, linewidth=0.5, color='gray', alpha=0.5)

pcm2 = ax2.pcolormesh(
    lon, lat, rain_data_smoothed,
    cmap='Blues', shading='auto',
    vmin=vmin, vmax=vmax
)
ax2.plot(
    watershed_lon, watershed_lat,
    color='red', linewidth=2,
    transform=ccrs.PlateCarree()
)
ax2.set_title('Smoothed Rainfall')

# -----------------------------
# 6. Single Horizontal Colorbar
# -----------------------------
# Create a scalar mappable from one of the pcolormesh objects
sm = plt.cm.ScalarMappable(norm=pcm1.norm, cmap=pcm1.cmap)
sm.set_array([])  # Dummy data for colorbar

cbar = plt.colorbar(
    sm,
    ax=[ax1, ax2],
    orientation='horizontal',
    fraction=0.05,
    pad=0.07
)
cbar.set_label('Rainfall (mm/day)')

plt.tight_layout()
plt.show()
