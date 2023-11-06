"""
Converts era5 forecast format data into binary if greater or smaller 
than a quantile threshold calculated from its corresponding hindcast
format data
"""

import xarray    as xr
import numpy    as np
from forsikring import config,misc,s2s

# input ----------------------------------------------
time_flag           = 'time'                   # time or timescale
variable            = 't2m24'                  # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
first_forecast_date = '20210104'               # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 1                        # number of forecast initializations
season              = 'annual'
grid                = '0.25x0.25'              # '0.25x0.25' or '0.5x0.5'
box_sizes           = np.arange(1,3,2)        # smoothing box size in grid points per side. Must be odd!
pval                = np.array([0.9])          # percentile values
comp_lev            = 5                        # level of compression
write2file          = False
# ----------------------------------------------------

forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d').values
print(forecast_dates)

for date in forecast_dates:

    misc.tic()
    print('\ncalculating binary for smoothed era5 forecast format data with ' + date + ' and grid: ' + grid)

    # define stuff                                                                                                                                                         
    path_in_forecast     = config.dirs['era5_s2s_forecast_daily_smooth'] + variable + '/'
    path_in_quantile     = config.dirs['era5_s2s_hindcast_daily_percentile'] + variable + '/'
    path_out             = config.dirs['era5_s2s_forecast_daily_binary'] + variable + '/'
    filename_in_forecast = variable + '_' + grid + '_' + date + '.nc'
    filename_in_quantile = 'quantile_' + variable + '_' + time_flag + '_' + grid + '_' + date + '.nc'
    filename_out         = variable + '_' + grid + '_' + date + '.nc'
    
    # read data                                                                                                                 
    forecast = xr.open_dataset(path_in_forecast + filename_in_forecast)[variable]
    quantile = xr.open_dataset(path_in_quantile + filename_in_quantile)['quantile']

    print(forecast)
    print(quantile)
    
    """
    # convert time to timescale if applicable                                                                                                                              
    forecast = verify.resample_time_to_timescale(forecast, time_flag)
    """
    
    misc.toc()
