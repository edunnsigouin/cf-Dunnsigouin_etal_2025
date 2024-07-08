"""
Converts smoothed era5 s2s forecast format data into anomaly relative
to smoothed climatological mean from hindcast format data.
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
from forsikring import misc,s2s,config,verify

# INPUT -----------------------------------------------
time_flag           = 'daily'                 # daily or weekly
variable            = 'tp24'              # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
first_forecast_date = '20230803'             # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 10                      # number of forecasts 
season              = 'annual'
grid                = '0.25x0.25'          # '0.25x0.25' & '0.5x0.5'
domain              = 'scandinavia'
box_sizes           = np.arange(1,61,2)        # smoothing box size in grid points per side. Must be odd!  
write2file          = False
# -----------------------------------------------------

# get forecast dates 
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')
#forecast_dates = pd.date_range(first_forecast_date, periods=number_forecasts).strftime('%Y-%m-%d') 
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
    filename_out      = variable + '_' + grid + '_' + date + '.nc'

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

    # calculate climatological mean from hindcast 
    hindcast = hindcast.mean(dim='hdate')

    # calc anomaly
    anomaly = forecast - hindcast

    # apply spatial smoothing
    anomaly_smooth = verify.boxcar_smoother_xy_optimized(box_sizes, anomaly, 'xarray')
    
    # modify metadata
    anomaly_smooth = anomaly_smooth.rename(variable)
    if variable == 'tp24':
        anomaly_smooth.attrs['units']     = 'm'
        anomaly_smooth.attrs['long_name'] = 'anomalies of daily accumulated precipitation'
    elif variable == 't2m24':
        anomaly_smooth.attrs['units']     = 'K'
        anomaly_smooth.attrs['long_name'] = 'anomalies of daily-mean 2-meter temperature'
    elif variable == 'rn24':
        anomaly_smooth.attrs['units']     = 'm'
        anomaly_smooth.attrs['long_name'] = 'anomalies of daily accumulated rainfall'
    elif variable == 'mx24tpr':
        anomaly_smooth.attrs['units']     = 'kg m**-2 s**-1'
        anomaly_smooth.attrs['long_name'] = 'anomalies of daily maximum timestep precipitation rate'
    elif variable == 'mx24tp6':
        anomaly_smooth.attrs['units']     = 'm'
        anomaly_smooth.attrs['long_name'] = 'anomalies of daily maximum 6 hour accumulated precipitation'
    elif variable == 'mx24rn6':
        anomaly_smooth.attrs['units']     = 'm'
        anomaly_smooth.attrs['long_name'] = 'anomalies of daily maximum 6 hour accumulated rainfall'

    # write output
    if write2file: misc.to_netcdf_with_packing_and_compression(anomaly_smooth, path_out + filename_out)

    forecast.close()
    hindcast.close()
    anomaly.close()
    anomaly_smooth.close()

    misc.toc()


