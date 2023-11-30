"""
calculates the lead-time gained by increasing spatial scale for a given
forecast skill based off of lead-time vs spatial scale fss data.
"""

import numpy    as np
import xarray   as xr
from forsikring import misc,s2s,verify,config
from matplotlib import pyplot as plt

# INPUT -----------------------------------------------
score_flag               = 'fss'
time_flag                = 'daily'                   # daily or weekly
variable                 = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain                   = 'europe'                 # europe or norway only? 
first_forecast_date      = '20200102'               # first initialization date of forecast (either a monday or thursday)
number_forecasts         = 313                      # number of forecasts
season                   = 'annual'                 # pick forecasts in specific season (djf,mam,jja,son,annual)
grids                    = ['0.25x0.25']
write2file               = False
# -----------------------------------------------------    

misc.tic()

# define stuff
forecast_dates          = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')
path_in                 = config.dirs['verify_s2s_forecast_daily']
path_out                = config.dirs['verify_s2s_forecast_daily']
prefix                  = 'fss_' + variable + '_' + time_flag + '_' + domain + '_' + season + '_' + forecast_dates[0] + '_' + forecast_dates[-1]
if len(grids) == 2: filename_in = prefix + '.nc'
else: filename_in = prefix + '_' + grids[0] + '.nc'

# read score data
score = xr.open_dataset(path_in + filename_in)
time  = score.time.values

# interpolate lead time dimension
score_interp = score[score_flag].interp(time=np.arange(time[0],time[-1]+0.2,0.2))
time_interp  = score_interp.time
box_size     = score_interp.box_size

# calculate lead time gained
lead_time_gained = score_interp.copy()
for bs in range(1,box_size.size):
    for t in range(0,time_interp.size):
        temp = np.absolute(score_interp[bs,t].values-score_interp[0,:].values)
        if time_interp[np.nanargmin(temp)].values == 1.0: # where there is no skill equivalent at grid resolution
            lead_time_gained[bs,t] = np.nan
        else:
            lead_time_gained[bs,t] = time_interp[t].values - time_interp[np.nanargmin(temp)].values

# merge with score 
lead_time_gained = lead_time_gained.rename('lead_time_gained')
score = xr.merge([score,lead_time_gained])

# write to file
if write2file: score.to_netcdf(path_out + filename_in)

misc.toc()
