"""
Plots fig. 2 in Dunn-Sigouin et al. 
"""

import numpy     as np
import xarray    as xr
from matplotlib  import pyplot as plt
from forsikring  import misc,s2s,config
import matplotlib as mpl


def setup_subplot_ltg(flag, ax, time, box_size, fss_data, sig_data, ltg_data, dummy, title_text, clevs1, clevs2, cmap, fontsize):
    """
    Sets up specifics of subplots for fig. 2
    """
    p = ax.contourf(ltg_data.time, box_size, ltg_data, levels=clevs2, cmap=cmap, extend='both')
    ax.pcolor(time, box_size, sig_data, hatch='\\\\', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)
    ax.pcolor(dummy.time, box_size, dummy, hatch='xx', cmap=mpl.colors.ListedColormap(['none']), edgecolor=[0.8,0.8,0.8], lw=0)

    contour = ax.contour(time, box_size, fss_data, levels=clevs1, linewidths=1,linestyles='-',colors='grey')
    ax.clabel(contour, clevs1, inline=True, fmt='%1.1f', fontsize=fontsize)

    ax.set_xticks(time)
    ax.set_xlim([time[0], time[-1]])

    if flag == 4:
        ax.set_xticklabels(['1','2','3','4','5','6'],fontsize=fontsize)
        ax.set_xlabel(r'lead time [weeks]',fontsize=fontsize)
    elif flag == 3:
        ax.set_xticklabels(['1', '', '', '', '5', '', '', '', '', '10', '', '', '', '', '15'], fontsize=fontsize)
        ax.set_xlabel(r'lead time [days]', fontsize=fontsize)

    ax.set_yticks(np.array([1, 9, 17, 25, 33, 41, 49, 57]))
    ax.set_yticklabels(['1/9', '9/81', '17/153', '25/225', '33/297', '41/369', '49/441', '57/513'], fontsize=fontsize)
    if (flag == 3) or (flag == 1):
        ax.set_ylabel(r'spatial scale [gridpoints$^2$/km$^2$]', fontsize=fontsize)
    ax.set_ylim([box_size[0], box_size[-2]])

    ax.set_title(title_text, fontsize=fontsize + 2)

    cb = plt.colorbar(p, ax=ax, orientation='vertical', ticks=clevs2, pad=0.025, aspect=15)
    if (flag == 3) or (flag == 1):
        cb.ax.set_title('[days]', fontsize=fontsize)
    elif (flag == 4) or (flag == 2):
        cb.ax.set_title('[weeks]', fontsize=fontsize)
    cb.ax.tick_params(labelsize=fontsize, size=0)

    return ax

# INPUT -----------------------
write2file = False
# -----------------------------

# define stuff         
path_in           = config.dirs['verify_s2s_forecast_daily']
path_out          = config.dirs['fig'] + 'paper/'
filename_in_1     = 'ltg_fss_tp24_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_2     = 'ltg_fss_tp24_weekly_europe_annual_2021-01-04_2021-12-30.nc'
filename_in_3     = 'test.nc' #'ltg_fbss_tp24_pval0.1_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_4     = 'ltg_fbss_tp24_pval0.1_weekly_europe_annual_2021-01-04_2021-12-30.nc'
filename_in_5     = 'fss_tp24_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_6     = 'fss_tp24_weekly_europe_annual_2021-01-04_2021-12-30.nc'
filename_in_7     = 'fbss_tp24_pval0.1_daily_europe_annual_2020-01-02_2022-12-29_0.25x0.25.nc'
filename_in_8     = 'fbss_tp24_pval0.1_weekly_europe_annual_2021-01-04_2021-12-30.nc'
figname_out       = 'fig_02.pdf'

# read in data
ds1        = xr.open_dataset(path_in + filename_in_1)
ds2        = xr.open_dataset(path_in + filename_in_2)    
ds3        = xr.open_dataset(path_in + filename_in_3)
ds4        = xr.open_dataset(path_in + filename_in_4)

ds5        = xr.open_dataset(path_in + filename_in_5)
ds6        = xr.open_dataset(path_in + filename_in_6)
ds7        = xr.open_dataset(path_in + filename_in_7)
ds8        = xr.open_dataset(path_in + filename_in_8)

