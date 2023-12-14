"""
Plots fig. xy in Dunn-Sigouin et al. 
"""

import numpy       as np
import xarray      as xr
from matplotlib    import pyplot as plt
from forsikring    import misc,s2s,config
import cartopy.crs as ccrs
import matplotlib as mpl

def setup_subplot_xy(flag, ax, fss, sig, title_text, clevs, cmap, fontsize):
    """ 
    Sets up specifics of subplots for fig. xy
    """
    p = ax.contourf(fss.longitude,fss.latitude,fss,levels=clevs,cmap=cmap,extend='min',transform=ccrs.PlateCarree())
    ax.pcolor(sig.longitude, sig.latitude, sig, hatch='////', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.5,0.5,0.5], lw=0, transform=ccrs.PlateCarree())
    
    ax.coastlines(color='k',linewidth=1)
    ax.set_aspect('auto')
    ax.set_title(title_text, fontsize=fontsize )
    
    cb = plt.colorbar(p, ax=ax, orientation='vertical', ticks=clevs, pad=0.025, aspect=15)
    cb.ax.set_title('fss', fontsize=fontsize)
    cb.ax.tick_params(labelsize=fontsize, size=0)

    if (flag == 0) or (flag == 1):
        rectangle = plt.Rectangle((-25, 34), 0.25, 0.25, fc='r',ec='r')
    elif (flag == 2) or (flag == 3):
        rectangle = plt.Rectangle((-25, 34), 6.25, 6.25, fc=(0.5,0.5,0.5,0),ec='r')    
    elif (flag == 4) or (flag == 5):
        rectangle = plt.Rectangle((-25, 34), 6.25, 6.25, fc=(0.5,0.5,0.5,0),ec='r')
    ax.add_patch(rectangle)
    
    return ax

# INPUT -----------------------
write2file = False
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'fss_xy_tp24_daily_europe_annual_boxsize_1_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_2     = 'fss_xy_tp24_weekly_europe_annual_boxsize_1_leadtime_2_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_3     = 'fss_xy_tp24_daily_europe_annual_boxsize_25_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_4     = 'fss_xy_tp24_weekly_europe_annual_boxsize_25_leadtime_2_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_5     = 'fss_xy_tp24_daily_europe_annual_boxsize_41_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_6     = 'fss_xy_tp24_weekly_europe_annual_boxsize_41_leadtime_2_2020-01-02_2022-12-29_0.25x0.25.nc'
figname_out       = 'fig_xy.pdf'

# read in data
ds1        = xr.open_dataset(path_in + filename_in_1)
ds2        = xr.open_dataset(path_in + filename_in_2)    
ds3        = xr.open_dataset(path_in + filename_in_3)
ds4        = xr.open_dataset(path_in + filename_in_4)
ds5        = xr.open_dataset(path_in + filename_in_5)
ds6        = xr.open_dataset(path_in + filename_in_6)

# calculate significance
sig1       = s2s.mask_significant_values_from_bootstrap(ds1['fss_bootstrap'],0.05)
sig2       = s2s.mask_significant_values_from_bootstrap(ds2['fss_bootstrap'],0.05)
sig3       = s2s.mask_significant_values_from_bootstrap(ds3['fss_bootstrap'],0.05)
sig4       = s2s.mask_significant_values_from_bootstrap(ds4['fss_bootstrap'],0.05)
sig5       = s2s.mask_significant_values_from_bootstrap(ds5['fss_bootstrap'],0.05)
sig6       = s2s.mask_significant_values_from_bootstrap(ds6['fss_bootstrap'],0.05)

# plot 
fontsize   = 11
clevs      = np.arange(0,1.1,0.1)
cmap       = 'GnBu'
figsize    = np.array([18,8])
fig,ax     = plt.subplots(nrows=3,ncols=2,figsize=(figsize[0],figsize[1]),subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0.0)})
ax         = ax.ravel()

setup_subplot_xy(0, ax[0], ds1['fss'], sig1, 'a) lead time: 5 days, spatial scale: 1 gridpoints$^{2}$ / 9km$^{2}$', clevs, cmap, fontsize)
setup_subplot_xy(1, ax[1], ds2['fss'], sig2, 'b) lead time: 2 weeks, spatial scale: 1 gridpoints$^{2}$ / 9km$^{2}$', clevs, cmap, fontsize)
setup_subplot_xy(2, ax[2], ds3['fss'], sig3, 'c) lead time: 5 days, spatial scale: 25 gridpoints$^{2}$ / 225km$^{2}$', clevs, cmap, fontsize)
setup_subplot_xy(3, ax[3], ds4['fss'], sig4, 'd) lead time: 2 weeks, spatial scale: 25 gridpoints$^{2}$ / 225km$^{2}$', clevs, cmap, fontsize)
setup_subplot_xy(4, ax[4], ds5['fss'], sig5, 'e) lead time: 5 days, spatial scale: 41 gridpoints$^{2}$ / 369km$^{2}$', clevs, cmap, fontsize)
setup_subplot_xy(5, ax[5], ds6['fss'], sig6, 'f) lead time: 2 weeks, spatial scale: 41 gridpoints$^{2}$ / 369km$^{2}$', clevs, cmap, fontsize)

# write2file
plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()

