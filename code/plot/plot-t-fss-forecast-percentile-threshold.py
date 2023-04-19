"""
Plots an example of the fraction skill score calculated 
for one forecast with one threshold for tp24
"""

import numpy     as np
import xarray    as xr
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config

# INPUT -----------------------
RF_flag           = 'clim'                   # clim or pers 
time_flag         = 'timescale'                   # time or timescale
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'europe'                 # europe/nordic/vestland                       
init_start        = '20210104'               # first initialization date of forecast (either a monday or thursday)
init_n            = 104                        # number of weeks with forecasts
pval              = 0.9
write2file        = False
# -----------------------------

# define stuff         
init_dates       = s2s.get_init_dates(init_start,init_n)
init_dates       = init_dates.strftime('%Y-%m-%d').values
path_in          = config.dirs['verify_forecast_daily']
path_out         = config.dirs['fig'] + 'ecmwf/forecast/daily/'
filename_in      = time_flag + '_fss_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
                   'pval_' + str(0.9) + '_0.25x0.25_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
figname_out      = time_flag + '_fss_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
                   'pval_' + str(0.9) + '_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.pdf'

# read in data
ds     = xr.open_dataset(path_in + filename_in)
fss    = ds['fss']
fss_bs = ds['fss_bs']
ds.close()

# define error bar quantities (mean + 5th and 95th percentiles) 
y          = fss.values
yerr1      = y - fss_bs.quantile(0.05,dim='number').values
yerr2      = fss_bs.quantile(0.95,dim='number').values - y
x          = fss.neighborhood

# plot 
fontsize = 11
figsize  = np.array([4*1.61,4])
fig,ax   = plt.subplots(nrows=1,ncols=1,figsize=(figsize[0],figsize[1]))

if time_flag == 'time':
    ax.errorbar(x-1.5,y[:,0],yerr=[yerr1[:,0],yerr2[:,0]],fmt='o',c='k',ecolor='k',elinewidth=2,label='1 day',linestyle='-')
    ax.errorbar(x-0.75,y[:,1],yerr=[yerr1[:,1],yerr2[:,1]],fmt='o',c='tab:blue',ecolor='tab:blue',elinewidth=2,label='5 day',linestyle='-')
    ax.errorbar(x,y[:,2],yerr=[yerr1[:,2],yerr2[:,2]],fmt='o',c='tab:green',ecolor='tab:green',elinewidth=2,label='10 day',linestyle='-')
    ax.errorbar(x+0.75,y[:,3],yerr=[yerr1[:,3],yerr2[:,3]],fmt='o',c='tab:red',ecolor='tab:red',elinewidth=2,label='15 day',linestyle='-')
elif time_flag == 'timescale':
    ax.errorbar(x-1.5,y[:,0],yerr=[yerr1[:,0],yerr2[:,0]],fmt='o',c='k',ecolor='k',elinewidth=2,label='1d1d',linestyle='-')
    ax.errorbar(x-0.75,y[:,1],yerr=[yerr1[:,1],yerr2[:,1]],fmt='o',c='tab:blue',ecolor='tab:blue',elinewidth=2,label='2d2d',linestyle='-')
    ax.errorbar(x,y[:,2],yerr=[yerr1[:,2],yerr2[:,2]],fmt='o',c='tab:green',ecolor='tab:green',elinewidth=2,label='4d4d',linestyle='-')
    ax.errorbar(x+0.75,y[:,3],yerr=[yerr1[:,3],yerr2[:,3]],fmt='o',c='tab:red',ecolor='tab:red',elinewidth=2,label='1w1w',linestyle='-')
    
ax.legend(frameon=False,ncol=4,fontsize=fontsize,loc='lower center')
ax.axhline(y=0.0, color='k', linestyle='-',linewidth=0.75)
ax.set_xticks(x)
ax.set_xticklabels(['1/18','9/162','19/342','29/522','39/702','49/882','59/1062'],fontsize=fontsize)
ax.set_yticks(np.round(np.arange(-0.2,1.2,0.2),2))
ax.set_yticklabels(np.round(np.arange(-0.2,1.2,0.2),2),fontsize=fontsize)
ax.set_xlim([-2,52])
ax.set_ylim([-0.3,1.0])
ax.set_xlabel(r'spatial scale [grid squares/km$^2$]',fontsize=fontsize)
ax.set_ylabel('fractions skill score',fontsize=fontsize)
    
plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()


