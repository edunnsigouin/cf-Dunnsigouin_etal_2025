"""
Converts monthly seasonal forecast data into anomalies relative 
to climatology derived from corresponding hindcasts.
"""

import numpy  as np
import xarray as xr
from forsikring import config,misc,s2s

# INPUT -----------------------------------------------
variables        = ['tp','t2m'] # tp & t2m
forecast_years   = np.arange(2017,2023,1)
forecast_months  = np.arange(1,13,1)
lead_time_months = np.arange(1,7,1)
comp_lev         = 5
write2file       = True
# -----------------------------------------------------         

for variable in variables:
    for year in forecast_years:
        for m, month in enumerate(forecast_months):

            print('\nvariable: ' + variable + ', year: ' + str(year) + ', month: ' + str(month))

            # define some paths and strings   
            path_in_clim     = config.dirs['seasonal_hindcast_monthly_clim'] + variable + '/'
            path_in_forecast = config.dirs['seasonal_forecast_monthly'] + variable + '/'
            path_out         = config.dirs['seasonal_forecast_monthly_anomaly'] + variable + '/'

            date                 = str(year) + '-' + str(month).zfill(2)
            filename_in_clim     = variable + '_' + date + '.nc'
            filename_in_forecast = variable + '_' + date + '.nc'
            filename_out         = variable + '_' + date + '.nc'

            # read in clim and forecast data
            ds_clim     = xr.open_dataset(path_in_clim + filename_in_clim)[variable]
            ds_forecast = xr.open_dataset(path_in_forecast + filename_in_forecast)[variable] # ensemble mean

            # initialize anomaly array with correct metadata
            ds_anomaly  = ds_forecast.copy()
            if variable == 'tp':
                ds_anomaly.attrs['long_name'] = 'anomalies of total accumulated monthly precipitation'
                ds_anomaly.attrs['units']     = 'm'
            elif variable == 't2m':
                ds_anomaly.attrs['long_name'] = 'anomalies of 2m temperature'
                ds_anomaly.attrs['units']     = 'K'

            # dump into yearly array
            ds_anomaly[:,:,:] = ds_forecast.values - ds_clim.values

            ds_clim.close()
            ds_forecast.close()
            
            if write2file:
                s2s.to_netcdf_pack64bit(ds_anomaly,path_out + filename_out)
                s2s.compress_file(comp_lev,3,filename_out,path_out)

            ds_anomaly.close()

