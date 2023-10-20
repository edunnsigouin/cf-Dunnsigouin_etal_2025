"""
Plots xy with coastlines of a given domain
"""

import numpy         as np
import xarray        as xr
from matplotlib      import pyplot as plt
import cartopy.crs   as ccrs
from forsikring      import misc,s2s,config
from scipy           import signal, ndimage

# INPUT -----------------------
domain            = 'scandinavia'            # europe/nordic/vestland                       
write2file        = False
# -----------------------------

# define stuff for dummy data
variable          = 'tp24'  
date              = '2023-08-09'
grid              = '0.25x0.25'    
dim               = misc.get_dim(grid,'time')
path_in           = config.dirs['era5_daily'] + variable + '/'
path_out          = config.dirs['fig'] + 'era5/' + variable + '/'
filename_in       = variable + '_' + grid + '_2023.nc'
figname_out       = 'xy_' + variable + '_' + grid + '_' + domain + '_' + date + '.pdf'


# read in dummy data
da = xr.open_dataset(path_in + filename_in).sel(time=date)[variable] # lead time indexing starts at day 0 (lead time 1 day)

# extract specified domain
dim     = misc.subselect_xy_domain_from_dim(dim,domain,grid)
da      = da.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')

# plot 
fontsize = 11
clevs    = np.arange(5,55,5)
cmap     = 'GnBu'
figsize  = np.array([1.618*4,4])
fig,ax   = plt.subplots(nrows=1,ncols=1,figsize=(figsize[0],figsize[1]),\
                        subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0.0)})

p0 = ax.contourf(dim.longitude,dim.latitude,da*np.nan,levels=clevs,cmap=cmap,extend='max',transform=ccrs.PlateCarree())
ax.coastlines('10m',color='k')
ax.set_aspect('auto')


plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()


