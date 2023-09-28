"""
Plots the fraction skill score calculated 
for anomalous forecasts as a funciton of time scale
and spatial scale.
"""

import numpy     as np
import xarray    as xr
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config
import matplotlib as mpl

# INPUT -----------------------
time_flag           = 'timescale'              # time or timescale ?
variable            = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain              = 'europe'                 # europe/nordic/vestland                       
first_forecast_date = '20210104'               # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 104                      # number of weeks with forecasts
grid                = 'both'
write2file          = True
# -----------------------------

# define stuff         
forecast_dates   = s2s.get_forecast_dates(first_forecast_date,number_forecasts).strftime('%Y-%m-%d')
path_in          = config.dirs['verify_s2s_forecast_daily']
path_out         = config.dirs['fig'] + 's2s/ecmwf/daily/forecast/'

if grid == 'both':
    filename_in      = time_flag + '_vs_ss_fss_anomaly_' + variable + '_' + domain + \
        '_' + forecast_dates[0] + '_' + forecast_dates[-1] + '.nc'
    figname_out      = time_flag + '_vs_spatialscale_fss_anomaly_' + variable + '_' + domain + \
        '_' + forecast_dates[0] + '_' + forecast_dates[-1] + '.pdf'
else:
    filename_in      = time_flag + '_vs_ss_fss_anomaly_' + variable + '_' + domain + \
        '_' + forecast_dates[0] + '_' + forecast_dates[-1] + '_' + grid + '.nc'
    figname_out      = time_flag + '_vs_spatialscale_fss_anomaly_' + variable + '_' + domain + \
        '_' + forecast_dates[0] + '_' + forecast_dates[-1] + '_' + grid + '.pdf'
    
# read in data
ds   = xr.open_dataset(path_in + filename_in)
fss  = ds['fss'].values
y    = ds['box_size'].values
x    = ds[time_flag].values
y2   = np.array([1,9,17,25,33,41,49,57])

# calculate significance
temp = ds['fss_bootstrap'].quantile(0.05,dim='number_shuffle_bootstrap',skipna=True).values
sig  = (temp < 0).astype(np.int32) # when 5th percentile crosses zero
sig  = np.ma.masked_less(sig, 0.5)

# remove box sizes where not applicable for low-res data 
if grid == 'both':
    index = np.where(~np.isnan(fss[:,4]))
    fss   = fss[index]
    sig   = sig[index]
    y     = y[index]

# plot 
fontsize = 11
clevs    = np.arange(0.0, 1.05, 0.05)
cmap     = mpl.cm.get_cmap("RdBu_r").copy()
cmap.set_bad(color=[0.8,0.8,0.8]) # set nans to specified color
figsize  = np.array([6*1.61,6])
fig,ax   = plt.subplots(nrows=1,ncols=1,figsize=(figsize[0],figsize[1]))

p = ax.contourf(x,y,fss,levels=clevs,cmap=cmap,extend='min')
ax.pcolor(x,y, sig, hatch='\\\\',cmap=mpl.colors.ListedColormap(['none']),edgecolor=[0.8,0.8,0.8],lw=0)

ax.set_xticks(x)
if grid == 'both':
    ax.set_xticklabels(['1d1d','2d2d','4d4d','1w1w','2w2w','4w3w'],fontsize=fontsize)
else:
    ax.set_xticklabels(['1d1d','2d2d','4d4d','1w1w'],fontsize=fontsize)
ax.set_xlabel(r'lead time [timescale]',fontsize=fontsize)
ax.set_xlim([x[0],x[-1]])

ax.set_yticks(y2)
ax.set_yticklabels(['1/0.25/9','9/2.25/81','17/4.25/153','25/6.25/225','33/8.25/297','41/10.25/369','49/12.25/441','57/14.25/513'],fontsize=fontsize)
ax.set_ylabel(r'spatial scale [gridpoints$^2$/degrees$^2$/km$^2$]',fontsize=fontsize)
ax.set_ylim([y[0],y[-1]])

cb = fig.colorbar(p, ax=ax, orientation='vertical',ticks=clevs[::2],pad=0.025,aspect=15)
cb.ax.set_title('fss',fontsize=fontsize)
cb.ax.tick_params(labelsize=fontsize,size=0)

plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()


