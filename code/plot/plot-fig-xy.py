"""
Plots fig. xy in Dunn-Sigouin et al. 
"""

import numpy       as np
import xarray      as xr
from matplotlib    import pyplot as plt
from forsikring    import misc,s2s,config
import cartopy.crs as ccrs
import matplotlib as mpl

def setup_subplot_xy(flag, ax, ds, title_text, clevs, cmap, fontsize):
    """ 
    Sets up specifics of subplots for fig. xy
    """
    lat   = ds.latitude
    lon   = ds.longitude
    score = ds['fss']
    sig   = ds['significance']
    
    p = ax.contourf(lon, lat, score,levels=clevs,cmap=cmap,extend='min',transform=ccrs.PlateCarree())
    ax.pcolor(lon, lat, sig, hatch='////', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.5,0.5,0.5], lw=0, transform=ccrs.PlateCarree())
    
    ax.coastlines(color='k',linewidth=1)
    #ax.set_aspect('auto')
    ax.set_title(title_text, fontsize=fontsize )
    
    if (flag == 1) or (flag == 4) or (flag == 7):
        rectangle = plt.Rectangle((-25, 34), 0.25, 0.25, fc='r',ec='r')
    elif (flag == 2) or (flag == 5) or (flag == 8):
        rectangle = plt.Rectangle((-25, 34), 6.25, 6.25, fc=(0.5,0.5,0.5,0),ec='r')    
    elif (flag == 3) or (flag == 6) or (flag == 9):
        rectangle = plt.Rectangle((-25, 34), 10.25, 10.25, fc=(0.5,0.5,0.5,0),ec='r')
    ax.add_patch(rectangle)
    
    return ax

# INPUT -----------------------
write2file = True
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'fss_xy_tp24_daily_europe_annual_boxsize_1_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_2     = 'fss_xy_tp24_daily_europe_annual_boxsize_25_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_3     = 'fss_xy_tp24_daily_europe_annual_boxsize_49_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc'
figname_out       = 'fig_xy.pdf'

# read in data
ds1        = xr.open_dataset(path_in + filename_in_1)
ds2        = xr.open_dataset(path_in + filename_in_2)    
ds3        = xr.open_dataset(path_in + filename_in_3)

# plot 
fontsize   = 11
clevs      = np.arange(0,1.1,0.1)
cmap       = 'GnBu'
figsize    = np.array([12,4])
fig,ax     = plt.subplots(nrows=1,ncols=3,figsize=(figsize[0],figsize[1]),subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0.0)})
ax         = ax.ravel()

title1 = 'a) 1 gridpoints$^{2}$ / 9km$^{2}$'
title2 = 'b) 25 gridpoints$^{2}$ / 225km$^{2}$'
title3 = 'c) 49 gridpoints$^{2}$ / 441km$^{2}$'

setup_subplot_xy(1, ax[0], ds1, title1, clevs, cmap, fontsize)
setup_subplot_xy(2, ax[1], ds2, title2, clevs, cmap, fontsize)
setup_subplot_xy(3, ax[2], ds3, title3, clevs, cmap, fontsize)

# write2file
plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()

