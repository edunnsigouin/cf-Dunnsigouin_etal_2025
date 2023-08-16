"""
Plots xy anomalies of a given variable from a single forecast at a given
lead time.
"""

import numpy         as np
import xarray        as xr
from matplotlib      import pyplot as plt
import cartopy.crs   as ccrs
from forsikring      import misc,s2s,config
from scipy           import signal, ndimage

def calc_frac_RL08MWR(NH,da):
    """ 
    Generates fractions following equations 2 and 3 from 
    Roberts and Lean 2008 MWR.
    Specifically, smooths 2D x,y fields using a boxcar smoother.
    Here, last two dimensions of 'da' are latitude and longitude.
    Note: only performs calculation on odd sized neighborhoods
    """
    frac = np.zeros((NH.size,) + da.shape)
    for n in range(0,NH.size,1):
        if NH[n] % 2 != 0: # odd
            kernel          = np.ones((NH[n],NH[n]))
            #kernel          = kernel[None,None,:,:]
            frac[n,:,:] = ndimage.convolve(da.values, kernel, mode='constant', cval=0.0, origin=0)/NH[n]**2
        else: # even
            frac[n,:,:] = np.nan
    return frac

# INPUT -----------------------
time_flag         = 'time'              # time or timescale
variable          = 'tp24'              # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'europe'            # europe/nordic/vestland                       
init_start        = '2021-01-04'        # initialization date
leadtime_day      = 5                   # lead time in days
grid              = '0.25x0.25'         # '0.25x0.25' or '0.5x0.5'
NH                = np.array([1,9,19,29,39,49,59])
write2file        = False
# -----------------------------

# define stuff
dim         = s2s.get_dim(grid,'time')
path_in     = config.dirs['forecast_daily_anomaly'] + variable + '/'
path_out    = config.dirs['fig'] + 'ecmwf/forecast/daily/' + variable + '/'
filename_in = variable + '_' + time_flag + '_' + grid + '_' + init_start + '.nc'
figname_out = 'xy_' + variable + '_anomaly_' + grid + '_' + domain + '_init_' + init_start + '_leadtimeday_' + str(leadtime_day) + '_NH_' + str(NH[0]) + '.pdf'

# read in data
da    = xr.open_dataset(path_in + filename_in).isel(time=leadtime_day-1)[variable] # lead time indexing starts at day 0 (lead time 1 day)
units = da.attrs['units']

# extract specified domain
dim  = misc.subselect_xy_domain_from_dim(dim,domain,grid)
da   = da.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')

print(np.count_nonzero(np.isnan(da.values)))

"""
# modify units
if units == 'm':
    da[:,:] = da[:,:]*1000
    units     = 'mm/day'
    
# smooth in 2D
da_frac = calc_frac_RL08MWR(NH,da)

# plot 
fontsize = 11
clevs    = np.arange(-42,46,4)
cmap     = 'BrBG'
figsize  = np.array([6,4])
fig,ax   = plt.subplots(nrows=1,ncols=1,figsize=(figsize[0],figsize[1]),\
                        subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0.0)})

# era5
p0 = ax.contourf(dim.longitude,dim.latitude,da,levels=clevs,cmap=cmap,extend='both',transform=ccrs.PlateCarree())
ax.coastlines()
ax.set_aspect('auto')
cb0 = fig.colorbar(p0, ax=ax, orientation='vertical',ticks=clevs[::2].astype(int),pad=0.025,aspect=15)
cb0.ax.set_title('[' + units + ']',fontsize=fontsize)
cb0.ax.tick_params(labelsize=fontsize,size=0)
#ax.set_title('era5 date = ' + date,fontsize=fontsize)

plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()
"""

