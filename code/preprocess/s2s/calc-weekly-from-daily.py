"""
Converts smoothed s2s forecast format data into anomaly relative
to smoothed climatological mean from hindcast data.
"""

import numpy    as np
import xarray   as xr
from forsikring import misc,s2s,config,verify

# INPUT -----------------------------------------------
product             = 'hindcast'          # forecast or hindcast
variable            = 'tp24'              # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
first_forecast_date = '20200102'             # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 313                      # number of forecasts 
season              = 'annual'
grid                = '0.25x0.25'          # '0.25x0.25' & '0.5x0.5'
write2file          = True
# -----------------------------------------------------

# get forecast dates 
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')
print(forecast_dates)

for date in forecast_dates:

    misc.tic()
    print('\n ' + variable + ', ' + grid + ', ' + date)
        
    # define stuff
    path_in           = config.dirs['s2s_' + product + '_daily'] + variable + '/'
    path_out          = config.dirs['s2s_' + product + '_weekly'] + variable + '/'
    filename_in       = variable + '_' + grid + '_' + date + '.nc'
    filename_out      = variable + '_' + grid + '_' + date + '.nc'

    # read daily forecast data
    data = xr.open_dataset(path_in + filename_in)[variable]

    # resample daily forecast to weekly 
    data = verify.resample_daily_to_weekly(data,'weekly', grid, variable)

    # modify metadata
    if variable == 'tp24':
        data.attrs['units']     = 'm'
        data.attrs['long_name'] = 'weekly accumulated precipitation'
    elif variable == 't2m24':
        data.attrs['units']     = 'K'
        data.attrs['long_name'] = 'weekly-mean 2-meter temperature'
    
    # write output
    if write2file: misc.to_netcdf_with_packing_and_compression(data, path_out + filename_out)

    data.close()

    misc.toc()

