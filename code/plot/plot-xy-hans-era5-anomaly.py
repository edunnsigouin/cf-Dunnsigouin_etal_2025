"""

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
    #ax.contour(lon, lat, ds, levels=clevs,colors = [(0.5,0.5,0.5)],linewidths=0.5,transform=ccrs.PlateCarree())
    ax.coastlines(color='k',linewidth=1)

    ax.set_title(title,fontsize=fontsize+5, loc='left',y=0.9,x=0.02)
    
    return p

# INPUT -----------------------
time_flag            = 'daily' 
variable             = 'tp24'   
domain               = 'scandinavia' 
grid                 = '0.25x0.25'
write2file           = False
# -----------------------------

# define stuff
dim              = misc.get_dim(grid,'daily')
filename1        = config.dirs['era5_forecast_' + time_flag + '_anomaly'] + '/' + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-06_standardized.nc'
filename2        = config.dirs['era5_forecast_' + time_flag + '_anomaly'] + '/' + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-07_standardized.nc'
filename3        = config.dirs['era5_forecast_' + time_flag + '_anomaly'] + '/' + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-08_standardized.nc'
filename4        = config.dirs['era5_forecast_' + time_flag + '_anomaly'] + '/' + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-09_standardized.nc'
path_out         = config.dirs['fig'] + 'paper/'
figname_out      = 'fig_XX.png'

# read in data
da1 = xr.open_dataset(filename1).isel(time=0).sel(box_size=1)[variable]
da2 = xr.open_dataset(filename2).isel(time=0).sel(box_size=1)[variable]
da3 = xr.open_dataset(filename3).isel(time=0).sel(box_size=1)[variable]
da4 = xr.open_dataset(filename4).isel(time=0).sel(box_size=1)[variable]

# modify units to mm/day
#da1   = da1*1000
#da2   = da2*1000
#da3   = da3*1000
#da4   = da4*1000

# extract specified domain
dim = misc.subselect_xy_domain_from_dim(dim,domain,grid)
da1 = da1.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da2 = da2.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da3 = da3.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da4 = da4.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')

# plot 
fontsize = 11
#clevs    = np.arange(5,55,5)
#cmap     = 'GnBu'
clevs    = np.arange(-10,11,1)
cmap     = 'RdBu_r'
figsize  = np.array([12,8])
fig,ax   = plt.subplots(nrows=2,ncols=2,figsize=(figsize[0],figsize[1]),subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0.0)})
ax       = ax.ravel()

title1 = 'August 6$^{th}$, 2023'
title2 = 'August 7$^{th}$, 2023'
title3 = 'August 8$^{th}$, 2023'
title4 = 'August 9$^{th}$, 2023'

setup_subplot_xy(1, ax[0], da1, clevs, cmap, fontsize, title1)
setup_subplot_xy(2, ax[1], da2, clevs, cmap, fontsize, title2)
setup_subplot_xy(3, ax[2], da3, clevs, cmap, fontsize, title3)
p = setup_subplot_xy(4, ax[3], da4, clevs, cmap, fontsize, title4)

fig.subplots_adjust(left=0.05,right=0.95, top=0.95, hspace=0.025,wspace=-0.11)
cbar_ax = fig.add_axes([0.2, 0.035, 0.6, 0.03])
cb = fig.colorbar(p, cax=cbar_ax, orientation='horizontal',ticks=clevs, pad=0.025)
cb.ax.tick_params(labelsize=fontsize, size=0)
cb.ax.set_title('daily accumulated precipitation [mm/day]', fontsize=fontsize+3,y=1.01)

if write2file: plt.savefig(path_out + figname_out)
plt.show()



