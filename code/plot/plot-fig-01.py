"""
Plots fig. 1 in Dunn-Sigouin et al. 
"""

import numpy     as np
import xarray    as xr
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config
import matplotlib as mpl


def setup_subplot_fss(flag, ax, ds, title_text, clevs, cmap, fontsize):
    """ 
    Sets up specifics of subplots for fig. 1
    """
    time     = ds['time']
    box_size = ds['box_size']
    
    p = ax.contourf(time, box_size, ds['score'], levels=clevs, cmap=cmap, extend='min')
    ax.pcolor(time, box_size, ds['significance'], hatch='\\\\', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)

    contour = ax.contour(time, box_size, ds['score'], levels=clevs, linewidths=1,linestyles='-',colors='grey')
    ax.clabel(contour, clevs, inline=True, fmt='%1.1f', fontsize=fontsize)

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
        ax.set_ylabel(r'spatial scale [gridpoints$^2$]', fontsize=fontsize)

    ax.set_ylim([box_size[0], box_size[-2]])

    if (flag == 2) or (flag == 4) or (flag == 6):
        ax2 = ax.twinx()
        ax2.set_yticks(np.array([0, 9, 17, 25, 33, 41, 49, 57]))
        ax2.set_yticklabels(['9', '81', '153', '225', '297', '369', '441', '513'], fontsize=fontsize)
        ax2.set_ylabel(r'spatial scale [km$^2$]', fontsize=fontsize)
        
    ax.set_title(title_text, fontsize=fontsize + 3)
    
    return p

# INPUT -----------------------
write2file = False
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'fmsess_tp24_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc' #'fss_tp24_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
#filename_in_2     = 'fss_tp24_weekly_europe_annual_2021-01-04_2021-12-30.nc'
filename_in_3     = 'fbss_tp24_pval0.9_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'# 'fbss_tp24_pval0.9_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
#filename_in_4     = 'fbss_tp24_pval0.9_weekly_europe_annual_2021-01-04_2021-12-30.nc'
filename_in_5     = 'fbss_tp24_pval0.1_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_6     = 'fbss_tp24_pval0.1_weekly_europe_annual_2021-01-04_2021-12-30.nc'
figname_out       = 'fig_01.pdf'

# read in data
ds1        = xr.open_dataset(path_in + filename_in_1)
#ds2        = xr.open_dataset(path_in + filename_in_2)    
ds3        = xr.open_dataset(path_in + filename_in_3)
#ds4        = xr.open_dataset(path_in + filename_in_4)
ds5        = xr.open_dataset(path_in + filename_in_5)
ds6        = xr.open_dataset(path_in + filename_in_6)

print(ds6['significance'].values)

# Remove box sizes where low and high-res data don't overlap on the same grid in timescale dimension data
#index      = np.where(~np.isnan(ds2['fss'][:,4]))[0]
#ds2        = ds2.isel(box_size=index)
#index      = np.where(~np.isnan(ds4['fbss'][:,4]))[0]
#ds4        = ds4.isel(box_size=index)
index      = np.where(~np.isnan(ds6['score'][:,4]))[0] 
ds6        = ds6.isel(box_size=index)

# calculate significance
#sig1       = s2s.mask_significant_values_from_bootstrap(ds1['fss_bootstrap'],0.05)
#sig2       = s2s.mask_significant_values_from_bootstrap(ds2['fss_bootstrap'],0.05)
#sig3       = s2s.mask_significant_values_from_bootstrap(ds3['fbss_bootstrap'],0.05)
#sig4       = s2s.mask_significant_values_from_bootstrap(ds4['fbss_bootstrap'],0.05)
#sig5       = s2s.mask_significant_values_from_bootstrap(ds5['fbss_bootstrap'],0.05)
#sig6       = s2s.mask_significant_values_from_bootstrap(ds6['fbss_bootstrap'],0.05)

# plot 
fontsize   = 11
clevs1     = np.arange(0,1.1,0.1)
clevs2     = np.arange(0.0, 3.5, 0.5)
clevs3     = np.arange(0.0, 1.1, 0.1)
cmap1      = mpl.cm.get_cmap("GnBu").copy()
figsize    = np.array([12,12])
fig,ax     = plt.subplots(nrows=3,ncols=2,sharey='row',sharex='col',figsize=(figsize[0],figsize[1]))
ax         = ax.ravel()

title1 = 'a) daily precipitation'
title2 = 'b) weekly precipitation'
title3 = 'c) daily 90$^{th}$ quantile precipitation'
title4 = 'd) weekly 90$^{th}$ quantile precipitation'
title5 = 'e) daily 10$^{th}$ quantile precipitation'
title6 = 'f) weekly 10$^{th}$ quantile precipitation'

setup_subplot_fss(1, ax[0], ds1, title1, clevs1, cmap1, fontsize)

#setup_subplot_fss(2, ax[1], ds2['time'], ds2['box_size'], ds2['fss'], sig2, title2, clevs1, cmap1, fontsize)

setup_subplot_fss(3, ax[2], ds3, title3, clevs1, cmap1, fontsize)

#setup_subplot_fss(4, ax[3], ds4['time'], ds4['box_size'], ds4['fbss'], sig4, title4, clevs1, cmap1, fontsize)

setup_subplot_fss(5, ax[4], ds5 , title5, clevs1, cmap1, fontsize)

p = setup_subplot_fss(6, ax[5], ds6, title6, clevs1, cmap1, fontsize)

fig.subplots_adjust(right=0.925, left=0.075,top=0.96,hspace=0.15,wspace=0.075)
cbar_ax = fig.add_axes([0.2, 0.035, 0.6, 0.02])
cb = fig.colorbar(p, cax=cbar_ax, orientation='horizontal',ticks=clevs1, pad=0.025)
cb.ax.tick_params(labelsize=fontsize, size=0) 
cb.ax.set_title('[fmsess/fbss]', fontsize=fontsize,y=1.01)


# write2file
if write2file: plt.savefig(path_out + figname_out)
plt.show()

