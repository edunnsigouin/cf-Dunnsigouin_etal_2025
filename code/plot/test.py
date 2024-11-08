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

def setup_subplot_xy(flag, ax, ds1, ds2, clevs, cmap, fontsize, title, stats):
    """ 
    Sets up specifics of subplots for fig.05
    """
    lat   = ds2.latitude
    lon   = ds2.longitude

    p = ax.contourf(lon, lat, ds2,levels=clevs,cmap=cmap,extend='max',transform=ccrs.PlateCarree())
    ax.contour(lon, lat, ds2, levels=clevs,colors = [(1,1,1)],linewidths=0.5,transform=ccrs.PlateCarree())

    if flag < 7:
        ds1 = ds1  > 0.8
        ds1 = ds1.where(ds1, np.nan)
        ax.pcolor(lon, lat, ds1, hatch='..', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[1.0,0.0,0.0], lw=0)
        rectangle_length = 0.25*ds2['box_size']
        rectangle = plt.Rectangle((31.75, 72.75), rectangle_length, rectangle_length, angle=180, fc=(0.5,0.5,0.5,0),ec='r',lw=2)
        ax.add_patch(rectangle)        
        ax.text(0.1,0.865,stats,fontsize=fontsize+2,transform=ax.transAxes)
    else:
        rectangle = plt.Rectangle((31.75, 72.75), 0.25, 0.25, angle=180, fc=(0.5,0.5,0.5,0),ec='r',lw=2)
        ax.add_patch(rectangle)
        
    ax.coastlines(color='k',linewidth=1)
    ax.set_title(title, fontsize=fontsize + 4,loc='left', ha='left', y=0.89, x=0.02, bbox={'facecolor': 'white', 'edgecolor': 'black', 'pad': 3})    
    
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
filename1        = config.dirs['s2s_forecast_' + time_flag + '_EFI'] + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-03_EFI.nc'
filename2        = config.dirs['s2s_forecast_' + time_flag + '_EFI'] + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-03_EFI.nc'
filename3        = config.dirs['s2s_forecast_' + time_flag + '_EFI'] + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-05_EFI.nc'
filename4        = config.dirs['s2s_forecast_' + time_flag + '_EFI'] + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-05_EFI.nc'
filename5        = config.dirs['s2s_forecast_' + time_flag + '_EFI'] + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-07_EFI.nc'
filename6        = config.dirs['s2s_forecast_' + time_flag + '_EFI'] + domain + '/' + variable + '/' + 'tp24_0.25x0.25_2023-08-07_EFI.nc'
filename7        = config.dirs['era5_forecast_' + time_flag] + '/' + variable + '/' + variable + '_' + grid + '_' + date + '.nc'
path_out         = config.dirs['fig'] + 'paper/'
figname_out      = 'fig_06-test.png'

# read in data
da1 = xr.open_dataset(filename1).sel(time=date).sel(box_size=1)
da2 = xr.open_dataset(filename2).sel(time=date).sel(box_size=33)
da3 = xr.open_dataset(filename3).sel(time=date).sel(box_size=1)
da4 = xr.open_dataset(filename4).sel(time=date).sel(box_size=19)
da5 = xr.open_dataset(filename5).sel(time=date).sel(box_size=1)
da6 = xr.open_dataset(filename6).sel(time=date).sel(box_size=9)
da7 = xr.open_dataset(filename7).sel(time=date)

# extract specified domain
dim = misc.subselect_xy_domain_from_dim(dim,domain,grid)
da1 = da1.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da2 = da2.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da3 = da3.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da4 = da4.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da5 = da5.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da6 = da6.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da7 = da7.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')

# convert to mm/day 
da7[variable] = da7[variable]*1000

# plot 
fontsize = 11
clevs    = np.arange(5,55,5)
cmap     = 'GnBu'
figsize  = np.array([12,16])
fig,ax   = plt.subplots(nrows=4,ncols=2,figsize=(figsize[0],figsize[1]),subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0.0)})
ax       = ax.ravel()


