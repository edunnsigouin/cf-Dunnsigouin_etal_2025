"""
Plots an example of the fraction skill score calculated 
for anomalies using seasonal forecast data
"""

import numpy     as np
import xarray    as xr
import pandas    as pd
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config
import matplotlib as mpl

# INPUT -----------------------
variable            = 'tp'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain              = 'europe'                 # europe/nordic/vestland                       
first_forecast_date = '2017-01'
number_forecasts    = 72
write2file          = True
# -----------------------------

# define stuff         
forecast_dates = pd.date_range(first_forecast_date,periods=number_forecasts,freq="M").strftime('%Y-%m').values
path_in        = config.dirs['verify_seasonal_forecast_monthly'] 
path_out       = config.dirs['fig'] + 'seasonal/ecmwf/monthly/forecast/'
filename_in    = 'time_fss_seasonal_forecast_' + variable + '_anomaly_' + domain + '_' + \
                  forecast_dates[0] + '_' + forecast_dates[-1] + '.nc'
figname_out    = 'time_fss_seasonal_forecast_' + variable + '_anomaly_' + domain + '_' + \
                  forecast_dates[0] + '_' + forecast_dates[-1] + '.pdf'

# read in data
ds   = xr.open_dataset(path_in + filename_in)
fss  = ds['fss'].values
x    = ds['box_size'].values
t    = ds['time'].values
x2   = np.array([1,9,19,29,39,49,59])


# calculate significance
temp = ds['fss_bootstrap'].quantile(0.05,dim='number_shuffle_bootstrap',skipna=True).values
sig  = (temp < 0).astype(np.int32) # when 5th percentile crosses zero
sig  = np.ma.masked_less(sig, 0.5)

# plot 
fontsize = 11
clevs    = np.arange(0.0, 1.05, 0.05)
cmap     = mpl.cm.get_cmap("RdBu_r").copy()
cmap.set_bad(color=[0.8,0.8,0.8]) # set nans to specified color
figsize  = np.array([6*1.61,6])
fig,ax   = plt.subplots(nrows=1,ncols=1,figsize=(figsize[0],figsize[1]))

p = ax.contourf(t,x,fss,levels=clevs,cmap=cmap,extend='both')
ax.pcolor(t, x, sig, hatch='\\\\',cmap=mpl.colors.ListedColormap(['none']),edgecolor=[0.8,0.8,0.8],lw=0)

ax.set_xticks(t)
ax.set_xticklabels(t,fontsize=fontsize)
ax.set_xlabel(r'lead time [months]',fontsize=fontsize)

ax.set_yticks(x2)
ax.set_yticklabels(['1x1','9x9','19x19','29x29','39x39','49x49','59x59'],fontsize=fontsize)
ax.set_ylabel(r'spatial scale [grid points or degrees$^{\circ}$]',fontsize=fontsize)
ax.set_xlim([1,6])
ax.set_ylim([x[0],x[-1]])

cb = fig.colorbar(p, ax=ax, orientation='vertical',ticks=clevs[::4],pad=0.025,aspect=15)
cb.ax.set_title('fss',fontsize=fontsize)
cb.ax.tick_params(labelsize=fontsize,size=0)

plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()


