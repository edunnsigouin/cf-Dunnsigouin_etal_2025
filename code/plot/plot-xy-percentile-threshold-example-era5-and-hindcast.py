"""
Plots two xy maps of era5 and hincast climatological percentile thresholds
for a given forecast initialization date and lead time.
e.g., forecast initialized on 2021-01-04 with lead time 5 days will plot era5 clim on 01-09 
calculated over years 2001-2020 and hindcast clim 01-09 based on the hindcasts initialized on 01-04 from years 2001-2020.  
"""

import numpy         as np
import xarray        as xr
from matplotlib      import pyplot as plt
import cartopy.crs   as ccrs
from forsikring      import misc,s2s,config

# INPUT -----------------------
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'europe'                 # europe/nordic/vestland                       
years             = np.arange(2001,2021,1)   # years for threshold data
init_start        = '2021-01-04'               # initialization date
ltime             = 5                        # lead time in days
grid              = '0.25x0.25'              # '0.25x0.25' or '0.5x0.5'
pval              = 0.95
write2file        = False
# -----------------------------

# define stuff
dim           = s2s.get_dim(grid,'time')
path_in_O     = config.dirs['era5_percentile'] + variable + '/'
filename_in_O = 'xyt_percentile_' + variable + '_' + grid + '_' + str(years[0]) + '-' + str(years[-1]) + '.nc'
path_in_H     = config.dirs['hindcast_percentile'] + variable + '/'
filename_in_H = 'xyt_percentile_' + variable + '_' + grid + '_' + init_start + '.nc'
path_out      = config.dirs['fig'] + 'era5_and_ecmwf/' + variable + '/'
figname_out   = 'example_xy_' + variable + '_pval' + str(pval) + '_' + grid + '_' + domain + '_init_' + init_start + '_ltime_' + str(ltime) + 'day.pdf'

# read in data
da_O  = xr.open_dataset(path_in_O + filename_in_O).sel(pval=pval)['percentile']
units = da_O.attrs['units']
da_H  = xr.open_dataset(path_in_H + filename_in_H).sel(pval=pval)['percentile']

# select data at given lead time (hindcast) and corresponding calendar day (era5)
da_H = da_H.isel(time=ltime)
date = da_H.time.values.astype('datetime64[D]').astype('str')
da_O = da_O.sel(time=date).squeeze()

# extract specified domain
dim  = misc.subselect_xy_domain_from_dim(dim,domain,grid)
da_H = da_H.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
da_O = da_O.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')

# modify units
if units == 'm':
    da_H[:,:] = da_H[:,:]*1000
    da_O[:,:] = da_O[:,:]*1000
    units     = 'mm/day'
    
# plot 
fontsize = 11
clevs    = np.arange(0,45,5)
cmap     = 'GnBu'
figsize  = np.array([7,8])
fig,axes = plt.subplots(nrows=2,ncols=1,figsize=(figsize[0],figsize[1]),\
                        subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0.0)})
axes = axes.ravel()

# era5
p0 = axes[0].contourf(dim.longitude,dim.latitude,da_O,levels=clevs,cmap=cmap,extend='both',transform=ccrs.PlateCarree())
axes[0].coastlines()
axes[0].set_aspect('auto')
cb0 = fig.colorbar(p0, ax=axes[0], orientation='vertical',ticks=clevs.astype(int),pad=0.025,aspect=15)
cb0.ax.set_title('[' + units + ']',fontsize=fontsize)
cb0.ax.tick_params(labelsize=fontsize,size=0)
axes[0].set_title('era5 date = ' + date,fontsize=fontsize)

# hindcast
p1 = axes[1].contourf(dim.longitude,dim.latitude,da_H,levels=clevs,cmap=cmap,extend='both',transform=ccrs.PlateCarree())
axes[1].coastlines()
axes[1].set_aspect('auto')
cb1 = fig.colorbar(p1, ax=axes[1], orientation='vertical',ticks=clevs.astype(int),pad=0.025,aspect=15)
cb1.ax.set_title('[' + units + ']',fontsize=fontsize)
cb1.ax.tick_params(labelsize=fontsize,size=0)
axes[1].set_title('hindcast/forecast initialized = ' + init_start + ', lead time = ' + str(ltime) + 'day',fontsize=fontsize)

plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()


