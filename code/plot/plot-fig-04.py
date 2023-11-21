"""
Plots fig. 4 in Dunn-Sigouin et al. 
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
    if (title_text == 'c) temperature minus precipitation') or (title_text == 'f) temperature minus precipitation'):
        p = ax.contourf(time, box_size, fss_data, levels=clevs, cmap=cmap, extend='both')
    else:
        p = ax.contourf(time, box_size, fss_data, levels=clevs, cmap=cmap, extend='min')
    ax.pcolor(time, box_size, sig_data, hatch='\\\\', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)

    ax.set_xticks(time)
    if time.size == 6:
        ax.set_xticklabels(['1d1d','2d2d','4d4d','1w1w','2w2w','4w3w'],fontsize=fontsize)
        ax.set_xlabel(r'lead time [timescale]',fontsize=fontsize)
    else:
        #ax.set_xticklabels(['1', '', '3', '', '5', '', '7', '', '9', '', '11', '', '13', '', '15','','17','','19','','21'], fontsize=fontsize)
        ax.set_xticklabels(['1', '', '3', '', '5', '', '7', '', '9', '', '11', '', '13', '', '15'], fontsize=fontsize)
        ax.set_xlabel(r'lead time [days]', fontsize=fontsize)
    ax.set_xlim([time[0], time[-1]])

    ax.set_yticks(np.array([1, 9, 17, 25, 33, 41, 49, 57]))
    ax.set_yticklabels(['1/0.25', '9/2.25', '17/4.25', '25/6.25', '33/8.25', '41/10.25', '49/12.25', '57/14.25'], fontsize=fontsize)
    if (title_text == 'a) precipitation') or (title_text == 'd) precipitation'):
        ax.set_ylabel(r'spatial scale [gridpoints$^2$/degrees$^2$]', fontsize=fontsize)
    ax.set_ylim([box_size[0], box_size[-2]])

    ax.set_title(title_text, fontsize=fontsize + 3)
    if (title_text == 'c) temperature minus precipitation') or (title_text == 'f) temperature minus precipitation'):
        cb = plt.colorbar(p, ax=ax, orientation='vertical', ticks=clevs[::2], pad=0.025, aspect=15)
    else:
        cb = plt.colorbar(p, ax=ax, orientation='vertical', ticks=clevs, pad=0.025, aspect=15)
    cb.ax.set_title('fbss', fontsize=fontsize)
    cb.ax.tick_params(labelsize=fontsize, size=0)
    return ax

# INPUT -----------------------
write2file = False
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'fbss_tp24_pval0.9_time_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_2     = 'fbss_tp24_pval0.1_time_europe_annual_2022-01-03_2022-12-29_0.25x0.25.nc'
filename_in_3     = ''
filename_in_4     = 'fbss_t2m24_pval0.9_time_europe_annual_2021-01-04_2021-12-30_0.25x0.25.nc'
filename_in_5     = 'fbss_t2m24_pval0.1_time_europe_annual_2021-01-04_2021-12-30_0.25x0.25.nc'
filename_in_6     = ''
figname_out       = 'fig_04.pdf'

# read in data
ds1        = xr.open_dataset(path_in + filename_in_1)
ds2        = xr.open_dataset(path_in + filename_in_2)
#ds3        = xr.open_dataset(path_in + filename_in_3)
ds4        = xr.open_dataset(path_in + filename_in_4)
ds5        = xr.open_dataset(path_in + filename_in_5)
#ds6        = xr.open_dataset(path_in + filename_in_6)

# Remove box sizes where low and high-res data don't overlap on the same grid in timescale dimension data
#index         = np.where(~np.isnan(ds4['fbss'][:,4]))[0]
#ds4           = ds4.isel(box_size=index)
#ds5           = ds5.isel(box_size=index)
#ds6           = ds6.isel(box_size=index)

# calculate significance
sig1       = s2s.mask_significant_values_from_bootstrap(ds1['fbss_bootstrap'],0.05)
sig2       = s2s.mask_significant_values_from_bootstrap(ds2['fbss_bootstrap'],0.05)
#sig3       = s2s.mask_significant_values_from_bootstrap(ds3['fbss_bootstrap'],0.05)
sig4       = s2s.mask_significant_values_from_bootstrap(ds4['fbss_bootstrap'],0.05)
sig5       = s2s.mask_significant_values_from_bootstrap(ds5['fbss_bootstrap'],0.05)
#sig6       = s2s.mask_significant_values_from_bootstrap(ds6['fbss_bootstrap'],0.05)

# plot 
fontsize   = 11
clevs      = np.arange(0.0, 1.1, 0.1)
clevs_anom = np.arange(-0.5, 0.55, 0.05)
cmap       = mpl.cm.get_cmap("GnBu").copy()
cmap_anom  = mpl.cm.get_cmap("RdBu_r").copy()
figsize    = np.array([12*1.61,9])
fig,ax     = plt.subplots(nrows=2,ncols=3,sharey='row',figsize=(figsize[0],figsize[1]))
ax         = ax.ravel()

# A) precipitation
setup_subplot(ax[0], ds1['time'], ds1['box_size'], ds1['fbss'], sig1, 'a) precipitation q90', clevs, cmap, fontsize)

# B) temperature 
setup_subplot(ax[1], ds2['time'], ds2['box_size'], ds2['fbss'], sig2, 'b) precipitation q10', clevs, cmap, fontsize)

# C) precip minus temperature 
#setup_subplot(ax[2], ds3['time'], ds3['box_size'], ds3['fbss'], sig3, 'c) temperature minus precipitation', clevs_anom, cmap_anom, fontsize)

# D) precip 
setup_subplot(ax[3], ds4['time'], ds4['box_size'], ds4['fbss'], sig4, 'd) temperature q90', clevs, cmap, fontsize)

# E) temperature 
setup_subplot(ax[4], ds5['time'], ds5['box_size'], ds5['fbss'], sig5, 'e) temperature q10', clevs, cmap, fontsize)

# F) temperature minus precipitation 
#setup_subplot(ax[5], ds6['timescale'],ds6['box_size'], ds6['fbss'], sig6, 'f) temperature minus precipitation', clevs_anom, cmap_anom, fontsize)

# write2file
plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()

