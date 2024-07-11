"""
Converts smoothed s2s forecast format data into anomaly relative
to smoothed climatological mean from hindcast data.

modified for use in fig 05 of paper. Here I choose the most recent hindcast 
because some of th forecasts dont have corresponding hindcasts! 
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
import os
from   datetime import datetime
from forsikring import misc,s2s,config,verify

def find_most_recent_hindcast(forecast_file, hindcast_dir):
    # Extract date from the forecast filename
    forecast_date_str = os.path.basename(forecast_file).split('_')[-1].split('.')[0]
    forecast_date = datetime.strptime(forecast_date_str, '%Y-%m-%d')

    # List all hindcast files in the directory
    hindcast_files = [f for f in os.listdir(hindcast_dir) if f.endswith('.nc')]

    # Find the most recent hindcast file 
    most_recent_hindcast = None
    most_recent_date = None

    for file in hindcast_files:
        hindcast_date_str = file.split('_')[-1].split('.')[0]
        hindcast_date = datetime.strptime(hindcast_date_str, '%Y-%m-%d')

        if hindcast_date <= forecast_date:
            if most_recent_date is None or hindcast_date > most_recent_date:
                most_recent_hindcast = file
                most_recent_date = hindcast_date

    return os.path.join(hindcast_dir, most_recent_hindcast) if most_recent_hindcast else None


# INPUT -----------------------------------------------
time_flag           = 'daily'                 # daily or weekly
variable            = 'tp24'              # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
first_forecast_date = '20230803'             # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 6                      # number of forecasts 
season              = 'annual'
grid                = '0.25x0.25'          # '0.25x0.25' & '0.5x0.5'
domain              = 'scandinavia'
box_sizes           = np.arange(1,61,2)        # smoothing box size in grid points per side. Must be odd!  
write2file          = True
# -----------------------------------------------------

# get forecast dates 
forecast_dates = pd.date_range(first_forecast_date, periods=number_forecasts).strftime('%Y-%m-%d') 
print(forecast_dates)

for date in forecast_dates:

    misc.tic()
    print('\n ' + variable + ', ' + grid + ', ' + date)
        
    # define stuff
    path_in_forecast  = config.dirs['s2s_forecast_daily'] + variable + '/'
    path_in_hindcast  = config.dirs['s2s_hindcast_daily'] + variable + '/'
    path_out          = config.dirs['s2s_forecast_' + time_flag + '_anomaly'] + '/' + domain + '/' + variable + '/'
    filename_forecast = path_in_forecast + variable + '_' + grid + '_' + date + '.nc'
    filename_hindcast = find_most_recent_hindcast(filename_forecast, path_in_hindcast) # find most recent bi-weekly hindcast!   
    filename_out      = path_out + variable + '_' + grid + '_' + date + '.nc'

    # read forecast and hindcast format data from specific domain
    dim      = verify.get_data_dimensions(grid, time_flag, domain)
    forecast = xr.open_dataset(filename_forecast).sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')[variable]
    hindcast = xr.open_dataset(filename_hindcast).sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')[variable]

    # calculate hindcast climatology and forecast ensemble mean
    hindcast = hindcast.mean(dim='number').mean(dim='hdate')
    forecast = forecast.mean(dim='number')
    
    # resample to weekly if applicable
    forecast = verify.resample_daily_to_weekly(forecast, time_flag, grid, variable)
    hindcast = verify.resample_daily_to_weekly(hindcast, time_flag, grid, variable)

    # calc anomaly
    anomaly = forecast - hindcast.values

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
    if write2file: misc.to_netcdf_with_packing_and_compression(anomaly_smooth, filename_out)

    forecast.close()
    hindcast.close()
    anomaly.close()
    anomaly_smooth.close()

    misc.toc()


