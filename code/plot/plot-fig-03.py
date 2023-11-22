"""
Plots fig. 2 in Dunn-Sigouin et al. 
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

    contour = ax.contour(time, box_size, fss_data, levels=clevs, linewidths=1,linestyles='-',colors='grey')
    ax.clabel(contour, clevs, inline=True, fmt='%1.1f', fontsize=fontsize)

    
    ax.set_xticks(time)
    ax.set_xticklabels(['1', '', '3', '', '5', '', '7', '', '9', '', '11', '', '13', '', '15'], fontsize=fontsize)
    ax.set_xlabel(r'lead time [days]', fontsize=fontsize)
    ax.set_xlim([time[0], time[-1]])

    ax.set_yticks(np.array([1, 9, 17, 25, 33, 41, 49, 57]))
    ax.set_yticklabels(['1/9', '9/81', '17/153', '25/225', '33/297', '41/369', '49/441', '57/513'], fontsize=fontsize)
    if (title_text == 'a) europe') or (title_text == 'c) scandinavia'):
        ax.set_ylabel(r'spatial scale [gridpoints$^2$/km$^2$]', fontsize=fontsize)
    ax.set_ylim([box_size[0], box_size[-2]])

    """
    ax.set_title(title_text, fontsize=fontsize + 3)
    cb = plt.colorbar(p, ax=ax, orientation='vertical', ticks=clevs, pad=0.025, aspect=15)
    cb.ax.set_title('fss', fontsize=fontsize)
    cb.ax.tick_params(labelsize=fontsize, size=0)
    """
    return ax


# INPUT -----------------------
write2file = False
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'fss_tp24_time_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_2     = 'fss_tp24_time_europe2_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_3     = 'fss_tp24_time_europe3_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_4     = 'fss_t2m24_time_europe_annual_2021-01-04_2021-12-30_0.25x0.25.nc'
filename_in_5     = 'fss_t2m24_time_europe2_annual_2021-01-04_2021-12-30_0.25x0.25.nc'
filename_in_6     = 'fss_t2m24_time_europe3_annual_2021-01-04_2021-12-30_0.25x0.25.nc'
figname_out       = 'fig_03.pdf'

# read in data
ds1        = xr.open_dataset(path_in + filename_in_1)
ds2        = xr.open_dataset(path_in + filename_in_2)   
ds3        = xr.open_dataset(path_in + filename_in_3)                                                                                           
ds4        = xr.open_dataset(path_in + filename_in_4)
ds5        = xr.open_dataset(path_in + filename_in_5)
ds6        = xr.open_dataset(path_in + filename_in_6)

# calculate significance
sig1       = s2s.mask_significant_values_from_bootstrap(ds1['fss_bootstrap'],0.05)
sig2       = s2s.mask_significant_values_from_bootstrap(ds2['fss_bootstrap'],0.05)
sig3       = s2s.mask_significant_values_from_bootstrap(ds3['fss_bootstrap'],0.05)
sig4       = s2s.mask_significant_values_from_bootstrap(ds4['fss_bootstrap'],0.05)
sig5       = s2s.mask_significant_values_from_bootstrap(ds5['fss_bootstrap'],0.05)
sig6       = s2s.mask_significant_values_from_bootstrap(ds6['fss_bootstrap'],0.05)

# plot 
fontsize   = 11
clevs      = np.arange(0.0, 1.1, 0.1)
cmap       = mpl.cm.get_cmap("GnBu").copy()
cmap2      = mpl.cm.get_cmap("YlOrBr").copy()
figsize    = np.array([20,10])
fig,ax     = plt.subplots(nrows=2,ncols=3,figsize=(figsize[0],figsize[1]))
ax         = ax.ravel()

# A) europe
setup_subplot(ax[0], ds1['time'], ds1['box_size'], ds1['fss'], sig1, 'a) europe1', clevs, cmap, fontsize)

# B) europe2
setup_subplot(ax[1], ds2['time'], ds2['box_size'], ds2['fss'], sig2, 'b) europe2', clevs, cmap, fontsize)

# C) europe3
setup_subplot(ax[2], ds3['time'], ds3['box_size'], ds3['fss'], sig3, 'c) europe3', clevs, cmap, fontsize)

# D) europe  
setup_subplot(ax[3], ds4['time'], ds4['box_size'], ds4['fss'], sig4, 'd) europe1', clevs, cmap2, fontsize)

# E) europe2
setup_subplot(ax[4], ds5['time'], ds5['box_size'], ds5['fss'], sig5, 'e) europe2', clevs, cmap2, fontsize)

# F) europe3 
setup_subplot(ax[5], ds6['time'], ds6['box_size'], ds6['fss'], sig6, 'f) europe3', clevs, cmap2, fontsize)

# write2file
plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()

