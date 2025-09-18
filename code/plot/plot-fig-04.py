"""
Plots fig. 04 in Dunn-Sigouin et al. 
"""

import numpy       as np
import xarray      as xr
from matplotlib    import pyplot as plt
from Dunnsigouin_etal_2025    import misc,s2s,config
import cartopy.crs as ccrs
import matplotlib as mpl

def setup_subplot_xy(flag, ax, title_text, ds, clevs, cmap, fontsize):
    """ 
    Sets up specifics of subplots for fig.04
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
    rectangle = plt.Rectangle((44, 72.75), rectangle_length, rectangle_length, angle=180, fc=(0.5,0.5,0.5,0),ec='r',lw=2)
    ax.add_patch(rectangle)

    ax.set_title(title_text, fontsize=fontsize + 4,loc='left', ha='left', y=0.89, x=0.015, bbox={'facecolor': 'white', 'edgecolor': 'black', 'pad': 3})
    
    return p

# INPUT -----------------------
write2file = True
# -----------------------------

# define stuff         
path_in           = config.dirs['verify']
path_out          = config.dirs['fig'] 
filename_in_1     = 'fmsess_xy_tp24_weekly_europe_annual_boxsize_1_leadtime_2_2020-01-02_2022-12-29_0.25x0.25.nc' 
filename_in_2     = 'fmsess_xy_tp24_weekly_europe_annual_boxsize_33_leadtime_2_2020-01-02_2022-12-29_0.25x0.25.nc' 
filename_in_3     = 'fbss_xy_tp24_pval0.9_weekly_europe_annual_boxsize_1_leadtime_2_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_4     = 'fbss_xy_tp24_pval0.9_weekly_europe_annual_boxsize_33_leadtime_2_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_5     = 'fbss_xy_tp24_pval0.1_weekly_europe_annual_boxsize_1_leadtime_2_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_6     = 'fbss_xy_tp24_pval0.1_weekly_europe_annual_boxsize_33_leadtime_2_2020-01-02_2022-12-29_0.25x0.25.nc'
figname_out       = 'fig_04.pdf'

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

fig.subplots_adjust(right=0.95, left=0.05,top=0.975,bottom=0.05,hspace=-0.38,wspace=0.01)

setup_subplot_xy(1, ax[0], 'a)', ds1, clevs, cmap, fontsize)
setup_subplot_xy(2, ax[1], 'b)', ds2, clevs, cmap, fontsize)
setup_subplot_xy(3, ax[2], 'c)', ds3, clevs, cmap, fontsize)
setup_subplot_xy(4, ax[3], 'd)', ds4, clevs, cmap, fontsize)
setup_subplot_xy(5, ax[4], 'e)', ds5, clevs, cmap, fontsize)
p = setup_subplot_xy(6, ax[5], 'f)', ds6, clevs, cmap, fontsize)

cbar_ax = fig.add_axes([0.25, 0.08, 0.5, 0.02])
cb = fig.colorbar(p, cax=cbar_ax, orientation='horizontal',ticks=clevs, pad=0.025)
cb.ax.tick_params(labelsize=fontsize+2, size=0)
cb.ax.set_title('accuracy at lead week 2 [FMSESS or FBSS]', fontsize=fontsize+5,y=1.01)

fig.text(0.275,0.9,'1 gridpoint$^{2}$ precision',horizontalalignment='center',fontsize=fontsize+5)
fig.text(0.74,0.9,'33 gridpoint$^{2}$ precision',horizontalalignment='center',fontsize=fontsize+5)
fig.text(0.025,0.725,'anomalies',rotation=90,fontsize=fontsize+5)
fig.text(0.025,0.42,'0.9 quantile extremes',rotation=90,fontsize=fontsize+5)
fig.text(0.025,0.16,'0.1 quantile extremes',rotation=90,fontsize=fontsize+5)

# write2file
if write2file: plt.savefig(path_out + figname_out)
plt.show()

