import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from scipy.ndimage import gaussian_filter

# -----------------------------
# 1. Setup domain and grid for Southern Norway
# -----------------------------
lat_min, lat_max = 57, 64   # degrees North
lon_min, lon_max = 4, 12    # degrees East

# Increased resolution:
num_lat = 80
num_lon = 100

lat = np.linspace(lat_min, lat_max, num_lat)
lon = np.linspace(lon_min, lon_max, num_lon)

LON, LAT = np.meshgrid(lon, lat)

# -----------------------------
# 2. Create synthetic rainfall
# -----------------------------
np.random.seed(42)
random_field = np.random.rand(num_lat, num_lon)

# Add a wave pattern for some spatial structure
wave_pattern = (
    10 * np.sin(2 * np.pi * (LAT - lat_min) / (lat_max - lat_min)) *
    np.cos(2 * np.pi * (LON - lon_min) / (lon_max - lon_min))
)

# Combine patterns, offset for positive mm/day
rain_data_original = 10 + 20 * random_field + wave_pattern

# -----------------------------
# 3. Apply spatial smoothing
# -----------------------------
sigma = 3.0  # control smoothing level
rain_data_smoothed = gaussian_filter(rain_data_original, sigma=sigma)

# -----------------------------
# 4. Define a hypothetical watershed boundary
# -----------------------------
# This polygon is just an example. The last point matches the first to "close" it.
watershed_lon = np.array([5, 5, 10, 11,  7,  5])
watershed_lat = np.array([58, 62, 63, 61, 57.5, 58])

# -----------------------------
# 5. Plot the results
# -----------------------------
fig = plt.figure(figsize=(12, 6))
projection = ccrs.PlateCarree()

# We can fix a common color range so the two panels match visually
vmin = rain_data_original.min()
vmax = rain_data_original.max()

# -----------------------------
# Subplot A: Original (High-Resolution) Data
# -----------------------------
ax1 = fig.add_subplot(1, 2, 1, projection=projection)
ax1.set_extent([lon_min, lon_max, lat_min, lat_max], crs=projection)

ax1.coastlines(resolution='50m')
ax1.gridlines(draw_labels=True)

# Plot the original rainfall field
pcm1 = ax1.pcolormesh(
    lon, lat, rain_data_original,
    cmap='Blues', shading='auto',
    vmin=vmin, vmax=vmax
)

# Plot the watershed boundary in red
ax1.plot(
    watershed_lon, watershed_lat,
    color='red', linewidth=2,
    transform=ccrs.PlateCarree()
)

cbar1 = plt.colorbar(pcm1, ax=ax1, orientation='vertical', fraction=0.04, pad=0.05)
cbar1.set_label('Rainfall (mm/day)')

ax1.set_title('Original (High-Res) Rainfall Forecast')

# -----------------------------
# Subplot B: Smoothed Data
# -----------------------------
ax2 = fig.add_subplot(1, 2, 2, projection=projection)
ax2.set_extent([lon_min, lon_max, lat_min, lat_max], crs=projection)

ax2.coastlines(resolution='50m')
ax2.gridlines(draw_labels=True)

pcm2 = ax2.pcolormesh(
    lon, lat, rain_data_smoothed,
    cmap='Blues', shading='auto',
    vmin=vmin, vmax=vmax
)

# Plot the same boundary on this panel
ax2.plot(
    watershed_lon, watershed_lat,
    color='red', linewidth=2,
    transform=ccrs.PlateCarree()
)

cbar2 = plt.colorbar(pcm2, ax=ax2, orientation='vertical', fraction=0.04, pad=0.05)
cbar2.set_label('Rainfall (mm/day)')

ax2.set_title('Smoothed Rainfall Forecast')

plt.tight_layout()
plt.show()
