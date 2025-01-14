"""
Plots fig. 3 in Dunn-Sigouin et al. 
"""

import numpy     as np
import xarray    as xr
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config
import matplotlib as mpl


def setup_subplot(flag, ax, ds, title_text, clevs_score, clevs_ltg, cmap_score, cmap_ltg, fontsize):
    """ 
    Sets up specifics of subplots for fig. 3
    """
    time        = ds['time']
    time_interp = ds['time_interp']
    box_size    = ds['box_size']

    if (flag == 0) or (flag == 2) or (flag == 4):
        p = ax.contourf(time, box_size, ds['score'], levels=clevs_score, cmap=cmap_score)
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
        ax.set_xlabel(r'lead time [weeks]',fontsize=fontsize,labelpad=0)

    ax.set_xticks(time)
    ax.set_xlim([time[0], time[-1]])
    ax.set_xticklabels(['1','2','3','4','5','6'],fontsize=fontsize)
    
    ax.set_ylim([box_size[0], box_size[-2]])
    ax.set_title(title_text, fontsize=fontsize + 4,loc='left', ha='left', y=0.89, x=0.015, bbox={'facecolor': 'white', 'edgecolor': 'black', 'pad': 3})
    
    return p


# INPUT -----------------------
write2file = True
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'fmsess_t2m24_weekly_europe_annual_2020-01-02_2021-12-30.nc'
filename_in_2     = 'fbss_t2m24_pval0.9_weekly_europe_annual_2020-01-02_2021-12-30.nc'
filename_in_3     = 'fbss_t2m24_pval0.1_weekly_europe_annual_2020-01-02_2021-12-30.nc'
figname_out       = 'fig_S4.png'

# read in data
ds1        = xr.open_dataset(path_in + filename_in_1)
ds2        = xr.open_dataset(path_in + filename_in_2)    
ds3        = xr.open_dataset(path_in + filename_in_3)

# convert weekly lead_time_gained to units of days    
#ds1['lead_time_gained'] = ds1['lead_time_gained']*7
#ds2['lead_time_gained'] = ds2['lead_time_gained']*7
#ds3['lead_time_gained'] = ds3['lead_time_gained']*7

# plot 
fontsize    = 11
clevs_score = np.arange(0,1.1,0.1)
clevs_ltg   = np.arange(-3.5, 3.75, 0.25)
cmap_score  = 'GnBu'
cmap_ltg    = plt.get_cmap('PiYG', clevs_ltg.size - 1) # -1 so that colorbar tick labels match individual colors
figsize     = np.array([12,12])
fig,ax      = plt.subplots(nrows=3,ncols=2,sharey='row',sharex='col',figsize=(figsize[0],figsize[1]))
ax          = ax.ravel()

fig.text(0.5, 0.965, 'anomalies',horizontalalignment='center',color='k',fontsize=fontsize+4)
fig.text(0.5, 0.675, '0.9 quantile extremes',horizontalalignment='center',color='k',fontsize=fontsize+4)
fig.text(0.5, 0.38, '0.1 quantile extremes',horizontalalignment='center',color='k',fontsize=fontsize+4)

setup_subplot(0, ax[0], ds1, 'a)', clevs_score, clevs_ltg, cmap_score, cmap_ltg, fontsize)

setup_subplot(2, ax[2], ds2, 'c)', clevs_score, clevs_ltg, cmap_score, cmap_ltg, fontsize)

p1 = setup_subplot(4, ax[4], ds3, 'e)', clevs_score, clevs_ltg, cmap_score, cmap_ltg, fontsize)

setup_subplot(1, ax[1], ds1, 'b)', clevs_score,clevs_ltg, cmap_score, cmap_ltg, fontsize)

setup_subplot(3, ax[3], ds2, 'd)', clevs_score,clevs_ltg, cmap_score, cmap_ltg, fontsize)

p2 = setup_subplot(5, ax[5], ds3, 'f)', clevs_score,clevs_ltg, cmap_score, cmap_ltg, fontsize)

fig.subplots_adjust(right=0.925, left=0.075,top=0.96,hspace=0.12,wspace=0.04)

cb1_ax = fig.add_axes([0.075, 0.045, 0.41, 0.02])
cb1    = fig.colorbar(p1, cax=cb1_ax, orientation='horizontal',ticks=clevs_score, pad=0.025)
cb1.ax.tick_params(labelsize=fontsize, size=0) 
cb1.ax.set_title('accuracy [FMSESS or FBSS]', fontsize=fontsize+3,y=-2)

cb2_ax = fig.add_axes([0.515, 0.045, 0.41, 0.02])
cb2    = fig.colorbar(p2, cax=cb2_ax, orientation='horizontal',ticks=clevs_ltg[2::4], pad=0.025)
cb2.ax.tick_params(labelsize=fontsize, size=0)
cb2.ax.set_title('lead time gained or lost [weeks]', fontsize=fontsize+3,y=-2)

# write2file
if write2file: plt.savefig(path_out + figname_out)
plt.show()

