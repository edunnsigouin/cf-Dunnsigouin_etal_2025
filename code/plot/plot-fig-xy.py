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
    score = ds['score']
    sig   = ds['significance']
    
    p = ax.contourf(lon, lat, score,levels=clevs,cmap=cmap,extend='min',transform=ccrs.PlateCarree())
    ax.pcolor(lon, lat, sig, hatch='/////', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.4,0.4,0.4], lw=0, transform=ccrs.PlateCarree())
    
    ax.coastlines(color='k',linewidth=1)
    #ax.set_aspect('auto')
    ax.set_title(title_text, fontsize=fontsize )
    
    if (flag == 1) or (flag == 3) or (flag == 5):
        rectangle = plt.Rectangle((-25, 34), 0.25, 0.25, fc='r',ec='r',lw=2)
    elif (flag == 2) or (flag == 4) or (flag == 6):
        rectangle = plt.Rectangle((-25, 34), 6.25, 6.25, fc=(0.5,0.5,0.5,0),ec='r',lw=2)    
    ax.add_patch(rectangle)
    
    return p

# INPUT -----------------------
write2file = False
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'fmsess_xy_tp24_daily_europe_annual_boxsize_1_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc' 
filename_in_2     = 'fmsess_xy_tp24_daily_europe_annual_boxsize_25_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc' 
filename_in_3     = 'fbss_xy_tp24_pval0.9_daily_europe_annual_boxsize_1_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_4     = 'fbss_xy_tp24_pval0.9_daily_europe_annual_boxsize_25_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_5     = 'fbss_xy_tp24_pval0.1_daily_europe_annual_boxsize_1_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_6     = 'fbss_xy_tp24_pval0.1_daily_europe_annual_boxsize_25_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc'
figname_out       = 'fig_xy.pdf'

# read in data
ds1        = xr.open_dataset(path_in + filename_in_1)
ds2        = xr.open_dataset(path_in + filename_in_2)    
ds3        = xr.open_dataset(path_in + filename_in_3)
ds4        = xr.open_dataset(path_in + filename_in_4)
ds5        = xr.open_dataset(path_in + filename_in_5)
ds6        = xr.open_dataset(path_in + filename_in_6)

# plot 
fontsize   = 11
clevs      = np.arange(0,1.1,0.1)
cmap       = 'GnBu'
figsize    = np.array([12,12])
fig,ax     = plt.subplots(nrows=3,ncols=2,figsize=(figsize[0],figsize[1]),subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0.0)})
ax         = ax.ravel()

title1 = 'a) 1 gridpoints$^{2}$ / 9km$^{2}$'
title2 = 'b) 25 gridpoints$^{2}$ / 225km$^{2}$'
title3 = 'c) 1 gridpoints$^{2}$ / 9km$^{2}$'
title4 = 'd) 25 gridpoints$^{2}$ / 225km$^{2}$'
title5 = 'e) 1 gridpoints$^{2}$ / 9km$^{2}$'
title6 = 'f) 25 gridpoints$^{2}$ / 225km$^{2}$'

setup_subplot_xy(1, ax[0], ds1, title1, clevs, cmap, fontsize)
setup_subplot_xy(2, ax[1], ds2, title2, clevs, cmap, fontsize)
setup_subplot_xy(3, ax[2], ds3, title3, clevs, cmap, fontsize)
setup_subplot_xy(4, ax[3], ds4, title4, clevs, cmap, fontsize)
setup_subplot_xy(5, ax[4], ds5, title5, clevs, cmap, fontsize)
p = setup_subplot_xy(6, ax[5], ds6, title6, clevs, cmap, fontsize)


fig.subplots_adjust(right=0.925, left=0.075,top=0.96,hspace=0.15,wspace=0.075)
cbar_ax = fig.add_axes([0.2, 0.035, 0.6, 0.02])
cb = fig.colorbar(p, cax=cbar_ax, orientation='horizontal',ticks=clevs, pad=0.025)
cb.ax.tick_params(labelsize=fontsize, size=0)
cb.ax.set_title('accuracy at lead day 5 [fmsess or fbss]', fontsize=fontsize,y=1.01)

# write2file
#plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()

