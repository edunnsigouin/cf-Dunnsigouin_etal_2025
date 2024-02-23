"""
Plots fig 05 in Dunn-Sigouin et al. 
"""

import numpy         as np
import xarray        as xr
from matplotlib      import pyplot as plt
import cartopy.crs   as ccrs
from forsikring      import misc,s2s,config
from scipy           import signal, ndimage

def setup_subplot_xy(flag, ax, ds, clevs, cmap, fontsize, title):
    """ 
    Sets up specifics of subplots for fig.05
    """
    lat   = ds.latitude
    lon   = ds.longitude

    p = ax.contourf(lon, lat, ds,levels=clevs,cmap=cmap,extend='max',transform=ccrs.PlateCarree())
    ax.contour(lon, lat, ds, levels=clevs,colors = [(0.5,0.5,0.5)],linewidths=0.5,transform=ccrs.PlateCarree())
    ax.coastlines(color='k',linewidth=1)

    ax.set_title(title,fontsize=fontsize+5, loc='left',y=0.9,x=0.02)
    
    if flag == 1 :
        rectangle = plt.Rectangle((25, 66.25), 6.25, 6.25, fc=(0.5,0.5,0.5,0),ec='r',lw=2)
    elif flag == 2:
        rectangle = plt.Rectangle((28, 69.25), 3.25, 3.25, fc=(0.5,0.5,0.5,0),ec='r',lw=2)
    elif flag == 3:
        rectangle = plt.Rectangle((30.25, 71.25), 1.25, 1.25, fc=(0.5,0.5,0.5,0),ec='r',lw=2)
    elif flag == 4:
        rectangle = plt.Rectangle((31.25, 72.25), 0.25, 0.25, fc='r',ec='r',lw=2)
    ax.add_patch(rectangle)

    return p

# INPUT -----------------------
time_flag            = 'daily' 
variable             = 'tp24'   
domain               = 'scandinavia' 
date                 = '2023-08-07'
grid                 = '0.25x0.25'
write2file           = True
# -----------------------------

# define stuff
dim              = misc.get_dim(grid,'daily')
filename1        = config.dirs['s2s_forecast_' + time_flag + '_smooth'] + variable + '/' + 'tp24_0.25x0.25_2023-08-05.nc'
filename2        = config.dirs['s2s_forecast_' + time_flag + '_smooth'] + variable + '/' + 'tp24_0.25x0.25_2023-08-06.nc'
filename3        = config.dirs['s2s_forecast_' + time_flag + '_smooth'] + variable + '/' + 'tp24_0.25x0.25_2023-08-07.nc'
filename4        = config.dirs['era5_forecast_' + time_flag] + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-07.nc'
path_out         = config.dirs['fig'] + 'paper/'
figname_out      = 'fig_05.png'

# read in data
da1 = xr.open_dataset(filename1).sel(time=date)[variable].sel(box_size=25).mean(dim='number')
da2 = xr.open_dataset(filename2).sel(time=date)[variable].sel(box_size=13).mean(dim='number')
da3 = xr.open_dataset(filename3).sel(time=date)[variable].sel(box_size=3).mean(dim='number')
da4 = xr.open_dataset(filename4).sel(time=date)[variable]

# modify units to mm/day
da1   = da1*1000
da2   = da2*1000
da3   = da3*1000
da4   = da4*1000

# extract specified domain
dim = misc.subselect_xy_domain_from_dim(dim,domain,grid)
da1 = da1.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da2 = da2.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da3 = da3.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da4 = da4.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')

# plot 
fontsize = 11
clevs    = np.arange(5,55,5)
cmap     = 'GnBu'
figsize  = np.array([12,8])
fig,ax   = plt.subplots(nrows=2,ncols=2,figsize=(figsize[0],figsize[1]),subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0.0)})
ax       = ax.ravel()

title1 = '3-day lead time'
title2 = '2-day lead time'
title3 = '1-day lead time'
title4 = 'August 7$^{th}$, 2023'

setup_subplot_xy(1, ax[0], da1, clevs, cmap, fontsize, title1)
setup_subplot_xy(2, ax[1], da2, clevs, cmap, fontsize, title2)
setup_subplot_xy(3, ax[2], da3, clevs, cmap, fontsize, title3)
p = setup_subplot_xy(4, ax[3], da4, clevs, cmap, fontsize, title4)

fig.subplots_adjust(left=0.05,right=0.95, top=0.95, hspace=0.025,wspace=-0.11)
cbar_ax = fig.add_axes([0.2, 0.035, 0.6, 0.03])
cb = fig.colorbar(p, cax=cbar_ax, orientation='horizontal',ticks=clevs, pad=0.025)
cb.ax.tick_params(labelsize=fontsize, size=0)
cb.ax.set_title('daily accumulated precipitation anomalies [mm/day]', fontsize=fontsize+3,y=1.01)

if write2file: plt.savefig(path_out + figname_out)
plt.show()


