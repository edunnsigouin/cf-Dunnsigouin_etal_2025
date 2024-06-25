"""
Plots fig. 2 in Dunn-Sigouin et al. 
"""

import numpy     as np
import xarray    as xr
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config
import matplotlib as mpl


def setup_subplot_ltg(flag, ax, ds, title_text, clevs_score, clevs_ltg, cmap, fontsize):
    """
    Sets up specifics of subplots for fig. 2
    """
    time        = ds['time']
    time_interp = ds['time_interp']
    box_size    = ds['box_size']

    p = ax.pcolormesh(time_interp, box_size, ds['lead_time_gained'], vmin=clevs_ltg[0], vmax=clevs_ltg[-1], cmap=cmap,edgecolor='none',shading='auto')
    ax.pcolor(time, box_size, ds['significance'], hatch='\\\\', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)
    ax.pcolor(time_interp, box_size, ds['max_skill_mask'], hatch='xx', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)

    contour = ax.contour(time, box_size,ds['score'], levels=clevs_score, linewidths=2,linestyles='-',colors = [(0.5,0.5,0.5)])
    ax.clabel(contour, clevs_score, inline=True, fmt='%1.1f', fontsize=fontsize)

    ax.set_xticks(time)
    ax.set_xlim([time[0], time[-1]])

    if flag == 6:
        ax.set_xticklabels(['1','2','3','4','5','6'],fontsize=fontsize)
        ax.set_xlabel(r'lead time [weeks]',fontsize=fontsize)
    elif flag == 5:
        ax.set_xticklabels(['1', '', '', '', '5', '', '', '', '', '10', '', '', '', '', '15'], fontsize=fontsize)
        ax.set_xlabel(r'lead time [days]', fontsize=fontsize)

    if (flag == 1) or (flag == 3) or (flag == 5):
        ax.set_yticks(np.array([1, 9, 17, 25, 33, 41, 49, 57]))
        ax.set_yticklabels(['1', '9', '17', '25', '33', '41', '49', '57'], fontsize=fontsize)
        ax.set_ylabel(r'precision [gridpoints$^2$]', fontsize=fontsize)

    ax.set_ylim([box_size[0], box_size[-2]])

    if (flag == 2) or (flag == 4) or (flag == 6):
        ax2 = ax.twinx()
        ax2.set_yticks(np.array([0, 9, 17, 25, 33, 41, 49, 57]))
        ax2.set_yticklabels(['9', '81', '153', '225', '297', '369', '441', '513'], fontsize=fontsize)
        ax2.set_ylabel(r'precision [km$^2$]', fontsize=fontsize)

    ax.set_title(title_text, fontsize=fontsize + 3)

    return p


# INPUT -----------------------
write2file = True
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'fmsess_tp24_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_2     = 'fmsess_tp24_weekly_europe_annual_2020-01-02_2022-12-29.nc'
filename_in_3     = 'fbss_tp24_pval0.9_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_4     = 'fbss_tp24_pval0.9_weekly_europe_annual_2020-01-02_2022-12-29.nc'
filename_in_5     = 'fbss_tp24_pval0.1_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_6     = 'fbss_tp24_pval0.1_weekly_europe_annual_2020-01-02_2022-12-29.nc'
figname_out       = 'fig_02.png'

# read in data
ds1        = xr.open_dataset(path_in + filename_in_1)
ds2        = xr.open_dataset(path_in + filename_in_2)    
ds3        = xr.open_dataset(path_in + filename_in_3)
ds4        = xr.open_dataset(path_in + filename_in_4)
ds5        = xr.open_dataset(path_in + filename_in_5)
ds6        = xr.open_dataset(path_in + filename_in_6)

# convert weekly lead_time_gained to units of days
ds2['lead_time_gained'] = ds2['lead_time_gained']*7
ds4['lead_time_gained'] = ds4['lead_time_gained']*7
ds6['lead_time_gained'] = ds6['lead_time_gained']*7

# plot 
fontsize    = 11
clevs_score = np.arange(0,1.1,0.1)
clevs_ltg   = np.arange(-3.5, 3.75, 0.25)
cmap        = plt.get_cmap('PiYG', clevs_ltg.size - 1) # -1 so that colorbar tick labels match individual colors
figsize     = np.array([12,12])
fig,ax      = plt.subplots(nrows=3,ncols=2,sharey='row',sharex='col',figsize=(figsize[0],figsize[1]))
ax          = ax.ravel()

title1 = 'a) daily anomalies'
title2 = 'b) weekly anomalies'
title3 = 'c) daily 90$^{th}$ quantile extremes'
title4 = 'd) weekly 90$^{th}$ quantile extremes'
title5 = 'e) daily 10$^{th}$ quantile extremes'
title6 = 'f) weekly 10$^{th}$ quantile extremes'

setup_subplot_ltg(1, ax[0], ds1, title1, clevs_score, clevs_ltg, cmap, fontsize)

setup_subplot_ltg(2, ax[1], ds2, title2, clevs_score, clevs_ltg, cmap, fontsize)

setup_subplot_ltg(3, ax[2], ds3, title3, clevs_score, clevs_ltg, cmap, fontsize)

setup_subplot_ltg(4, ax[3], ds4, title4, clevs_score, clevs_ltg, cmap, fontsize)

setup_subplot_ltg(5, ax[4], ds5, title5, clevs_score, clevs_ltg, cmap, fontsize)

p = setup_subplot_ltg(6, ax[5], ds6, title6, clevs_score, clevs_ltg, cmap, fontsize)

fig.subplots_adjust(right=0.925, left=0.075,top=0.96,hspace=0.15,wspace=0.075)
cbar_ax = fig.add_axes([0.2, 0.035, 0.6, 0.02])
cb      = fig.colorbar(p, cax=cbar_ax, orientation='horizontal',ticks=clevs_ltg[2::4])
cb.ax.tick_params(labelsize=fontsize, size=0)
cb.ax.set_title('lead time gained or lost [days]', fontsize=fontsize,y=1.01)

# write2file
if write2file: plt.savefig(path_out + figname_out)
plt.show()

