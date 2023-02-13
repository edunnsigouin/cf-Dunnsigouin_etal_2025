"""
plots mean-square-error skill score as a function of lead time for 
ecmwf forecasts relative to reference forecasts era5 climatology 
or era5 persistence
"""

import numpy  as np
import xarray as xr
from dask.diagnostics   import ProgressBar
from forsikring import config,misc,s2s
from matplotlib         import pyplot as plt

# INPUT -----------------------------------------------
ref_forecast_flag = 'clim' 
variable          = 'tp24'                    # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
dates             = ['2021-01-04','2021-12-30'] # first monday & thursday initialization date of forecast
comp_lev          = 5
write2file        = False
# -----------------------------------------------------      

# read hr and lr files and combine
path_in         = config.dirs['calc_forecast_daily'] + variable + '/'
filename_hr     = 't_msess_' + ref_forecast_flag + '_0.25x0.25_' + dates[0] + '_' + dates[-1] + '.nc'
filename_lr     = 't_msess_' + ref_forecast_flag + '_0.5x0.5_' + dates[0] + '_' + dates[-1] + '.nc'
ds              = xr.open_mfdataset([path_in + filename_hr,path_in + filename_lr]).compute()
        
# plot
fontsize  = 11
figsize   = np.array([4*1.61,4])
fig,ax    = plt.subplots(nrows=1,ncols=1,figsize=(figsize[0],figsize[1]))
ax.plot(ds['msess'],'k',linewidth=1.25)
ax.plot(ds['msess'],'ko',markersize=5)
ax.set_xticks(np.arange(0,46,5))
ax.set_xticklabels(np.arange(0,46,5))
ax.set_yticks(np.round(np.arange(-0.2,1.2,0.2),2))
ax.set_yticklabels(np.round(np.arange(-0.2,1.2,0.2),2))
ax.set_xlim([0,45])
ax.set_ylim([-0.2,1.0])
ax.set_ylabel('msess',fontsize=fontsize)
ax.set_xlabel('lead time [days]',fontsize=fontsize)
ax.axhline(y=0, color='k', linestyle='-',linewidth=0.75)
plt.show()


ds.close()

        
