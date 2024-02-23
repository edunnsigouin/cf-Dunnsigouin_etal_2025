"""

"""

import numpy         as np
import xarray        as xr
from matplotlib      import pyplot as plt
import cartopy.crs   as ccrs
from forsikring      import misc,s2s,config

def setup_subplot_xy(flag, ax, ds, clevs, cmap, fontsize, title):
    """
    Sets up specifics of subplots for fig.05 
    """
    lat   = ds.latitude
    lon   = ds.longitude

    p = ax.contourf(lon, lat, ds,levels=clevs,cmap=cmap,extend='max',transform=ccrs.PlateCarree())
    ax.contour(lon, lat, ds, levels=clevs,colors = [(0.5,0.5,0.5)],linewidths=0.5,transform=ccrs.PlateCarree())
    ax.coastlines(color='k',linewidth=1)

    """
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
    """
    return p



# INPUT -----------------------
time_flag         = 'daily'              # time or timescale
variable          = 'tp24'              # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'scandinavia'            # europe/nordic/vestland                       
init_date         = '2021-01-07'        # initialization date
grid              = '0.25x0.25'         # '0.25x0.25' or '0.5x0.5'
pval              = 0.9
box_size          = 17
write2file        = True
# -----------------------------

# define stuff
dim         = misc.get_dim(grid,time_flag)
path_in1    = config.dirs['s2s_forecast_daily_smooth'] + variable + '/'
path_in2    = config.dirs['s2s_forecast_daily_probability'] + str(pval) + '/' + domain + '/' + variable + '/'
path_out    = config.dirs['fig'] + 's2s/ecmwf/daily/forecast/'
filename_in = variable + '_' + grid + '_' + init_date + '.nc'
figname_out = 'xy_example_' + variable + '_' + grid + '_' + domain + '_init_' + init_date + '.pdf'

# read in data 
da1 = xr.open_dataset(path_in1 + filename_in).isel(time=3).isel(box_size=0).mean(dim='number')[variable] 
da2 = xr.open_dataset(path_in1 + filename_in).isel(time=3).sel(box_size=box_size).mean(dim='number')[variable]
da3 = xr.open_dataset(path_in2 + filename_in).isel(time=3).sel(box_size=box_size)[variable]

# modify units to mm/day
da1 = da1*1000
da2 = da2*1000

# extract specified domain
dim     = misc.subselect_xy_domain_from_dim(dim,domain,grid)
da1     = da1.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da2     = da2.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da3     = da3.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')


fontsize   = 11
clevs_rain = np.arange(1,11,1)
clevs_prob = np.arange(0,1.2,0.2)
cmap_rain  = 'GnBu'
cmap_prob  = 'Reds'
figsize    = np.array([12,4])
fig,ax     = plt.subplots(nrows=1,ncols=3,figsize=(figsize[0],figsize[1]),subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0.0)})
ax         = ax.ravel()

title1 = ''
title2 = ''
title3 = ''

setup_subplot_xy(1, ax[0], da1, clevs_rain, cmap_rain, fontsize, title1)
setup_subplot_xy(2, ax[1], da2, clevs_rain, cmap_rain, fontsize, title2)
setup_subplot_xy(3, ax[2], da3, clevs_prob, cmap_prob, fontsize, title3)

fig.subplots_adjust(left=0.05,right=0.95, top=0.95, hspace=0,wspace=0.02)
if write2file: plt.savefig(path_out + figname_out)
plt.show()
