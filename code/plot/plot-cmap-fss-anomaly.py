"""
Plots an example of the fraction skill score calculated 
for anomalous forecasts 
"""

import numpy     as np
import xarray    as xr
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config
import matplotlib as mpl

# INPUT -----------------------
RF_flag           = 'clim'                   # clim or pers 
time_flag         = 'time'              # time or timescale
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'europe'                 # europe/nordic/vestland                       
init_start        = '20200102'               # first initialization date of forecast (either a monday or thursday)
init_n            = 313                      # number of weeks with forecasts
write2file        = False
# -----------------------------

# define stuff         
init_dates       = s2s.get_init_dates(init_start,init_n)
init_dates       = init_dates.strftime('%Y-%m-%d').values
path_in          = config.dirs['verify_forecast_daily']
path_out         = config.dirs['fig'] + 'ecmwf/forecast/daily/'
if time_flag == 'timescale':
    filename_in      = time_flag + '_fss_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
        'anomaly_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
else:
    filename_in      = time_flag + '_fss_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
        'anomaly_0.25x0.25_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'

figname_out = 'cmap_' + time_flag + '_fss_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
    'anomaly_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.pdf'

# read in data
ds   = xr.open_dataset(path_in + filename_in)
fss  = ds['fss'].values
x    = ds['neighborhood'].values
t    = ds['time'].values
x2   = np.array([1,9,19,29,39,49,59])


# calculate significance
temp = ds['fss_bs'].quantile(0.05,dim='number',skipna=True).values
sig  = (temp < 0).astype(np.int32) # when 5th percentile crosses zero
sig  = np.ma.masked_less(sig, 0.5)

# plot 
fontsize = 11
clevs    = np.arange(0.0, 1.05, 0.05)
cmap     = mpl.cm.get_cmap("RdBu_r").copy()
cmap.set_bad(color=[0.8,0.8,0.8]) # set nans to specified color
figsize  = np.array([6*1.61,6])
fig,ax   = plt.subplots(nrows=1,ncols=1,figsize=(figsize[0],figsize[1]))

#p = ax.pcolormesh(t,x,fss,cmap=cmap,vmin=0.0,vmax=1.0)
p = ax.contourf(t,x,fss,levels=clevs,cmap=cmap)
ax.pcolor(t, x, sig, hatch='\\\\',cmap=mpl.colors.ListedColormap(['none']),edgecolor=[0.8,0.8,0.8],lw=0)
#ax.contour(t, x, sig, hatch='//',cmap=mpl.colors.ListedColormap(['none']),edgecolor=[0.8,0.8,0.8],lw=0)

if time_flag == 'time':
    ax.set_xticks(t)
    ax.set_xticklabels(['1','','3','','5','','7','','9','','11','','13','','15'],fontsize=fontsize)
    ax.set_xlabel(r'lead time [days]',fontsize=fontsize)
elif time_flag == 'timescale':
    ax.set_xticks(t)
    ax.set_xticklabels(['1d1d','2d2d','4d4d','1w1w','2w2w','4w3w'],fontsize=fontsize)
    ax.set_xlabel(r'lead time [timescale]',fontsize=fontsize)

ax.set_yticks(x2)
ax.set_yticklabels(['1x1\n18x18','9x9\n162x162','19x19\n342x342','29x29\n522x522','39x39\n702x702','49x49\n882x882','59x59\n1062x1062'],fontsize=fontsize)
ax.set_ylabel(r'spatial scale [grid points/km$^2$]',fontsize=fontsize)
ax.set_xlim([1,15])
ax.set_ylim([x[0],x[-1]])

cb = fig.colorbar(p, ax=ax, orientation='vertical',ticks=clevs[::4],pad=0.025,aspect=15)
cb.ax.set_title('fss',fontsize=fontsize)
cb.ax.tick_params(labelsize=fontsize,size=0)

plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()


