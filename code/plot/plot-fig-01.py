"""
Plots the fraction skill score calculated 
for anomalous forecasts as a funciton of time
and spatial scale.
"""

import numpy     as np
import xarray    as xr
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config
import matplotlib as mpl

def calc_significance(ds,threshold):
    """calculates significance from boostrapped samples"""
    temp = ds['fss_bootstrap'].quantile(threshold,dim='number_shuffle_bootstrap',skipna=True).values
    sig  = (temp < 0).astype(np.int32) # when 5th percentile crosses zero
    sig  = np.ma.masked_less(sig, 0.5)
    return sig


# INPUT -----------------------
write2file = True
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_tp24  = 'time_vs_ss_fss_anomaly_tp24_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_t2m24 = 'time_vs_ss_fss_anomaly_t2m24_europe_annual_2021-01-04_2021-12-30_0.25x0.25.nc'
figname_out       = 'fig_01.pdf'
    
# read in data
ds_tp24  = xr.open_dataset(path_in + filename_in_tp24)
ds_t2m24 = xr.open_dataset(path_in + filename_in_t2m24)
y        = ds_tp24['box_size'].values
x        = ds_tp24['time'].values

# calculate significance
sig_tp24  = calc_significance(ds_tp24,0.05)
sig_t2m24 = calc_significance(ds_t2m24,0.05)

# plot 
fontsize = 11
clevs    = np.arange(0.0, 1.05, 0.05)
cmap     = mpl.cm.get_cmap("RdBu_r").copy()
figsize  = np.array([12*1.61,6])
fig,ax   = plt.subplots(nrows=1,ncols=2,figsize=(figsize[0],figsize[1]))
ax       = ax.ravel()

# precipitation
p1 = ax[0].contourf(x,y,ds_tp24['fss'],levels=clevs,cmap=cmap,extend='min')
ax[0].pcolor(x,y,sig_tp24, hatch='\\\\',cmap=mpl.colors.ListedColormap(['none']),edgecolor=[0.8,0.8,0.8],lw=0)

ax[0].set_xticks(x)
ax[0].set_xticklabels(['1','','3','','5','','7','','9','','11','','13','','15'],fontsize=fontsize)
ax[0].set_xlabel(r'lead time [days]',fontsize=fontsize)
ax[0].set_xlim([x[0],x[-1]])

ax[0].set_yticks(np.array([1,9,17,25,33,41,49,57]))
ax[0].set_yticklabels(['1/0.25/9','9/2.25/81','17/4.25/153','25/6.25/225','33/8.25/297','41/10.25/369','49/12.25/441','57/14.25/513'],fontsize=fontsize)
ax[0].set_ylabel(r'spatial scale [gridpoints$^2$/degrees$^2$/km$^2$]',fontsize=fontsize)
ax[0].set_ylim([y[0],y[-2]])

cb = fig.colorbar(p1, ax=ax[0], orientation='vertical',ticks=clevs[::2],pad=0.025,aspect=15)
cb.ax.set_title('fss',fontsize=fontsize)
cb.ax.tick_params(labelsize=fontsize,size=0)

# temperature
p2 = ax[1].contourf(x,y,ds_t2m24['fss'],levels=clevs,cmap=cmap,extend='min')
ax[1].pcolor(x,y,sig_t2m24, hatch='\\\\',cmap=mpl.colors.ListedColormap(['none']),edgecolor=[0.8,0.8,0.8],lw=0)

ax[1].set_xticks(x)
ax[1].set_xticklabels(['1','','3','','5','','7','','9','','11','','13','','15'],fontsize=fontsize)
ax[1].set_xlabel(r'lead time [days]',fontsize=fontsize)
ax[1].set_xlim([x[0],x[-1]])

ax[1].set_yticks(np.array([1,9,17,25,33,41,49,57]))
ax[1].set_yticklabels(['1/0.25/9','9/2.25/81','17/4.25/153','25/6.25/225','33/8.25/297','41/10.25/369','49/12.25/441','57/14.25/513'],fontsize=fontsize)
#ax[1].set_ylabel(r'spatial scale [gridpoints$^2$/degrees$^2$/km$^2$]',fontsize=fontsize)
ax[1].set_ylim([y[0],y[-2]])

cb = fig.colorbar(p1, ax=ax[1], orientation='vertical',ticks=clevs[::2],pad=0.025,aspect=15)
cb.ax.set_title('fss',fontsize=fontsize)
cb.ax.tick_params(labelsize=fontsize,size=0)

# write2file
plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()


