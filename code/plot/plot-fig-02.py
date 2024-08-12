"""
Plots fig. 02 in Dunn-Sigouin et al. 
"""

import numpy       as np
import xarray      as xr
from matplotlib    import pyplot as plt
from forsikring    import misc,s2s,config
import cartopy.crs as ccrs
import matplotlib as mpl

def setup_subplot_xy(flag, ax, ds, clevs, cmap, fontsize):
    """ 
    Sets up specifics of subplots for fig.03
    """
    lat   = ds.latitude
    lon   = ds.longitude
    score = ds['score']
    sig   = ds['significance']
    
    p = ax.contourf(lon, lat, score,levels=clevs,cmap=cmap,transform=ccrs.PlateCarree())
    ax.pcolor(lon, lat, sig, hatch='/////', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.4,0.4,0.4], lw=0, transform=ccrs.PlateCarree())
    ax.coastlines(color='k',linewidth=1)

    if (flag == 1) or (flag == 3) or (flag == 5):
        rectangle_length = 0.25
    else:
        rectangle_length = 0.25*33
    rectangle        = plt.Rectangle((31.75, 72.75), rectangle_length, rectangle_length, angle=180, fc=(0.5,0.5,0.5,0),ec='r',lw=2)
    #if (flag == 1) or (flag == 3) or (flag == 5):
    #    rectangle = plt.Rectangle((-25, 34), 0.25, 0.25, fc='r',ec='r',lw=2)
    #elif (flag == 2) or (flag == 4) or (flag == 6):
    #    rectangle = plt.Rectangle((-25, 34), 8.25, 8.25, fc=(0.5,0.5,0.5,0),ec='r',lw=2)    
    ax.add_patch(rectangle)
    
    return p

# INPUT -----------------------
write2file = True
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'fmsess_xy_tp24_daily_europe_annual_boxsize_1_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc' 
filename_in_2     = 'fmsess_xy_tp24_daily_europe_annual_boxsize_33_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc' 
filename_in_3     = 'fbss_xy_tp24_pval0.9_daily_europe_annual_boxsize_1_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_4     = 'fbss_xy_tp24_pval0.9_daily_europe_annual_boxsize_33_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_5     = 'fbss_xy_tp24_pval0.1_daily_europe_annual_boxsize_1_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_6     = 'fbss_xy_tp24_pval0.1_daily_europe_annual_boxsize_33_leadtime_5_2020-01-02_2022-12-29_0.25x0.25.nc'
figname_out       = 'fig_02.png'

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

fig.subplots_adjust(right=0.95, left=0.05,top=0.975,bottom=0.05,hspace=-0.25,wspace=0.025)

setup_subplot_xy(1, ax[0], ds1, clevs, cmap, fontsize)
setup_subplot_xy(2, ax[1], ds2, clevs, cmap, fontsize)
setup_subplot_xy(3, ax[2], ds3, clevs, cmap, fontsize)
setup_subplot_xy(4, ax[3], ds4, clevs, cmap, fontsize)
setup_subplot_xy(5, ax[4], ds5, clevs, cmap, fontsize)
p = setup_subplot_xy(6, ax[5], ds6, clevs, cmap, fontsize)

cbar_ax = fig.add_axes([0.25, 0.05, 0.5, 0.02])
cb = fig.colorbar(p, cax=cbar_ax, orientation='horizontal',ticks=clevs, pad=0.3)
cb.ax.tick_params(labelsize=fontsize, size=0)
cb.ax.set_title('accuracy at lead day 5 [FMSESS or FBSS]', fontsize=fontsize+5,y=1.01)

ax[0].set_title('a)',fontsize=fontsize+3)
ax[1].set_title('b)',fontsize=fontsize+3)
ax[2].set_title('c)',fontsize=fontsize+3)
ax[3].set_title('d)',fontsize=fontsize+3)
ax[4].set_title('e)',fontsize=fontsize+3)
ax[5].set_title('f)',fontsize=fontsize+3)

fig.text(0.275,0.945,'precision = 1 gridpoint$^{2}$ / 9km$^{2}$',horizontalalignment='center',fontsize=fontsize+5)
fig.text(0.74,0.945,'precision = 33 gridpoints$^{2}$ / 297km$^{2}$',horizontalalignment='center',fontsize=fontsize+5)
fig.text(0.025,0.75,'anomalies',rotation=90,fontsize=fontsize+5)
fig.text(0.025,0.41,'90$^{th}$ quantile extremes',rotation=90,fontsize=fontsize+5)
fig.text(0.025,0.135,'10$^{th}$ quantile extremes',rotation=90,fontsize=fontsize+5)

# write2file
if write2file: plt.savefig(path_out + figname_out)
plt.show()

