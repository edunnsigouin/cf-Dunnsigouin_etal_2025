"""
Calculates climatology per xy grid point from ecmwf smoothed 
hindcast data
"""

import numpy           as np
import xarray          as xr
from forsikring        import misc,s2s,config
import os

# input ----------------------------------------------
variables            = ['t2m24']                  # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
first_forecast_date  = '20210104'              # first initialization date of forecast (either a monday or thursday)   
number_forecasts     = 104                     # number of forecast initializations 
season               = 'annual'
grids                = ['0.25x0.25'] # '0.25x0.25' or '0.5x0.5'
write2file           = False
# ----------------------------------------------------

# get all dates for monday and thursday forecast initializations
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')
print(forecast_dates)

for variable in variables:
    for grid in grids:
        for date in forecast_dates:
        
            misc.tic()
            print('\ncalculating climatology for hindcast ' + date + ' and grid: ' + grid)
        
            # define stuff
            dim             = misc.get_dim(grid,'time')
            path_in         = config.dirs['s2s_hindcast_daily_smooth'] + variable + '/'
            path_out        = config.dirs['s2s_hindcast_climatology'] + variable + '/'
            filename_in     = variable + '_' + grid + '_' + date + '.nc'
            filename_out    = 'climatology_' + variable + '_' + grid + '_' + date + '.nc'

            # read in data
            da = xr.open_dataset(path_in + filename_in)[variable]

            # calculate climatological and ensemble mean
            da = da.mean(dim='hdate').mean(dim='number')

            # modify metadata
            if variable == 'tp24':
                da.attrs['units']     = 'm'
                da.attrs['long_name'] = 'climatological and ensemble mean daily accumulated precipitation'
            elif variable == 't2m24':
                da.attrs['units']     = 'K'
                da.attrs['long_name'] = 'climatological and ensemble mean daily-mean 2-meter temperature'
            elif variable == 'rn24':
                da.attrs['units']     = 'm'
                da.attrs['long_name'] = 'climatological and ensemble mean daily accumulated rainfall'
            elif variable == 'mx24tpr':
                da.attrs['units']     = 'kg m**-2 s**-1'
                da.attrs['long_name'] = 'climatological and ensemble mean daily maximum timestep precipitation rate'
            elif variable == 'mx24tp6':
                da.attrs['units']     = 'm'
                da.attrs['long_name'] = 'climatological and ensemble mean daily maximum 6 hour accumulated precipitation'
            elif variable == 'mx24rn6':
                da.attrs['units']     = 'm'
                da.attrs['long_name'] = 'climatological and ensemble mean daily maximum 6 hour accumulated rainfall'

            if write2file: misc.to_netcdf_with_packing_and_compression(da, path_out + filename_out)
            
            misc.toc()

