"""
fig. S5
"""

import numpy         as np
import xarray        as xr
from matplotlib      import pyplot as plt
import cartopy.crs   as ccrs
from Dunnsigouin_etal_2025      import misc,s2s,config
from scipy           import signal, ndimage
import matplotlib    as mpl

def setup_subplot_xy(flag, ax, ds1, ds2, clevs, cmap, fontsize, title, stats):
    """ 
    Sets up specifics of subplots for fig.S5
    """
    lat   = ds2.latitude
    lon   = ds2.longitude

    p = ax.contourf(lon, lat, ds2,levels=clevs,cmap=cmap,extend='max',transform=ccrs.PlateCarree())
    ax.contour(lon, lat, ds2, levels=clevs,colors = [(1,1,1)],linewidths=0.5,transform=ccrs.PlateCarree())

    if flag < 3:
        ds1 = ds1  > 0.8
        ds1 = ds1.where(ds1, np.nan)
        ax.pcolor(lon, lat, ds1, hatch='..', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[1.0,0.0,0.0], lw=0)
        rectangle_length = 0.25*ds2['box_size']
        rectangle = plt.Rectangle((31.75, 72.75), rectangle_length, rectangle_length, angle=180, fc=(0.5,0.5,0.5,0),ec='r',lw=2)
        ax.add_patch(rectangle)        
        ax.text(0.1,0.86,stats,fontsize=fontsize+2,transform=ax.transAxes)
    else:
        ds1 = ds1  > 0.8
        ds1 = ds1.where(ds1, np.nan)
        ax.pcolor(lon, lat, ds1, hatch='..', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[1.0,0.0,0.0], lw=0)
        rectangle_length = 0.25*ds2['box_size']
        rectangle = plt.Rectangle((31.75, 72.75), rectangle_length, rectangle_length, angle=180, fc=(0.5,0.5,0.5,0),ec='r',lw=2)
        ax.add_patch(rectangle)

        
    ax.coastlines(color='k',linewidth=1)
    ax.set_title(title, fontsize=fontsize + 4,loc='left', ha='left', y=0.88, x=0.02, bbox={'facecolor': 'white', 'edgecolor': 'black', 'pad': 3})    
    
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
filename1        = config.dirs['s2s_forecast_' + time_flag + '_EFI'] + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-01_EFI.nc'
filename2        = config.dirs['s2s_forecast_' + time_flag + '_EFI'] + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-01_EFI.nc'
filename3        = config.dirs['era5_forecast_' + time_flag + '_EFI'] + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-07_EFI.nc'
path_out         = config.dirs['fig'] + 'paper/'
figname_out      = 'fig_response_to_reviewers.pdf'

# read in data
da1 = xr.open_dataset(filename1).sel(time=date).sel(box_size=1)
da2 = xr.open_dataset(filename2).sel(time=date).sel(box_size=47)
da3 = xr.open_dataset(filename3).sel(time=date).sel(box_size=1)

# extract specified domain
dim = misc.subselect_xy_domain_from_dim(dim,domain,grid)
da1 = da1.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da2 = da2.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da3 = da3.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')


# plot 
fontsize = 11
clevs    = np.arange(5,55,5)
cmap     = 'GnBu'
figsize  = np.array([10,5])
fig,ax   = plt.subplots(nrows=1,ncols=2,figsize=(figsize[0],figsize[1]),subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0.0)})
ax       = ax.ravel()


fig.subplots_adjust(top=0.95, bottom=0.1, left=0.05, right=0.95,wspace=0.02)

title1 = r'a) 1 gridpoint$^2$ precision'
title2 = r'b) 33 gridpoint$^2$ precision'
title3 = r'c) 1 gridpoint$^2$ precision'
title4 = r'd) 19 gridpoint$^2$ precision'
title5 = r'e) 1 gridpoint$^2$ precision'
title6 = r'f) 9 gridpoint$^2$ precision'
title7 = r'g) 1 gridpoint$^2$ precision'

stats1 = r'FMSESS = ' + str(da1['fmsess'].values.round(2)) + '\nFBSS$_{0.9}$ = ' + str(da1['fbss'].values.round(2))
stats2 = r'FMSESS = ' + str(da2['fmsess'].values.round(2)) + '\nFBSS$_{0.9}$ = ' + str(da2['fbss'].values.round(2))
stats3 = r'FMSESS = ' + str(da1['fmsess'].values.round(2)) + '\nFBSS$_{0.9}$ = ' + str(da1['fbss'].values.round(2))

setup_subplot_xy(1, ax[0], da1['EFI'], da1[variable], clevs, cmap, fontsize, 'a)', stats1)
p = setup_subplot_xy(2, ax[1], da2['EFI'], da2[variable], clevs, cmap, fontsize, 'b)', stats2)


cbar_ax = fig.add_axes([0.25, 0.1, 0.5, 0.05])
cb = fig.colorbar(p, cax=cbar_ax, orientation='horizontal',ticks=clevs, pad=0.025)
cb.ax.tick_params(labelsize=fontsize+5, size=0)
cb.ax.set_title('daily accumulated precipitation [mm/day]', fontsize=fontsize+5,y=1.01)

# figure labels
nrows = 1
y_positions = [1 - (i + 0.47) / nrows for i in range(nrows)]  # Centered vertically per row
labels = ['forecast lead day 7']

for y, label in zip(y_positions, labels):
    fig.text(0.04, y, label, fontsize=fontsize + 5, va='center', ha='right', rotation=90)

#ncols = 2
#x_positions = [(i + 0.5) / ncols for i in range(ncols)]  # Centered above each column
#top_labels = ['grid scale precision', 'optimized accuracy']

#for x, label in zip(x_positions, top_labels):
#    fig.text(x, 0.83, label, fontsize=fontsize + 5, va='bottom', ha='center')  # Adjust y-position if needed

top_labels = ['grid scale precision', 'optimized accuracy']

for i, label in enumerate(top_labels):
    ax[i].text(0.5, 1.02, label, transform=ax[i].transAxes,
               fontsize=fontsize + 5, ha='center', va='bottom')
    
#plt.tight_layout()

if write2file: plt.savefig(path_out + figname_out)
plt.show()



