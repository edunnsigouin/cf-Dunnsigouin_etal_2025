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
time_flag         = 'time'                   # time or timescale
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'europe'                 # europe/nordic/vestland                       
init_start        = '20210104'               # first initialization date of forecast (either a monday or thursday)
init_n            = 104                      # number of weeks with forecasts
pval              = 0.9
write2file        = True
# -----------------------------

# define stuff         
init_dates       = s2s.get_init_dates(init_start,init_n)
init_dates       = init_dates.strftime('%Y-%m-%d').values
path_in          = config.dirs['verify_forecast_daily']
path_out         = config.dirs['fig'] + 'ecmwf/forecast/daily/'
filename_in      = time_flag + '_fss_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
                   'pval_' + str(0.9) + '_0.25x0.25_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
figname_out      = 'cmap_' + time_flag + '_fss_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
                   'pval_' + str(0.9) + '_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.pdf'

# read in data
ds   = xr.open_dataset(path_in + filename_in)
fss  = ds['fss'].values
sig  = (ds['fss_bs'].quantile(0.05,dim='number').values < 0).astype(np.int32) # when 5th percentile crosses zero
x    = ds['neighborhood'].values
t    = ds['time'].values
ds.close()

# plot 
fontsize = 11
clevs    = np.arange(-1.0,1.1,0.1)
cmap     = 'RdBu_r'
figsize  = np.array([4*1.61,4])
fig,ax   = plt.subplots(nrows=1,ncols=1,figsize=(figsize[0],figsize[1]))

if time_flag == 'time':
    p = ax.contourf(t,x,fss,levels=clevs,cmap=cmap,extend='both')
    ax.contour(t,x,fss,levels=clevs,colors='grey',linewidths=1.0)
    ax.contourf(t,x,sig,levels=1,colors='none',hatches=["", "///"])
    plt.rcParams['hatch.linewidth'] = 0.25
    ax.set_xticks(t)
    ax.set_xticklabels(t,fontsize=fontsize)
    ax.set_xlabel(r'lead time [days]',fontsize=fontsize)

elif time_flag == 'timescale':
    print('needs to be coded..')
    
cb = fig.colorbar(p, ax=ax, orientation='vertical',ticks=clevs[0::2],pad=0.025,aspect=15)
cb.ax.set_title('fss',fontsize=fontsize)
cb.ax.tick_params(labelsize=fontsize,size=0)
ax.set_yticks(x)
ax.set_yticklabels(['1/18','9/162','19/342','29/522','39/702','49/882','59/1062'],fontsize=fontsize)
ax.set_ylabel(r'spatial scale [grid points/km$^2$]',fontsize=fontsize)

plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()


