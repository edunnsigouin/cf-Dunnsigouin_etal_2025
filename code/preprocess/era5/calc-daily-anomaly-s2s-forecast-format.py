"""
Converts smoothed era5 s2s forecast format data into anomaly relative
to smoothed climatological mean from hindcast format data.
"""

import numpy    as np
import xarray   as xr
from forsikring import misc,s2s,config,verify

# INPUT -----------------------------------------------
time_flag           = 'daily'                 # daily or weekly
variables           = ['t2m24']              # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
first_forecast_date = '20210104'             # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 104                      # number of forecasts 
season              = 'annual'
grids               = ['0.5x0.5']          # '0.25x0.25' & '0.5x0.5'
write2file          = True
# -----------------------------------------------------

# get forecast dates 
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')
print(forecast_dates)

for variable in variables:
    for grid in grids:
        for date in forecast_dates:

            misc.tic()
            print('\nconverting forecast to anomaly ' + variable + ' for ' + grid + ' and initialization ' + date)
        
            # define stuff
            path_in_forecast  = config.dirs['era5_forecast_daily_smooth'] + variable + '/'
            path_in_clim      = config.dirs['era5_hindcast_' + time_flag + '_climatology'] + variable + '/'
            path_out          = config.dirs['era5_forecast_' + time_flag + '_anomaly'] + variable + '/'
            filename_forecast = variable + '_' + grid + '_' + date + '.nc'
            filename_clim     = variable + '_' + grid + '_' + date + '.nc'
            filename_out      = variable + '_' + grid + '_' + date + '.nc'
        
            # read forecast and climatology in forecast format
            da_forecast = xr.open_dataset(path_in_forecast + filename_forecast)[variable]
            da_clim     = xr.open_dataset(path_in_clim + filename_clim)[variable]

            # Convert time to timescale if applicable
            da_forecast = verify.resample_daily_to_weekly(da_forecast, time_flag, grid)
            
            # calc anomaly
            da_anomaly = da_forecast - da_clim

            # modify metadata
            if variable == 'tp24':
                da_anomaly.attrs['units']     = 'm'
                da_anomaly.attrs['long_name'] = 'anomalies of daily accumulated precipitation'
            elif variable == 't2m24':
                da_anomaly.attrs['units']     = 'K'
                da_anomaly.attrs['long_name'] = 'anomalies of daily-mean 2-meter temperature'
            elif variable == 'rn24':
                da_anomaly.attrs['units']     = 'm'
                da_anomaly.attrs['long_name'] = 'anomalies of daily accumulated rainfall'
            elif variable == 'mx24tpr':
                da_anomaly.attrs['units']     = 'kg m**-2 s**-1'
                da_anomaly.attrs['long_name'] = 'anomalies of daily maximum timestep precipitation rate'
            elif variable == 'mx24tp6':
                da_anomaly.attrs['units']     = 'm'
                da_anomaly.attrs['long_name'] = 'anomalies of daily maximum 6 hour accumulated precipitation'
            elif variable == 'mx24rn6':
                da_anomaly.attrs['units']     = 'm'
                da_anomaly.attrs['long_name'] = 'anomalies of daily maximum 6 hour accumulated rainfall'

            # write output
            if write2file: misc.to_netcdf_with_packing_and_compression(da_anomaly, path_out + filename_out)

            da_forecast.close()
            da_clim.close()
            da_anomaly.close()

            misc.toc()


