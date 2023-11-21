"""
Plots time vs sparial scale of a forecast score
"""

import numpy     as np
import xarray    as xr
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config
import matplotlib as mpl

def setup_subplot(ax, time, box_size, fss_data, sig_data, title_text, clevs, cmap, fontsize):
    """
    Sets up specifics of subplot
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
    cb.ax.set_title('fss', fontsize=fontsize)
    cb.ax.tick_params(labelsize=fontsize, size=0)
    return ax

# INPUT -----------------------
variable   = 'fbss'
write2file = False
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'forecast/'
filename_in       = 'fbss_tp24_pval0.1_time_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
figname_out       = 'fbss_tp24_pval0.9_time_europe_annual_2020-01-02_2022-12-29_0.25x0.25.pdf'

# read in data
ds = xr.open_dataset(path_in + filename_in)

# Remove box sizes where low and high-res data don't overlap on the same grid in timescale dimension data
#index         = np.where(~np.isnan(ds[variable][:,4]))[0]
#ds            = ds.isel(box_size=index)

# calculate significance
sig       = s2s.mask_significant_values_from_bootstrap(ds[variable + '_bootstrap'],0.05)

# plot 
fontsize   = 11
title      = ''
clevs      = np.arange(0.0, 1.1, 0.1)
clevs_anom = np.arange(-0.5, 0.55, 0.05)
cmap       = mpl.cm.get_cmap("GnBu").copy()
cmap_anom  = mpl.cm.get_cmap("RdBu_r").copy()
figsize    = np.array([4*1.61,4])
fig,ax     = plt.subplots(nrows=1,ncols=1,figsize=(figsize[0],figsize[1]))

# A) precipitation
setup_subplot(ax, ds['time'], ds['box_size'], ds[variable], sig, title, clevs, cmap, fontsize)

# write2file
plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()

