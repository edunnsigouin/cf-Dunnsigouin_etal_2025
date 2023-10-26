"""
Plots fig. 3 in Dunn-Sigouin et al. 
"""

import numpy     as np
import xarray    as xr
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config
import matplotlib as mpl

def setup_subplot(ax, time, box_size, fss_data, sig_data, title_text, clevs, cmap, fontsize):
    """
    Sets up specifics of subplots for fig. 3
    """
    p = ax.contourf(time, box_size, fss_data, levels=clevs, cmap=cmap, extend='min')
    ax.pcolor(time, box_size, sig_data, hatch='\\\\', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)

    ax.set_xticks(time)
    ax.set_xticklabels(['1', '', '3', '', '5', '', '7', '', '9', '', '11', '', '13', '', '15'], fontsize=fontsize)
    ax.set_xlabel(r'lead time [days]', fontsize=fontsize)
    ax.set_xlim([time[0], time[-1]])

    ax.set_yticks(np.array([1, 9, 17, 25, 33, 41, 49, 57]))
    ax.set_yticklabels(['1/0.25', '9/2.25', '17/4.25', '25/6.25', '33/8.25', '41/10.25', '49/12.25', '57/14.25'], fontsize=fontsize)
    if (title_text == 'a) northern europe precipitation') or (title_text == 'd) northern europe temperature'):
        ax.set_ylabel(r'spatial scale [gridpoints$^2$/degrees$^2$]', fontsize=fontsize)
    ax.set_ylim([box_size[0], box_size[-2]])

    ax.set_title(title_text, fontsize=fontsize + 3)
    if (title_text == 'c) southern minus northern europe precipitation') or (title_text == 'f) southern minus northern europe temperature'):
        cb = plt.colorbar(p, ax=ax, orientation='vertical', ticks=clevs[::2], pad=0.025, aspect=15)
    else:
        cb = plt.colorbar(p, ax=ax, orientation='vertical', ticks=clevs, pad=0.025, aspect=15)
    cb.ax.set_title('fss', fontsize=fontsize)
    cb.ax.tick_params(labelsize=fontsize, size=0)
    return ax

# INPUT -----------------------
write2file = True
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'time_vs_ss_fss_anomaly_tp24_northern_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_2     = 'time_vs_ss_fss_anomaly_tp24_southern_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_3     = 'time_vs_ss_fss_anomaly_t2m24_northern_europe_annual_2021-01-04_2021-12-30_0.25x0.25.nc'
filename_in_4     = 'time_vs_ss_fss_anomaly_t2m24_southern_europe_annual_2021-01-04_2021-12-30_0.25x0.25.nc'
figname_out       = 'fig_03.pdf'
    
# read in data
fss_1      = xr.open_dataset(path_in + filename_in_1)['fss']
fss_2      = xr.open_dataset(path_in + filename_in_2)['fss']
fss_3      = xr.open_dataset(path_in + filename_in_3)['fss']
fss_4      = xr.open_dataset(path_in + filename_in_4)['fss']
fssb_1     = xr.open_dataset(path_in + filename_in_1)['fss_bootstrap']
fssb_2     = xr.open_dataset(path_in + filename_in_2)['fss_bootstrap']
fssb_3     = xr.open_dataset(path_in + filename_in_3)['fss_bootstrap']
fssb_4     = xr.open_dataset(path_in + filename_in_4)['fss_bootstrap']
box_size   = fss_1['box_size']
time       = fss_1['time']

# calculate significance
sig_1       = s2s.mask_significant_values_from_bootstrap(fssb_1,0.05)
sig_2       = s2s.mask_significant_values_from_bootstrap(fssb_2,0.05)
sig_3       = s2s.mask_significant_values_from_bootstrap(fssb_3,0.05)
sig_4       = s2s.mask_significant_values_from_bootstrap(fssb_4,0.05)
sig_2minus1 = s2s.mask_significance_between_bootstraps(fssb_1, fssb_2, 0.05)
sig_4minus3 = s2s.mask_significance_between_bootstraps(fssb_4, fssb_3, 0.05)

# plot 
fontsize    = 11
clevs       = np.arange(0.0, 1.1, 0.1)
clevs_anom1 = np.arange(-0.2, 0.22, 0.02)
clevs_anom2 = np.arange(-0.2, 0.22, 0.02)
cmap        = mpl.cm.get_cmap("GnBu").copy()
cmap_anom   = mpl.cm.get_cmap("RdBu_r").copy()
figsize     = np.array([12*1.61,9])
fig,ax      = plt.subplots(nrows=2,ncols=3,sharey='row',figsize=(figsize[0],figsize[1]))
ax          = ax.ravel()

# A) JJA precipitation
setup_subplot(ax[0], time, box_size, fss_1, sig_1, 'a) northern europe precipitation', clevs, cmap, fontsize)

# B) DJF precipitation
setup_subplot(ax[1], time, box_size, fss_2, sig_2, 'b) southern europe precipitation', clevs, cmap, fontsize)

# C) DJF minus JJA precipitation
setup_subplot(ax[2], time, box_size, fss_2-fss_1, sig_2minus1, 'c) southern minus northern europe precipitation', clevs_anom1, cmap_anom, fontsize)

# D) JJA temperature
setup_subplot(ax[3], time, box_size, fss_3, sig_3, 'd) nothern europe temperature', clevs, cmap, fontsize)

# E) DJF temperature
setup_subplot(ax[4], time, box_size, fss_4, sig_4, 'e) southern europe temperature', clevs, cmap, fontsize)

# F) DJF minus JJA temperature
setup_subplot(ax[5], time, box_size, fss_4-fss_3, sig_4minus3, 'f) southern minus northern europe temperature', clevs_anom2, cmap_anom, fontsize)

# write2file
plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()

