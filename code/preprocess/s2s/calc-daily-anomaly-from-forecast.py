"""
Converts ecmwf forecast data into anomalies relative to 
corresponding hindcast climatology.
"""

import numpy    as np
import xarray   as xr
import os
from forsikring import misc,s2s,config

# INPUT -----------------------------------------------
variables           = ['tp24']                  # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
first_forecast_date = '20200102'               # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 313                      # number of forecasts 
grids               = ['0.25x0.25']            # '0.25x0.25' & '0.5x0.5'
comp_lev            = 5                        # compression level (0-10) of netcdf putput file
write2file          = True
# -----------------------------------------------------

misc.tic()

# define stuff  
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts).strftime('%Y-%m-%d').values
print(forecast_dates)

for variable in variables:
    for grid in grids:
        for date in forecast_dates:

            print('\nconverting forecast to anomaly for ' + grid + ' and initialization ' + date)
        
            # define stuff
            dim               = misc.get_dim(grid,'time')
            path_in_forecast  = config.dirs['s2s_forecast_daily'] + variable + '/'
            path_in_clim      = config.dirs['s2s_hindcast_daily_clim'] + variable + '/'
            path_out          = config.dirs['s2s_forecast_daily_anomaly'] + variable + '/'
            filename_forecast = variable + '_' + grid + '_' + date + '.nc'
            filename_clim     = variable + '_' + grid + '_' + date + '.nc'
            filename_out      = variable + '_' + grid + '_' + date + '.nc'
        
            # read data
            da_forecast = xr.open_dataset(path_in_forecast + filename_forecast)[variable].mean(dim='number') # ensemble mean
            da_clim     = xr.open_dataset(path_in_clim + filename_clim)[variable]

	    # calculate anomalies from climatology
            da_anomaly = da_forecast - da_clim

            # modify metadata
            if variable == 'tp24':
                da_anomaly.attrs['units']     = 'm'
                da_anomaly.attrs['long_name'] = 'anomalies of daily accumulated precipitation'
            if variable == 'rn24':
                da_anomaly.attrs['units']     = 'm'
                da_anomaly.attrs['long_name'] = 'anomalies of daily accumulated rainfall'
            if variable == 'mx24tpr':
                da_anomaly.attrs['units']     = 'kg m**-2 s**-1'
                da_anomaly.attrs['long_name'] = 'anomalies of daily maximum timestep precipitation rate'
            if variable == 'mx24tp6':
                da_anomaly.attrs['units']     = 'm'
                da_anomaly.attrs['long_name'] = 'anomalies of daily maximum 6 hour accumulated precipitation'
            if variable == 'mx24rn6':
                da_anomaly.attrs['units']     = 'm'
                da_anomaly.attrs['long_name'] = 'anomalies of daily maximum 6 hour accumulated rainfall'

            # write output     
            if write2file:
                da_anomaly.to_netcdf(path_out + filename_out)
                misc.compress_file(comp_lev,3,filename_out,path_out) 
                
            da_forecast.close()
            da_clim.close()

misc.toc()


