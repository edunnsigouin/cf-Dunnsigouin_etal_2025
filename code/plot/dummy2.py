import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from scipy.ndimage import gaussian_filter

# -----------------------------
# 1. Setup domain and grid for Norway
# -----------------------------
lat_min, lat_max = 57, 72   # degrees North
lon_min, lon_max = 4, 31    # degrees East

# Number of points in each direction
num_lat = 30
num_lon = 40

# Create coordinates
lat = np.linspace(lat_min, lat_max, num_lat)
lon = np.linspace(lon_min, lon_max, num_lon)

# Create 2D mesh
LON, LAT = np.meshgrid(lon, lat)

# -----------------------------
# 2. Create synthetic rainfall
# -----------------------------
# Set random seed for reproducibility
np.random.seed(42)

# A random field
random_field = np.random.rand(num_lat, num_lon)

# A sinusoidal “wave” pattern to mimic a real spatial structure
wave_pattern = (
    10 * np.sin(2 * np.pi * (LAT - lat_min) / (lat_max - lat_min)) *
    np.cos(2 * np.pi * (LON - lon_min) / (lon_max - lon_min))
)

# Combine patterns + add an offset to ensure positive mm/day
rain_data_original = 10 + 20 * random_field + wave_pattern

# -----------------------------
# 3. Apply spatial smoothing
# -----------------------------
sigma = 3.0  # Larger sigma -> more smoothing
rain_data_smoothed = gaussian_filter(rain_data_original, sigma=sigma)

# -----------------------------
# 4. Plot the results
# -----------------------------
fig = plt.figure(figsize=(12, 5))

# We'll use a PlateCarree projection
projection = ccrs.PlateCarree()

# -----------------------------
# Subplot A: Original Data
# -----------------------------
ax1 = fig.add_subplot(1, 2, 1, projection=projection)
ax1.set_extent([lon_min, lon_max, lat_min, lat_max], crs=projection)

# Add some basic features
ax1.coastlines(resolution='50m', color='black', linewidth=1)
ax1.gridlines(draw_labels=True)

# Plot the original rainfall
pcm1 = ax1.pcolormesh(
    lon, lat, rain_data_original,
    cmap='Blues', shading='auto'
)
cbar1 = plt.colorbar(pcm1, ax=ax1, orientation='vertical', fraction=0.04, pad=0.05)
cbar1.set_label('Rainfall (mm/day)')

ax1.set_title('Original Rainfall Forecast')

# -----------------------------
# Subplot B: Smoothed Data
# -----------------------------
ax2 = fig.add_subplot(1, 2, 2, projection=projection)
ax2.set_extent([lon_min, lon_max, lat_min, lat_max], crs=projection)

# Add the same features for consistency
ax2.coastlines(resolution='50m', color='black', linewidth=1)
ax2.gridlines(draw_labels=True)

pcm2 = ax2.pcolormesh(
    lon, lat, rain_data_smoothed,
    cmap='Blues', shading='auto'
)
cbar2 = plt.colorbar(pcm2, ax=ax2, orientation='vertical', fraction=0.04, pad=0.05)
cbar2.set_label('Rainfall (mm/day)')

ax2.set_title('Smoothed Rainfall Forecast')

plt.tight_layout()
plt.show()
