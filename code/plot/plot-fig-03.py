"""
Plots fig. 3 in Dunn-Sigouin et al. 
"""

import numpy     as np
import xarray    as xr
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config
import matplotlib as mpl

def setup_subplot_fss(subplot_flag, ax, time, box_size, fss_data, sig_data, title_text, clevs, cmap, fontsize):
    """ 
    Sets up specifics of subplots for fig. 3
    """
    p = ax.contourf(time, box_size, fss_data, levels=clevs, cmap=cmap, extend='min')
    ax.pcolor(time, box_size, sig_data, hatch='\\\\', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)

    contour = ax.contour(time, box_size, fss_data, levels=clevs, linewidths=1,linestyles='-',colors='grey')
    ax.clabel(contour, clevs, inline=True, fmt='%1.1f', fontsize=fontsize)

    ax.set_xticks(time)
    ax.set_xlim([time[0], time[-1]])

    ax.set_yticks(np.array([1, 9, 17, 25, 33, 41, 49, 57]))
    ax.set_yticklabels(['1/9', '9/81', '17/153', '25/225', '33/297', '41/369', '49/441', '57/513'], fontsize=fontsize)
    if subplot_flag == 0:
        ax.set_ylabel(r'spatial scale [gridpoints$^2$/km$^2$]', fontsize=fontsize)
    ax.set_ylim([box_size[0], box_size[-2]])

    ax.set_title(title_text, fontsize=fontsize + 3)
    
    cb = plt.colorbar(p, ax=ax, orientation='vertical', ticks=clevs, pad=0.025, aspect=15)
    cb.ax.tick_params(labelsize=fontsize, size=0)
    
    return ax


def setup_subplot_ltg(subplot_flag, ax, time, box_size, fss_data, sig_data, ltg_data, title_text, clevs1, clevs2, cmap, fontsize):
    """
    Sets up specifics of subplots for fig. 1
    """
    p = ax.contourf(ltg_data.time, box_size, ltg_data, levels=clevs2, cmap=cmap, extend='max')
    ax.pcolor(time, box_size, sig_data, hatch='\\\\', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)

    contour = ax.contour(time, box_size, fss_data, levels=clevs1, linewidths=1,linestyles='-',colors='grey')
    ax.clabel(contour, clevs1, inline=True, fmt='%1.1f', fontsize=fontsize)

    ax.set_xticks(time)
    ax.set_xlim([time[0], time[-1]])
    if time.size == 6:
        ax.set_xticklabels(['1','2','3','4','5','6'],fontsize=fontsize)
        ax.set_xlabel(r'lead time [weeks]',fontsize=fontsize)
    else:
        ax.set_xticklabels(['1', '', '3', '', '5', '', '7', '', '9', '', '11', '', '13', '', '15'], fontsize=fontsize)
        ax.set_xlabel(r'lead time [days]', fontsize=fontsize)

    ax.set_yticks(np.array([1, 9, 17, 25, 33, 41, 49, 57]))
    ax.set_yticklabels(['1/9', '9/81', '17/153', '25/225', '33/297', '41/369', '49/441', '57/513'], fontsize=fontsize)
    if subplot_flag == 2:
        ax.set_ylabel(r'spatial scale [gridpoints$^2$/km$^2$]', fontsize=fontsize)
    ax.set_ylim([box_size[0], box_size[-2]])

    ax.set_title(title_text, fontsize=fontsize + 3)

    cb = plt.colorbar(p, ax=ax, orientation='vertical', ticks=clevs2, pad=0.025, aspect=15)
    cb.ax.set_title('[days]', fontsize=fontsize)
    cb.ax.tick_params(labelsize=fontsize, size=0)

    return ax

# INPUT -----------------------
write2file = True
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'fss_tp24_daily_europe_mjjas_2020-05-04_2022-09-29_0.25x0.25.nc'
filename_in_2     = 'fss_tp24_daily_europe_ndjfm_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_3     = 'ltg_fss_tp24_daily_europe_mjjas_2020-05-04_2022-09-29_0.25x0.25.nc'
filename_in_4     = 'ltg_fss_tp24_daily_europe_ndjfm_2020-01-02_2022-12-29_0.25x0.25.nc'
figname_out       = 'fig_03.pdf'

# read in data
ds1        = xr.open_dataset(path_in + filename_in_1)
ds2        = xr.open_dataset(path_in + filename_in_2)    
ds3        = xr.open_dataset(path_in + filename_in_3)
ds4        = xr.open_dataset(path_in + filename_in_4)

# calculate significance
sig1       = s2s.mask_significant_values_from_bootstrap(ds1['fss_bootstrap'],0.05)
sig2       = s2s.mask_significant_values_from_bootstrap(ds2['fss_bootstrap'],0.05)

# set ltg values to nan where fss not-significant. makes figure nicer. Hacky
time_interp = ds3['lead_time_gained'].time.astype('int')
time        = sig1.time.values
for bs in range(1,ds1['box_size'].size):
    index1                              = time[np.where(sig1[bs,:] == 1.0)[0]]
    index2                              = np.where(time_interp == index1[0])[0][0]-2
    ds3['lead_time_gained'][bs,index2:] = np.nan

time_interp = ds4['lead_time_gained'].time.astype('int')
time        = sig2.time.values
for bs in range(1,ds2['box_size'].size):
    index1                              = time[np.where(sig2[bs,:] == 1.0)[0]]
    index2                              = np.where(time_interp == index1[0])[0][0]-2
    ds4['lead_time_gained'][bs,index2:] = np.nan

    
    
# plot 
fontsize   = 11
clevs1     = np.arange(0,1.1,0.1)
clevs2     = np.arange(0.0, 4.5, 0.5)
cmap1      = mpl.cm.get_cmap("GnBu").copy()
cmap2      = mpl.cm.get_cmap("YlGn").copy()
figsize    = np.array([12,8])
fig,ax     = plt.subplots(nrows=2,ncols=2,sharey='row',sharex='col',figsize=(figsize[0],figsize[1]))
ax         = ax.ravel()

setup_subplot_fss(0, ax[0], ds1['time'], ds1['box_size'], ds1['fss'], sig1, 'a) summer mean square error skill score', clevs1, cmap1, fontsize)

setup_subplot_fss(1, ax[1], ds2['time'], ds2['box_size'], ds2['fss'], sig2, 'b) winter mean square error skill score', clevs1, cmap1, fontsize)

setup_subplot_ltg(2, ax[2], ds1['time'], ds1['box_size'], ds1['fss'], sig1, ds3['lead_time_gained'], 'c) summer lead time gained', clevs1, clevs2, cmap2, fontsize)

setup_subplot_ltg(3, ax[3], ds2['time'], ds2['box_size'], ds2['fss'], sig2, ds4['lead_time_gained'], 'd) winter lead time gained', clevs1, clevs2, cmap2, fontsize)

# write2file
plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()

