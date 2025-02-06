"""
Plots fig. 6 in Dunn-Sigouin et al. 
"""

import numpy     as np
import xarray    as xr
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config
from forsikring  import dim_025x025 as dim
import matplotlib as mpl

def spatial_scale_scaling(dim):
    dim = misc.subselect_xy_domain_from_dim(dim,'scandinavia','0.25x0.25')
    return np.mean(np.cos(np.deg2rad(dim.latitude)))

def setup_subplot(flag, ax, ds, title_text, clevs_score, clevs_ltg, cmap_score, cmap_ltg, fontsize):
    """ 
    Sets up specifics of subplots for fig. 1
    """
    time        = ds['time']
    time_interp = ds['time_interp']
    box_size    = ds['box_size']

    if (flag == 0) or (flag == 2) or (flag == 4):
        p = ax.contourf(time, box_size, ds['score'], levels=clevs_score, cmap=cmap_score)
        ax.pcolor(time, box_size, ds['significance'], hatch='\\\\', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)

        dummy = ax.contour(time, box_size, ds['score'], levels=clevs_score, linewidths=2,linestyles='-',colors = [(0.5,0.5,0.5)])
        ax.clabel(dummy, clevs_score, inline=True, fmt='%1.1f', fontsize=fontsize)

        #ax.contour(time, box_size, ds['score'], levels=[0.8], linewidths=3,linestyles='-',colors = [(1.0,0.0,0.0)])
        
        ax.set_yticks(np.array([1, 9, 17, 25, 33, 41, 49, 57]))
        ax.set_yticklabels(['1', '9', '17', '25', '33', '41', '49', '57'], fontsize=fontsize)
        ax.set_ylabel(r'precision [gridpoints$^2$]', fontsize=fontsize)

        ax2 = ax.twinx()
        ax2.set_yticks(np.array([0, 9, 17, 25, 33, 41, 49, 57]))
        scaling = spatial_scale_scaling(dim)
        yticklabels = scaling*27*np.array([1, 9, 17, 25, 33, 41, 49, 57])
        ax2.set_yticklabels(yticklabels.astype(int), fontsize=fontsize)
        ax2.set_ylabel(r'precision [km$^2$]', fontsize=fontsize)

    #if (flag == 4) or (flag == 5):
    ax.set_xlabel(r'lead time [days]', fontsize=fontsize,labelpad=0)

    ax.set_xticks(time)
    ax.set_xlim([time[0], time[-1]])
    ax.set_xticklabels(['1', '', '', '', '5', '', '', '', '', '10', '', '', '', '', '15'], fontsize=fontsize)
    
    ax.set_ylim([box_size[0], box_size[-2]])
    #ax.set_title(title_text, fontsize=fontsize + 4,loc='left', ha='left', y=0.89, x=0.015, bbox={'facecolor': 'white', 'edgecolor': 'black', 'pad': 3})
    return p


# INPUT -----------------------
write2file = True
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'fmsess_tp24_daily_scandinavia_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
#figname_out       = 'fig_05.png'
figname_out       = 'test.png'

# read in data
ds1        = xr.open_dataset(path_in + filename_in_1)

# plot 
fontsize    = 11
clevs_score = np.arange(0,1.1,0.1)
clevs_ltg   = np.arange(-3.5, 3.75, 0.25)
cmap_score  = 'GnBu'
cmap_ltg    = plt.get_cmap('PiYG', clevs_ltg.size - 1) # -1 so that colorbar tick labels match individual colors
figsize     = np.array([8,6])
fig,ax      = plt.subplots(nrows=1,ncols=1,figsize=(figsize[0],figsize[1]))


p1 = setup_subplot(0, ax, ds1, 'a)', clevs_score, clevs_ltg, cmap_score, cmap_ltg, fontsize+2)

ax.annotate("", xy=(1, 33), xytext=(15, 33),arrowprops=dict(arrowstyle="<|-|>,head_length=0.6,head_width=0.4",linewidth=3, color='red'))
ax.annotate("", xy=(3, 1), xytext=(3, 57),arrowprops=dict(arrowstyle="<|-|>,head_length=0.6,head_width=0.4",linewidth=3, color='black'))
ax.annotate("", xy=(1, 9), xytext=(9, 57),arrowprops=dict(arrowstyle="<|-|>,head_length=0.6,head_width=0.4",linewidth=3, color='blue'))

fig.text(0.5, 0.52, 'fixed spatial\nprecision',horizontalalignment='center',
         bbox=dict(boxstyle='square,pad=.2',facecolor='w', edgecolor='k'),color='red',fontsize=fontsize+3)

#fig.text(0.29, 0.75, 'fixed lead\ntime',horizontalalignment='center',
#         bbox=dict(boxstyle='square,pad=.2',facecolor='w', edgecolor='k'),color='k',fontsize=fontsize+3)

#fig.text(0.54, 0.71,'optimized\naccuracy',
#         horizontalalignment='center',bbox=dict(boxstyle='square,pad=.2',facecolor='w', edgecolor='k'),color='blue',fontsize=fontsize+3)

fig.subplots_adjust(right=0.9, left=0.1,top=0.9,bottom=0.21)

cb1_ax = fig.add_axes([0.1, 0.075, 0.8, 0.04])
cb1    = fig.colorbar(p1, cax=cb1_ax, orientation='horizontal',ticks=clevs_score, pad=0.025)
cb1.ax.tick_params(labelsize=fontsize, size=0) 
cb1.ax.yaxis.set_label_position('right') 
cb1.set_label('accuracy [FMSESS]',
              fontsize=fontsize+2)

# write2file
if write2file: plt.savefig(path_out + figname_out)
plt.show()

