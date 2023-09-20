"""
plots mean-square-error skill score as a function of lead time for 
ecmwf forecasts relative to reference forecasts era5 climatology 
or era5 persistence
"""

import numpy     as np
import xarray    as xr
from forsikring  import config,misc,s2s
from matplotlib  import pyplot as plt

# INPUT -----------------------------------------------
time_flag         = 'timescale'
RF_flag           = 'clim' 
variable          = 'tp24'                      # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'europe'                     # nordic only or europe?
init_start        = '20210104'                   # first initialization date of forecast (either a monday or thursday)  
init_n            = 104                          # number of weeks with forecasts    
comp_lev          = 5
write2file        = False
# -----------------------------------------------------      

# define stuff
init_dates       = s2s.get_init_dates(init_start,init_n)
init_dates       = init_dates.strftime('%Y-%m-%d').values
path_in          = config.dirs['calc_forecast_daily']
path_out         = config.dirs['fig'] + 'ecmwf/forecast/daily/'
filename_in      = time_flag + '_msess_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
                   domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
figname_out      = time_flag + '_msess_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
                   domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.pdf'

# read in data
ds       = xr.open_dataset(path_in + filename_in)
msess    = ds['msess']
msess_bs = ds['msess_bs']
ds.close()

# define error bar quantities (mean + 5th and 95th percentiles) 
y          = msess.values
yerr1      = y - msess_bs.quantile(0.05,dim='number').values
yerr2      = msess_bs.quantile(0.95,dim='number').values - y
x          = msess.time

# plot
fontsize  = 11
figsize   = np.array([4*1.61,4])
fig,ax    = plt.subplots(nrows=1,ncols=1,figsize=(figsize[0],figsize[1]))

ax.errorbar(x,y,yerr=[yerr1,yerr2],fmt='o',c='k',ecolor='gray',elinewidth=2,linestyle='-')
if time_flag == 'time':
    ax.set_xticks(np.arange(0,46,5))
    ax.set_xticklabels(np.arange(0,46,5),fontsize=fontsize)
    ax.set_xlim([0,46])
    ax.set_xlabel('lead time [days]',fontsize=fontsize)
elif time_flag == 'timescale':
    ax.set_xticks(np.arange(1,7,1))
    ax.set_xticklabels(['1d1d','2d2d','4d4d','1w1w','2w2w','4w3w'],fontsize=fontsize)
    ax.set_xlim([0.75,6.25])
    ax.set_xlabel('lead time [timescale]',fontsize=fontsize)
    
ax.set_yticks(np.round(np.arange(-1.0,1.2,0.2),2))
ax.set_yticklabels(np.round(np.arange(-1.0,1.2,0.2),2))
ax.set_ylim([-0.25,1.0])
ax.set_ylabel('msess',fontsize=fontsize)
ax.axhline(y=0, color='k', linestyle='-',linewidth=0.75)

plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()

ds.close()

        
