"""
Converts era5 forecast format data into binary if greater or smaller 
than a quantile threshold calculated from its corresponding hindcast
format data
"""

import xarray    as xr
import numpy    as np
from forsikring import config,misc,s2s, verify

# input ----------------------------------------------
time_flag           = 'time'                   # time or timescale
variable            = 'tp24'                  # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
first_forecast_date = '20200102'               # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 313                        # number of forecast initializations
season              = 'annual'
grid                = '0.25x0.25'              # '0.25x0.25' or '0.5x0.5'
pval                = 0.9          # percentile values
comp_lev            = 5                        # level of compression
write2file          = True
# ----------------------------------------------------

forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d').values
print(forecast_dates)

for date in forecast_dates:

    misc.tic()
    print('\ncalculating binary for smoothed era5 forecast format data with ' + date + ' and grid: ' + grid)

    # define stuff                                                                                                                                                         
    path_in_forecast     = config.dirs['era5_s2s_forecast_daily_smooth'] + variable + '/'
    path_in_quantile     = config.dirs['era5_s2s_hindcast_quantile'] + variable + '/'
    path_out             = config.dirs['era5_s2s_forecast_daily_binary'] + str(pval) + '/' + variable + '/'
    filename_in_forecast = variable + '_' + grid + '_' + date + '.nc'
    filename_in_quantile = 'quantile_' + variable + '_' + time_flag + '_' + grid + '_' + date + '.nc'
    filename_out         = 'binary_' + variable + '_' + time_flag + '_' + grid + '_' + date + '.nc'
    
    # read data                                                                                                                 
    forecast = xr.open_dataset(path_in_forecast + filename_in_forecast)[variable]
    quantile = xr.open_dataset(path_in_quantile + filename_in_quantile)['quantile'].sel(pval=pval,method='nearest')

    # convert time to timescale if applicable                                                                                                                              
    forecast = verify.resample_time_to_timescale(forecast, time_flag)

    # convert to binary
    binary = forecast.where(forecast < quantile, 1.0).where(forecast >= quantile, 0.0)

    if write2file: misc.to_netcdf_with_packing_and_compression(binary, path_out + filename_out)

    forecast.close()
    quantile.close()
    binary.close()

    misc.toc()