fig.subplots_adjust(top=0.9, bottom=0.05, left=0.15, right=0.98, hspace=0.02, wspace=0.02)

title1 = r'a) 1 gridpoint$^2$ precision'
title2 = r'b) 33 gridpoint$^2$ precision'
title3 = r'c) 1 gridpoint$^2$ precision'
title4 = r'd) 19 gridpoint$^2$ precision'
title5 = r'e) 1 gridpoint$^2$ precision'
title6 = r'f) 9 gridpoint$^2$ precision'
title7 = r'g) 1 gridpoint$^2$ precision'

stats1 = r'FMSESS = ' + str(da1['fmsess'].values.round(2)) + '\nFBSS$_{0.9}$ = ' + str(da1['fbss'].values.round(2))
stats2 = r'FMSESS = ' + str(da2['fmsess'].values.round(2)) + '\nFBSS$_{0.9}$ = ' + str(da2['fbss'].values.round(2))
stats3 = r'FMSESS = ' + str(da3['fmsess'].values.round(2)) + '\nFBSS$_{0.9}$ = ' + str(da3['fbss'].values.round(2))
stats4 = r'FMSESS = ' + str(da4['fmsess'].values.round(2)) + '\nFBSS$_{0.9}$ = ' + str(da4['fbss'].values.round(2))
stats5 = r'FMSESS = ' + str(da5['fmsess'].values.round(2)) + '\nFBSS$_{0.9}$ = ' + str(da5['fbss'].values.round(2))
stats6 = r'FMSESS = ' + str(da6['fmsess'].values.round(2)) + '\nFBSS$_{0.9}$ = ' + str(da6['fbss'].values.round(2))

setup_subplot_xy(1, ax[0], da1['EFI'], da1[variable], clevs, cmap, fontsize, 'a)', stats1)
setup_subplot_xy(2, ax[1], da2['EFI'], da2[variable], clevs, cmap, fontsize, 'b)', stats2)
setup_subplot_xy(3, ax[2], da3['EFI'], da3[variable], clevs, cmap, fontsize, 'c)', stats3)
setup_subplot_xy(4, ax[3], da4['EFI'], da4[variable], clevs, cmap, fontsize, 'd)', stats4)
setup_subplot_xy(5, ax[4], da5['EFI'], da5[variable], clevs, cmap, fontsize, 'e)', stats5)
p = setup_subplot_xy(6, ax[5], da6['EFI'], da6[variable], clevs, cmap, fontsize, 'f)', stats6)
setup_subplot_xy(7, ax[6], da5['EFI'], da7[variable], clevs, cmap, fontsize, 'g)', stats5)

ax[7].set_frame_on(False)

#cbar_ax = fig.add_axes([0.52, 0.2, 0.4, 0.02])
cbar_ax = fig.add_axes([0.55, 0.03, 0.35, 0.02])
cb = fig.colorbar(p, cax=cbar_ax, orientation='horizontal',ticks=clevs, pad=0.025)
cb.ax.tick_params(labelsize=fontsize+2, size=0)
cb.ax.set_title('daily accumulated precipitation [mm/day]', fontsize=fontsize+5,y=1.01)

# figure labels
nrows = 4
y_positions = [1 - (i + 0.5) / nrows for i in range(nrows)]  # Centered vertically per row
labels = ['forecast lead day 5', 'forecast lead day 3', 'forecast lead day 1', 'Storm Hans August 7th 2023']

for y, label in zip(y_positions, labels):
    fig.text(0.01, y, label, fontsize=fontsize + 5, va='center', ha='right', rotation=90)

ncols = 2
x_positions = [(i + 0.5) / ncols for i in range(ncols)]  # Centered above each column
top_labels = ['grid scale precision', 'optimized spatial precision']

# Place text at the top of the figure centered above each column
for x, label in zip(x_positions, top_labels):
    fig.text(x, 0.99, label, fontsize=fontsize + 5, va='bottom', ha='center')  # Adjust y-position if needed
    
plt.tight_layout()

if write2file: plt.savefig(path_out + figname_out,bbox_inches='tight')
plt.show()


