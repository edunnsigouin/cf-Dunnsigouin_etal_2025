"""
Plots xy anomalies of a given variable from a day in era5
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
variable          = 'tp24'              # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'nordic'            # europe/nordic/vestland                       
date              = '2023-08-07'        # initialization date
grid              = '0.25x0.25'         # '0.25x0.25' or '0.5x0.5'
NH                = np.array([1,9,19,29,39,49,59])
iNH               = 1
write2file        = True
# -----------------------------

# define stuff
dim         = s2s.get_dim(grid,'time')
path_in     = config.dirs['era5_cont_daily'] + variable + '/'
path_out    = config.dirs['fig'] + 'era5/' + variable + '/'
filename_in = variable + '_' + grid + '_2023.nc'
figname_out = 'xy_example_' + variable + '_' + grid + '_' + domain + '_' + date + '_NH_' + str(NH[iNH]) + '.pdf'

# read in data & take ensemble mean
da = xr.open_dataset(path_in + filename_in).sel(time=date)[variable] # lead time indexing starts at day 0 (lead time 1 day)

# modify units
if variable == 'tp24':
    da[:,:] = da[:,:]*1000
    units   = 'mm/day'

# smooth in 2D and dump back into da 
da_frac = calc_frac_RL08MWR(NH,da)
da[:,:] = da_frac[iNH,:,:]

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

p0 = ax.contourf(dim.longitude,dim.latitude,da,levels=clevs,cmap=cmap,extend='max',transform=ccrs.PlateCarree())
ax.contour(dim.longitude,dim.latitude,da,levels=clevs,colors='grey',linewidths=0.5,linestyles='-',transform=ccrs.PlateCarree())
ax.coastlines()
ax.set_aspect('auto')
cb0 = fig.colorbar(p0, ax=ax, orientation='vertical',ticks=clevs.astype(int),pad=0.025,aspect=15)
cb0.ax.set_title('[' + units + ']',fontsize=fontsize)
cb0.ax.tick_params(labelsize=fontsize,size=0)
#ax.set_title('era5 date = ' + date,fontsize=fontsize)

plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()


