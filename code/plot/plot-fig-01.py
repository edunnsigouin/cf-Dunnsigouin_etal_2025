"""
Plots fig. 1 in Dunn-Sigouin et al. 
"""

import numpy     as np
import xarray    as xr
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config
import matplotlib as mpl

def setup_subplot(ax, time, box_size, fss_data, sig_data, title_text, clevs, cmap, fontsize):
    """
    Sets up specifics of subplots for fig. 1
    """
    p = ax.contourf(time, box_size, fss_data, levels=clevs, cmap=cmap, extend='min')
    ax.pcolor(time, box_size, sig_data, hatch='\\\\', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)

    contour = ax.contour(time, box_size, fss_data, levels=clevs, linewidths=1,linestyles='-',colors='grey')
    ax.clabel(contour, clevs, inline=True, fmt='%1.1f', fontsize=fontsize)

    ax.set_xticks(time)
    ax.set_xlim([time[0], time[-1]])
    if time.size == 6:
        ax.set_xticklabels(['1','2','3','4','5','6'],fontsize=fontsize)
        if title_text == 'd) weekly-mean temperature':
            ax.set_xlabel(r'lead time [weeks]',fontsize=fontsize)
    else:
        ax.set_xticklabels(['1', '', '3', '', '5', '', '7', '', '9', '', '11', '', '13', '', '15'], fontsize=fontsize)
        if title_text == 'c) daily-mean temperature':
            ax.set_xlabel(r'lead time [days]', fontsize=fontsize)

    ax.set_yticks(np.array([1, 9, 17, 25, 33, 41, 49, 57]))
    ax.set_yticklabels(['1/9', '9/81', '17/153', '25/225', '33/297', '41/369', '49/441', '57/513'], fontsize=fontsize)
    if (title_text == 'a) daily-mean precipitation') or (title_text == 'c) daily-mean temperature'):
        ax.set_ylabel(r'spatial scale [gridpoints$^2$/km$^2$]', fontsize=fontsize)
    ax.set_ylim([box_size[0], box_size[-2]])

    ax.set_title(title_text, fontsize=fontsize + 3)
    """
    cb = plt.colorbar(p, ax=ax, orientation='vertical', ticks=clevs, pad=0.025, aspect=15)
    cb.ax.set_title('fss', fontsize=fontsize)
    cb.ax.tick_params(labelsize=fontsize, size=0)
    """
    return ax

# INPUT -----------------------
write2file = True
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'fss_tp24_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_2     = 'fss_tp24_weekly_europe_annual_2021-01-04_2021-12-30.nc'
filename_in_3     = 'fss_t2m24_daily_europe_annual_2021-01-04_2021-12-30_0.25x0.25.nc'
filename_in_4     = 'fss_t2m24_weekly_europe_annual_2021-01-04_2021-12-30.nc'
figname_out       = 'fig_01.pdf'

# read in data
ds1        = xr.open_dataset(path_in + filename_in_1)
ds2        = xr.open_dataset(path_in + filename_in_2)    
ds3        = xr.open_dataset(path_in + filename_in_3)                                                                                           
ds4        = xr.open_dataset(path_in + filename_in_4)

# Remove box sizes where low and high-res data don't overlap on the same grid in timescale dimension data
index         = np.where(~np.isnan(ds2['fss'][:,4]))[0]
ds2           = ds2.isel(box_size=index)
ds4           = ds4.isel(box_size=index)

# calculate significance
sig1       = s2s.mask_significant_values_from_bootstrap(ds1['fss_bootstrap'],0.05)
sig2       = s2s.mask_significant_values_from_bootstrap(ds2['fss_bootstrap'],0.05)
sig3       = s2s.mask_significant_values_from_bootstrap(ds3['fss_bootstrap'],0.05)
sig4       = s2s.mask_significant_values_from_bootstrap(ds4['fss_bootstrap'],0.05)

# plot 
fontsize   = 11
clevs      = np.arange(0.0, 1.1, 0.1)
cmap1      = mpl.cm.get_cmap("GnBu").copy()
cmap2      = mpl.cm.get_cmap("YlOrBr").copy()
figsize    = np.array([12,8])
fig,ax     = plt.subplots(nrows=2,ncols=2,sharey='row',sharex='col',figsize=(figsize[0],figsize[1]))
ax         = ax.ravel()

# A) daily precipitation
setup_subplot(ax[0], ds1['time'], ds1['box_size'], ds1['fss'], sig1, 'a) daily-mean precipitation', clevs, cmap1, fontsize)

# B) weekly precipitation 
setup_subplot(ax[1], ds2['time'], ds2['box_size'], ds2['fss'], sig2, 'b) weekly-mean precipitation', clevs, cmap1, fontsize)

# C) daily temperature
setup_subplot(ax[2], ds3['time'], ds3['box_size'], ds3['fss'], sig3, 'c) daily-mean temperature', clevs, cmap2, fontsize)

# D) weekly temperature
setup_subplot(ax[3], ds4['time'], ds4['box_size'], ds4['fss'], sig4, 'd) weekly-mean temperature', clevs, cmap2, fontsize)

# write2file
plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()