# Remove box sizes where low and high-res data don't overlap on the same grid in timescale dimension data
index      = np.where(~np.isnan(ds2['lead_time_gained'][:,4]))[0]
ds2        = ds2.isel(box_size=index)
ds4        = ds4.isel(box_size=index)
ds6        = ds6.isel(box_size=index)
ds8        = ds8.isel(box_size=index)

# significance
sig1 = s2s.mask_significant_values_from_bootstrap(ds5['fss_bootstrap'],0.05)
sig2 = s2s.mask_significant_values_from_bootstrap(ds6['fss_bootstrap'],0.05)
sig3 = s2s.mask_significant_values_from_bootstrap(ds7['fbss_bootstrap'],0.05)
sig4 = s2s.mask_significant_values_from_bootstrap(ds8['fbss_bootstrap'],0.05)

dummy1 = s2s.mask_skill_values(ds1['lead_time_gained'])
dummy2 = s2s.mask_skill_values(ds2['lead_time_gained'])
dummy3 = s2s.mask_skill_values(ds3['lead_time_gained'])
dummy4 = s2s.mask_skill_values(ds4['lead_time_gained'])


# set ltg values to nan where fss not-significant. makes figure nicer. Hacky
time_interp = ds1['lead_time_gained'].time.astype('int')
time        = sig1.time.values
for bs in range(1,ds1['box_size'].size):
    index1                              = time[np.where(sig1[bs,:] == 1.0)[0]]
    index2                              = np.where(time_interp == index1[0])[0][0]-2
    ds1['lead_time_gained'][bs,index2:] = np.nan
    index1                              = time[np.where(sig3[bs,:] == 1.0)[0]]
    index2                              = np.where(time_interp == index1[0])[0][0]-2
    ds3['lead_time_gained'][bs,index2:] = np.nan
    
time_interp = ds2['lead_time_gained'].time.astype('int')
time        = sig2.time.values
for bs in range(1,ds2['box_size'].size):
    index1                              = time[np.where(sig2[bs,:] == 1.0)[0]]
    index2                              = np.where(time_interp == index1[0])[0][0]-2
    ds2['lead_time_gained'][bs,index2:] = np.nan
    index1                              = time[np.where(sig4[bs,:] == 1.0)[0]]
    index2                              = np.where(time_interp == index1[0])[0][0]-2
    ds4['lead_time_gained'][bs,index2:] = np.nan


# plot 
fontsize   = 11
clevs1     = np.arange(0,1.1,0.1)
clevs2     = np.arange(-4.0, 4.5, 0.5)
clevs3     = np.arange(0.0, 1.2, 0.2)
cmap2      = mpl.cm.get_cmap("PiYG").copy()
figsize    = np.array([12,8])
fig,ax     = plt.subplots(nrows=2,ncols=2,sharey='row',sharex='col',figsize=(figsize[0],figsize[1]))
ax         = ax.ravel()

title1 = 'a) daily precipitation'
title2 = 'b) weekly precipitation'
title3 = 'c) daily 90$^{th}$ quantile precipitation'
title4 = 'd) weekly 90$^{th}$ quantile precipitation'

setup_subplot_ltg(1, ax[0], sig1['time'], ds1['box_size'], ds5['fss'], sig1, ds1['lead_time_gained'], dummy1, title1, clevs1, clevs2, cmap2, fontsize)

setup_subplot_ltg(2, ax[1], sig2['time'], ds2['box_size'], ds6['fss'], sig2, ds2['lead_time_gained']*7, dummy2, title2, clevs1, clevs2, cmap2, fontsize)

setup_subplot_ltg(3, ax[2], sig3['time'], ds3['box_size'], ds7['fbss'], sig3, ds3['lead_time_gained'], dummy3, title3, clevs1, clevs2, cmap2, fontsize)

setup_subplot_ltg(4, ax[3], sig4['time'], ds4['box_size'], ds8['fbss'], sig4, ds4['lead_time_gained']*7, dummy4, title4, clevs1, clevs2, cmap2, fontsize)


# write2file
plt.tight_layout()
if write2file: plt.savefig(path_out + figname_out)
plt.show()

