"""
Plots fig 05 in Dunn-Sigouin et al. 
"""

import numpy         as np
import xarray        as xr
from matplotlib      import pyplot as plt
import cartopy.crs   as ccrs
from forsikring      import misc,s2s,config
from scipy           import signal, ndimage
import matplotlib    as mpl

def setup_subplot_xy(flag, ax, ds1, ds2, clevs, cmap, fontsize, title):
    """ 
    Sets up specifics of subplots for fig.05
    """
    lat   = ds2.latitude
    lon   = ds2.longitude

    p = ax.contourf(lon, lat, ds2,levels=clevs,cmap=cmap,extend='max',transform=ccrs.PlateCarree())
    ax.contour(lon, lat, ds2, levels=clevs,colors = [(0.7,0.7,0.7)],linewidths=0.5,transform=ccrs.PlateCarree())

    if flag < 6:
        ds1 = ds1  > 0.8
        ds1 = ds1.where(ds1, np.nan)
        ax.pcolor(lon, lat, ds1, hatch='..', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[1.0,0.0,0.0], lw=0)
        rectangle_length = 0.25*ds2['box_size']
        
    ax.coastlines(color='k',linewidth=1)
    ax.set_title(title,fontsize=fontsize+1)

    if flag == 1 :
        rectangle = plt.Rectangle((31.75, 72.75), rectangle_length, rectangle_length, angle=180, fc=(0.5,0.5,0.5,0),ec='r',lw=2)
    elif flag == 2:
        rectangle = plt.Rectangle((31.75, 72.75), rectangle_length, rectangle_length, angle=180, fc=(0.5,0.5,0.5,0),ec='r',lw=2)
    elif flag == 3:
        rectangle = plt.Rectangle((31.75, 72.75), rectangle_length, rectangle_length, angle=180, fc=(0.5,0.5,0.5,0),ec='r',lw=2)
    elif flag == 4:
        rectangle = plt.Rectangle((31.75, 72.75), rectangle_length, rectangle_length, angle=180, fc=(0.5,0.5,0.5,0),ec='r',lw=2)
    elif flag == 5:
        rectangle = plt.Rectangle((31.75, 72.75), rectangle_length, rectangle_length, angle=180, fc='r',ec='r',lw=2)
    elif flag == 6:
        rectangle = plt.Rectangle((31.75, 72.75), 0.25, 0.25, angle=180, fc='r',ec='r',lw=2)
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
filename1        = config.dirs['s2s_forecast_' + time_flag + '_anomaly'] + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-03_EFI.nc'
filename2        = config.dirs['s2s_forecast_' + time_flag + '_anomaly'] + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-04_EFI.nc'
filename3        = config.dirs['s2s_forecast_' + time_flag + '_anomaly'] + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-05_EFI.nc'
filename4        = config.dirs['s2s_forecast_' + time_flag + '_anomaly'] + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-06_EFI.nc'
filename5        = config.dirs['s2s_forecast_' + time_flag + '_anomaly'] + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-07_EFI.nc'
filename6        = config.dirs['era5_forecast_' + time_flag] + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-07.nc'
path_out         = config.dirs['fig'] + 'paper/'
figname_out      = 'fig_05.png'

# read in data
da1 = xr.open_dataset(filename1).sel(time=date).sel(box_size=33)
da2 = xr.open_dataset(filename2).sel(time=date).sel(box_size=17)
da3 = xr.open_dataset(filename3).sel(time=date).sel(box_size=11)
da4 = xr.open_dataset(filename4).sel(time=date).sel(box_size=5)
da5 = xr.open_dataset(filename5).sel(time=date).sel(box_size=1)
da6 = xr.open_dataset(filename6).sel(time=date)

# extract specified domain
dim = misc.subselect_xy_domain_from_dim(dim,domain,grid)
da1 = da1.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da2 = da2.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da3 = da3.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da4 = da4.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da5 = da5.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da6 = da6.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')

# convert to mm/day
da6[variable] = da6[variable]*1000

# plot 
fontsize = 11
clevs    = np.arange(5,55,5)
cmap     = 'GnBu'
figsize  = np.array([12,12])
fig,ax   = plt.subplots(nrows=3,ncols=2,figsize=(figsize[0],figsize[1]),subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0.0)})
ax       = ax.ravel()

fig.subplots_adjust(right=0.95, left=0.05,top=0.975,bottom=0.1,hspace=0.1,wspace=-0.1)

title1 = r'a) forecast: lead day = 5, precision = 33 gridpoints$^2$'
title2 = r'b) forecast: 4-day lead day 4, precision = 17 gridpoints$^2$'
title3 = r'c) forecast: 3-day lead day 3, precision = 11 gridpoints$^2$'
title4 = r'd) forecast: 2-day lead day 2, precision = 5 gridpoints$^2$'
title5 = r'e) forecast: 1-day lead day 1, precision = 1 gridpoint$^2$'
title6 = r'f) verification: August 7$^{th}$, 2023'

setup_subplot_xy(1, ax[0], da1['EFI'], da1[variable], clevs, cmap, fontsize, title1)
setup_subplot_xy(2, ax[1], da2['EFI'], da2[variable], clevs, cmap, fontsize, title2)
setup_subplot_xy(3, ax[2], da3['EFI'], da3[variable], clevs, cmap, fontsize, title3)
setup_subplot_xy(4, ax[3], da4['EFI'], da4[variable], clevs, cmap, fontsize, title4)
setup_subplot_xy(5, ax[4], da5['EFI'], da5[variable], clevs, cmap, fontsize, title5)
p = setup_subplot_xy(6, ax[5], da6[variable], da6[variable], clevs, cmap, fontsize, title6)

cbar_ax = fig.add_axes([0.25, 0.05, 0.5, 0.02])
cb = fig.colorbar(p, cax=cbar_ax, orientation='horizontal',ticks=clevs, pad=0.025)
cb.ax.tick_params(labelsize=fontsize, size=0)
cb.ax.set_title('daily accumulated precipitation [mm/day]', fontsize=fontsize+2,y=1.01)

if write2file: plt.savefig(path_out + figname_out)
plt.show()


