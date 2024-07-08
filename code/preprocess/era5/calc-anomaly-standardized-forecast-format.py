"""
Converts era5 s2s forecast format data into anomaly relative
to climatological mean from hindcast format data and then spatially 
smooths output.
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
from forsikring import misc,s2s,config,verify

# INPUT -----------------------------------------------
time_flag           = 'daily'                 # daily or weekly
variable            = 'tp24'              # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
first_forecast_date = '20230809'             # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 1                      # number of forecasts 
season              = 'annual'
grid                = '0.25x0.25'          # '0.25x0.25' & '0.5x0.5'
domain              = 'scandinavia'
box_sizes           = np.arange(1,61,2)        # smoothing box size in grid points per side. Must be odd!  
write2file          = False
# -----------------------------------------------------

# get forecast dates 
#forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')
forecast_dates = pd.date_range(first_forecast_date, periods=number_forecasts).strftime('%Y-%m-%d')
print(forecast_dates)

for date in forecast_dates:

    misc.tic()
    print('\n ' + variable + ', ' + grid + ', ' + date)
        
    # define stuff
    path_in_forecast  = config.dirs['era5_forecast_daily'] + variable + '/'
    path_in_hindcast  = config.dirs['era5_hindcast_daily'] + variable + '/'
    path_out          = config.dirs['era5_forecast_' + time_flag + '_anomaly'] + '/' + domain + '/' + variable + '/'
    filename_forecast = variable + '_' + grid + '_' + date + '.nc'
    filename_hindcast = variable + '_' + grid + '_' + date + '.nc'
    filename_out      = variable + '_' + grid + '_' + date + '_standardized.nc'

    # read forecast and hindcast format data
    forecast = xr.open_dataset(path_in_forecast + filename_forecast)[variable]
    hindcast = xr.open_dataset(path_in_hindcast + filename_hindcast)[variable]

    # extract domain
    dim      = verify.get_data_dimensions(grid, time_flag, domain)
    forecast = forecast.sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')
    hindcast = hindcast.sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')
    
    # resample to weekly if applicable
    forecast = verify.resample_daily_to_weekly(forecast, time_flag, grid, variable)
    hindcast = verify.resample_daily_to_weekly(hindcast, time_flag, grid, variable)

    # apply spatial smoothing. Note here that in order to standardize correctly,
    # you need to smooth the forecast & hindcast before standardizing since
    # its not a linear operation.
    forecast = verify.boxcar_smoother_xy_optimized(box_sizes, forecast, 'xarray')
    hindcast = verify.boxcar_smoother_xy_optimized(box_sizes, hindcast, 'xarray')

    # calc smoothed & standardized anomaly.
    # sample to calculate climatology and standard deviation is hindcast initialization dates.
    anomaly = (forecast - hindcast.mean(dim='hdate')) / hindcast.std(dim='hdate')

    # modify metadata
    anomaly = anomaly.rename(variable)
    if variable == 'tp24':
        anomaly.attrs['units']     = 'standard deviations'
        anomaly.attrs['long_name'] = 'standardized anomalies of daily accumulated precipitation'
    elif variable == 't2m24':
        anomaly.attrs['units']     = 'standard deviations'
        anomaly.attrs['long_name'] = 'standardized anomalies of daily-mean 2-meter temperature'
    elif variable == 'rn24':
        anomaly.attrs['units']     = 'standard deviations'
        anomaly.attrs['long_name'] = 'standardized anomalies of daily accumulated rainfall'
    elif variable == 'mx24tpr':
        anomaly.attrs['units']     = 'standard deviations'
        anomaly.attrs['long_name'] = 'standardized anomalies of daily maximum timestep precipitation rate'
    elif variable == 'mx24tp6':
        anomaly.attrs['units']     = 'standard deviations'
        anomaly.attrs['long_name'] = 'standardized anomalies of daily maximum 6 hour accumulated precipitation'
    elif variable == 'mx24rn6':
        anomaly.attrs['units']     = 'standard deviations'
        anomaly.attrs['long_name'] = 'standardized anomalies of daily maximum 6 hour accumulated rainfall'

    # write output
    if write2file: misc.to_netcdf_with_packing_and_compression(anomaly, path_out + filename_out)

    forecast.close()
    hindcast.close()
    anomaly.close()

    misc.toc()


