import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from scipy.ndimage import gaussian_filter

# -----------------------------
# 1. Setup domain and grid
# -----------------------------
# Define latitude and longitude boundaries
lat_min, lat_max = 10, 50    # degrees North
lon_min, lon_max = -130, -60 # degrees East

# Number of points in each direction (moderate resolution)
num_lat = 40
num_lon = 70

# Create coordinates
lat = np.linspace(lat_min, lat_max, num_lat)
lon = np.linspace(lon_min, lon_max, num_lon)

# Create 2D mesh
LON, LAT = np.meshgrid(lon, lat)

# -----------------------------
# 2. Create synthetic rainfall
# -----------------------------
# Base random seed for reproducibility
np.random.seed(42)

# A random field
random_field = np.random.rand(num_lat, num_lon)

# Add a sinusoidal “wave” to create a pattern
wave_pattern = (
    10 * np.sin(2 * np.pi * (LAT - lat_min) / (lat_max - lat_min)) * 
    np.cos(2 * np.pi * (LON - lon_min) / (lon_max - lon_min))
)

# Combine patterns + offset to ensure positive mm/day
rain_data_original = 10 + 20 * random_field + wave_pattern

# -----------------------------
# 3. Apply spatial smoothing
# -----------------------------
# Use a Gaussian filter to “smooth” the field
# Sigma controls the degree of smoothing: larger sigma => more smoothing
sigma = 3.0
rain_data_smoothed = gaussian_filter(rain_data_original, sigma=sigma)

# -----------------------------
# 4. Plot the results
# -----------------------------
fig = plt.figure(figsize=(12, 5))

# Common projection
projection = ccrs.PlateCarree()

# -----------------------------
# Subplot A: Original Data
# -----------------------------
ax1 = fig.add_subplot(1, 2, 1, projection=projection)
ax1.set_extent([lon_min, lon_max, lat_min, lat_max], crs=projection)

# Add some basic features
ax1.coastlines()
ax1.gridlines(draw_labels=True)

# Contourf or pcolormesh for “cartoon style”
cs1 = ax1.pcolormesh(
    lon, lat, rain_data_original, 
    cmap='Blues', vmin=np.min(rain_data_original), vmax=np.max(rain_data_original),
    shading='auto'
)

# Add colorbar
cbar1 = plt.colorbar(cs1, ax=ax1, orientation='vertical', shrink=0.7)
cbar1.set_label('Rainfall (mm/day)')

ax1.set_title('Original Rainfall Forecast')

# -----------------------------
# Subplot B: Smoothed Data
# -----------------------------
ax2 = fig.add_subplot(1, 2, 2, projection=projection)
ax2.set_extent([lon_min, lon_max, lat_min, lat_max], crs=projection)
ax2.coastlines()
ax2.gridlines(draw_labels=True)

cs2 = ax2.pcolormesh(
    lon, lat, rain_data_smoothed,
    cmap='Blues', vmin=np.min(rain_data_original), vmax=np.max(rain_data_original),
    shading='auto'
)

cbar2 = plt.colorbar(cs2, ax=ax2, orientation='vertical', shrink=0.7)
cbar2.set_label('Rainfall (mm/day)')

ax2.set_title('Smoothed Rainfall Forecast')

plt.tight_layout()
plt.show()
