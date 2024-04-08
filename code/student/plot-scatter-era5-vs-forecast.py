"""
Plots era5 vs forecast at a given lead time. Sanity check to make sure data
is correct. expect high correlation at short lead times
"""

import numpy             as np
import xarray            as xr
from forsikring          import s2s,config,verify
import matplotlib.pyplot as plt

# Input -------------------------------------
variable              = 'tp24'              # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
first_forecast_date   = '2017-01-02'          # first initialization date of forecast (either a monday or thursday)
last_forecast_date    = '2022-12-29'
season                = 'annual'
grid                  = '0.25x0.25'         
write2file            = True
# -------------------------------------------

# defne stuff
path_in_s2s             = config.dirs['s2s_forecast_daily_student_combined']
path_in_era5            = config.dirs['era5_forecast_daily_student_combined']
path_out                = '/nird/home/edu061/cf-forsikring/fig/master/'
timestamp               = first_forecast_date + '_' + last_forecast_date
filename_in_s2s_bergen  = 'forecast_' + variable + '_bergen_' + grid + '_' + timestamp  + '.nc'
filename_in_era5_bergen = 'observation_' + variable + '_bergen_' + grid + '_' + timestamp  + '.nc'
filename_in_s2s_oslo    = 'forecast_' + variable + '_oslo_' + grid + '_' + timestamp  + '.nc'
filename_in_era5_oslo   = 'observation_' + variable + '_oslo_' + grid + '_' + timestamp  + '.nc'
figname                 = 'correlation.' + variable + '.obs.vs.forecast.bergen.oslo.' + timestamp + '.pdf'

# read data
ds_s2s_bergen  = xr.open_dataset(path_in_s2s + filename_in_s2s_bergen)[variable]
ds_era5_bergen = xr.open_dataset(path_in_era5 + filename_in_era5_bergen)[variable]
ds_s2s_oslo  = xr.open_dataset(path_in_s2s + filename_in_s2s_oslo)[variable]
ds_era5_oslo = xr.open_dataset(path_in_era5 + filename_in_era5_oslo)[variable]

# average over all boxes
ds_s2s_bergen  = ds_s2s_bergen.mean(dim='longitude').mean(dim='latitude')
ds_era5_bergen = ds_era5_bergen.mean(dim='longitude').mean(dim='latitude')
ds_s2s_oslo    = ds_s2s_oslo.mean(dim='longitude').mean(dim='latitude')
ds_era5_oslo   = ds_era5_oslo.mean(dim='longitude').mean(dim='latitude')

# average over ensemble members
ds_s2s_bergen = ds_s2s_bergen.mean(dim='number')
ds_s2s_oslo   = ds_s2s_oslo.mean(dim='number')

# correlation calculation
correlation = np.zeros([ds_s2s_bergen.lead_time.size,2])
for t,lt in enumerate(ds_s2s_bergen.lead_time):
    correlation[t,0] = np.corrcoef(ds_era5_bergen[:,t],ds_s2s_bergen[:,t])[0,1]
    correlation[t,1] = np.corrcoef(ds_era5_oslo[:,t],ds_s2s_oslo[:,t])[0,1]
    
# plot
figsize = np.array([4*1.61,4])
fig,ax  = plt.subplots(figsize=(figsize[0],figsize[1]))
plt.scatter(ds_s2s_bergen.lead_time,correlation[:,0],c='k',label='bergen')
plt.scatter(ds_s2s_oslo.lead_time,correlation[:,1],c='b',label='oslo')
plt.legend(loc='upper right')
ax.set_title('correlation between observations and forecast \n for init_dates ' + timestamp,fontsize=11)
ax.set_xticks(ds_s2s_bergen.lead_time)
ax.set_xlim([0.5,15.5])
ax.set_yticks(np.arange(0,1.1,0.1))
ax.set_ylim([0,1.0])
ax.set_xlabel('lead time (days)')
ax.set_ylabel('correlation')
plt.tight_layout()
if write2file: plt.savefig(path_out + figname)
plt.show()

