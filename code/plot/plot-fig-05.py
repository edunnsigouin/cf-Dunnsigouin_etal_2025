"""
Plots fig 06 in Dunn-Sigouin et al. 
"""

import numpy         as np
import xarray        as xr
from matplotlib      import pyplot as plt
import cartopy.crs   as ccrs
from forsikring      import misc,s2s,config
from scipy           import signal, ndimage
import matplotlib    as mpl

def setup_subplot_xy(ax, ds1, ds2, clevs, cmap, fontsize, title):
    """ 
    Sets up specifics of subplots for fig.06
    """
    lat   = ds2.latitude
    lon   = ds2.longitude

    p = ax.contourf(lon, lat, ds2,levels=clevs,cmap=cmap,extend='max',transform=ccrs.PlateCarree())
    ax.contour(lon, lat, ds2, levels=clevs,colors = [(1.0,1.0,1.0)],linewidths=0.5,transform=ccrs.PlateCarree())

    #rectangle = plt.Rectangle((31.75, 72.75), 0.25, 0.25, angle=180, fc=(0.5,0.5,0.5,0),ec='r',lw=2)
    ds1 = ds1  > 0.5
    ds1 = ds1.where(ds1, np.nan)
    ax.pcolor(lon, lat, ds1, hatch='..', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[1.0,0.0,0.0], lw=0)
        
    ax.coastlines(color='k',linewidth=1)
    ax.set_title(title,fontsize=fontsize+5)
    #ax.add_patch(rectangle)
    
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
filename1        = config.dirs['era5_forecast_' + time_flag] + '/' + variable + '/' + variable + '_' + grid + '_' + date + '.nc'
filename2        = config.dirs['era5_forecast_' + time_flag + '_binary'] + '0.9/' + domain + '/' + variable + '/' + variable + '_' + grid + '_' + date + '.nc'
path_out         = config.dirs['fig'] + 'paper/'
figname_out      = 'fig_05.png'

# read in data
da1 = xr.open_dataset(filename1).sel(time=date)
da2 = xr.open_dataset(filename2).sel(time=date).sel(box_size=1)

# extract specified domain
dim = misc.subselect_xy_domain_from_dim(dim,domain,grid)
da1 = da1.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da2 = da2.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')

# convert to mm/day
da1[variable] = da1[variable]*1000

# plot 
fontsize = 11
clevs    = np.arange(5,55,5)
cmap     = 'GnBu'
figsize  = np.array([1.61*7,7])
fig,ax   = plt.subplots(nrows=1,ncols=1,figsize=(figsize[0],figsize[1]),subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0.0)})

fig.subplots_adjust(right=1.0, left=0.0,top=0.9,bottom=0.15)

title = r'Storm Hans August 7$^{th}$ 2023'
p = setup_subplot_xy(ax, da2[variable], da1[variable], clevs, cmap, fontsize, title)

cbar_ax = fig.add_axes([0.152, 0.05, 0.697, 0.04])
cb = fig.colorbar(p, cax=cbar_ax, orientation='horizontal',ticks=clevs, pad=0.025)
cb.ax.tick_params(labelsize=fontsize, size=0)
cb.ax.set_title('daily accumulated precipitation [mm/day]', fontsize=fontsize+4,y=1.01)

#plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()


