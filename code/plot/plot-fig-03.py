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
    Sets up specifics of subplots for fig. 2
    """
    p = ax.contourf(time, box_size, fss_data, levels=clevs, cmap=cmap, extend='min')
    ax.pcolor(time, box_size, sig_data, hatch='\\\\', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)

    ax.set_xticks(time)
    if time.size == 6:
        ax.set_xticklabels(['1d1d','2d2d','4d4d','1w1w','2w2w','4w3w'],fontsize=fontsize)
        ax.set_xlabel(r'lead time [timescale]',fontsize=fontsize)
    else:
        ax.set_xticklabels(['1', '', '3', '', '5', '', '7', '', '9', '', '11', '', '13', '', '15'], fontsize=fontsize)
        ax.set_xlabel(r'lead time [days]', fontsize=fontsize)
    ax.set_xlim([time[0], time[-1]])

    ax.set_yticks(np.array([1, 9, 17, 25, 33, 41, 49, 57]))
    ax.set_yticklabels(['1/0.25', '9/2.25', '17/4.25', '25/6.25', '33/8.25', '41/10.25', '49/12.25', '57/14.25'], fontsize=fontsize)
    if (title_text == 'a) europe') or (title_text == 'c) scandinavia'):
        ax.set_ylabel(r'spatial scale [gridpoints$^2$/degrees$^2$]', fontsize=fontsize)
    ax.set_ylim([box_size[0], box_size[-2]])

    ax.set_title(title_text, fontsize=fontsize + 3)
    cb = plt.colorbar(p, ax=ax, orientation='vertical', ticks=clevs, pad=0.025, aspect=15)
    cb.ax.set_title('fss', fontsize=fontsize)
    cb.ax.tick_params(labelsize=fontsize, size=0)
    return ax


# INPUT -----------------------
write2file = False
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'fss_tp24_time_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_2     = 'fss_difference_time_tp24_europe_annual_2020-01-02_2022-12-29_tp24_northern_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_3     = 'fss_difference_time_tp24_europe_annual_2020-01-02_2022-12-29_tp24_scandinavia_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_4     = 'fss_difference_time_tp24_europe_annual_2020-01-02_2022-12-29_tp24_southern_norway_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
figname_out       = 'fig_03.pdf'

# read in data
ds1        = xr.open_dataset(path_in + filename_in_1)
ds2        = xr.open_dataset(path_in + filename_in_2)                                                                                                                                                
ds3        = xr.open_dataset(path_in + filename_in_3)                                                                                           
ds4        = xr.open_dataset(path_in + filename_in_4)

# calculate significance
sig1       = s2s.mask_significant_values_from_bootstrap(ds1['fss_bootstrap'],0.05)
sig2       = s2s.mask_significant_values_from_bootstrap(ds2['fss_bootstrap'],0.05)
sig3       = s2s.mask_significant_values_from_bootstrap(ds3['fss_bootstrap'],0.05)
sig4       = s2s.mask_significant_values_from_bootstrap(ds4['fss_bootstrap'],0.05)

# plot 
fontsize   = 11
#clevs      = np.arange(0.0, 1.1, 0.1)
clevs      = np.arange(-0.2, 0.22, 0.02)
cmap       = mpl.cm.get_cmap("RdBu_r").copy()
#cmap       = mpl.cm.get_cmap("GnBu").copy()
figsize    = np.array([12,9])
fig,ax     = plt.subplots(nrows=2,ncols=2,sharey='row',sharex='col',figsize=(figsize[0],figsize[1]))
ax         = ax.ravel()

# A) europe
setup_subplot(ax[0], ds1['time'], ds1['box_size'], ds1['fss'], sig1, 'a) europe', clevs, cmap, fontsize)

# B) northern europe
setup_subplot(ax[1], ds2['time'], ds2['box_size'], ds2['fss'], sig2, 'b) northern europe', clevs, cmap, fontsize)

# B) scandinavia
setup_subplot(ax[2], ds3['time'], ds3['box_size'], ds3['fss'], sig3, 'c) scandinavia', clevs, cmap, fontsize)

# B) southern norway
setup_subplot(ax[3], ds4['time'], ds4['box_size'], ds4['fss'], sig4, 'd) southern norway', clevs, cmap, fontsize)


# write2file
plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()

