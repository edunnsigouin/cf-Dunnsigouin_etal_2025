"""
Plots fig. 1 in Dunn-Sigouin et al. 
"""

import numpy     as np
import xarray    as xr
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config
import matplotlib as mpl


def setup_subplot(flag, ax, ds, title_text, clevs_score, clevs_ltg, cmap_score, cmap_ltg, fontsize):
    """ 
    Sets up specifics of subplots for fig. 1
    """
    time        = ds['time']
    time_interp = ds['time_interp']
    box_size    = ds['box_size']

    if (flag == 0) or (flag == 2) or (flag == 4):
        p = ax.contourf(time, box_size, ds['score'], levels=clevs_score, cmap=cmap_score, extend='min')
        ax.pcolor(time, box_size, ds['significance'], hatch='\\\\', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)

        contour = ax.contour(time, box_size, ds['score'], levels=clevs_score, linewidths=2,linestyles='-',colors = [(0.5,0.5,0.5)])
        ax.clabel(contour, clevs_score, inline=True, fmt='%1.1f', fontsize=fontsize)
        
        ax.set_yticks(np.array([1, 9, 17, 25, 33, 41, 49, 57]))
        ax.set_yticklabels(['1', '9', '17', '25', '33', '41', '49', '57'], fontsize=fontsize)
        ax.set_ylabel(r'precision [gridpoints$^2$]', fontsize=fontsize)

    if (flag == 1) or (flag == 3) or (flag == 5):

        p = ax.pcolormesh(time_interp, box_size, ds['lead_time_gained'], vmin=clevs_ltg[0], vmax=clevs_ltg[-1], cmap=cmap_ltg,edgecolor='none',shading='auto')
        ax.pcolor(time, box_size, ds['significance'], hatch='\\\\', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)
        ax.pcolor(time_interp, box_size, ds['max_skill_mask'], hatch='xx', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)

        contour = ax.contour(time, box_size,ds['score'], levels=clevs_score, linewidths=2,linestyles='-',colors = [(0.5,0.5,0.5)])
        ax.clabel(contour, clevs_score, inline=True, fmt='%1.1f', fontsize=fontsize)
        
        ax2 = ax.twinx()
        ax2.set_yticks(np.array([0, 9, 17, 25, 33, 41, 49, 57]))
        ax2.set_yticklabels(['9', '81', '153', '225', '297', '369', '441', '513'], fontsize=fontsize)
        ax2.set_ylabel(r'precision [km$^2$]', fontsize=fontsize)

    if (flag == 4) or (flag == 5):
        ax.set_xlabel(r'lead time [days]', fontsize=fontsize,labelpad=0)

    ax.set_xticks(time)
    ax.set_xlim([time[0], time[-1]])
    ax.set_xticklabels(['1', '', '', '', '5', '', '', '', '', '10', '', '', '', '', '15'], fontsize=fontsize)
    
    ax.set_ylim([box_size[0], box_size[-2]])
    ax.set_title(title_text, fontsize=fontsize + 3)
    
    return p


# INPUT -----------------------
write2file = False
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'fmsess_tp24_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_2     = 'fbss_tp24_pval0.9_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_3     = 'fbss_tp24_pval0.1_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
figname_out       = 'fig_01.png'

# read in data
ds1        = xr.open_dataset(path_in + filename_in_1)
ds2        = xr.open_dataset(path_in + filename_in_2)    
ds3        = xr.open_dataset(path_in + filename_in_3)

# plot 
fontsize    = 11
clevs_score = np.arange(0,1.1,0.1)
clevs_ltg   = np.arange(-3.5, 3.75, 0.25)
cmap_score  = 'GnBu'
cmap_ltg    = plt.get_cmap('PiYG', clevs_ltg.size - 1) # -1 so that colorbar tick labels match individual colors
figsize     = np.array([12,12])
fig,ax      = plt.subplots(nrows=3,ncols=2,sharey='row',sharex='col',figsize=(figsize[0],figsize[1]))
ax          = ax.ravel()

title1 = 'a) daily anomalies'
title2 = 'b) daily anomalies'
title3 = 'c) daily 90$^{th}$ quantile extremes'
title4 = 'd) daily 90$^{th}$ quantile extremes'
title5 = 'e) daily 10$^{th}$ quantile extremes'
title6 = 'f) daily 10$^{th}$ quantile extremes'

setup_subplot(0, ax[0], ds1, title1, clevs_score, clevs_ltg, cmap_score, cmap_ltg, fontsize)

setup_subplot(2, ax[2], ds2, title3, clevs_score, clevs_ltg, cmap_score, cmap_ltg, fontsize)

p1 = setup_subplot(4, ax[4], ds3 , title5, clevs_score, clevs_ltg, cmap_score, cmap_ltg, fontsize)

setup_subplot(1, ax[1], ds1, title4, clevs_score,clevs_ltg, cmap_score, cmap_ltg, fontsize)

setup_subplot(3, ax[3], ds2, title5, clevs_score,clevs_ltg, cmap_score, cmap_ltg, fontsize)

p2 = setup_subplot(5, ax[5], ds3, title6, clevs_score,clevs_ltg, cmap_score, cmap_ltg, fontsize)

fig.subplots_adjust(right=0.925, left=0.075,top=0.96,hspace=0.15,wspace=0.075)

cb1_ax = fig.add_axes([0.075, 0.05, 0.41, 0.02])
cb1    = fig.colorbar(p1, cax=cb1_ax, orientation='horizontal',ticks=clevs_score, pad=0.025)
cb1.ax.tick_params(labelsize=fontsize, size=0) 
cb1.ax.set_title('accuracy [FMSESS or FBSS]', fontsize=fontsize,y=-1.75)

cb2_ax = fig.add_axes([0.515, 0.05, 0.41, 0.02])
cb2    = fig.colorbar(p2, cax=cb2_ax, orientation='horizontal',ticks=clevs_ltg[2::4], pad=0.025)
cb2.ax.tick_params(labelsize=fontsize, size=0)
cb2.ax.set_title('lead time gained or lost [days]', fontsize=fontsize,y=-1.75)

# write2file
if write2file: plt.savefig(path_out + figname_out)
plt.show()

