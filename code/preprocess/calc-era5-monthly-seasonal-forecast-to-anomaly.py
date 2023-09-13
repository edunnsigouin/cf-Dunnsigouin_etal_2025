"""
converts era5 data in monthly seasonal forecast format into 
anomalies relative to climatology.
"""

import numpy  as np
import xarray as xr
import pandas as pd
from dask.diagnostics   import ProgressBar
import os
from forsikring import config,misc,s2s


def init_forecast_format_array(dim,lead_time_months,year,forecast_months,variable):
    """
    Initializes forecast format array used below.
    Written here to clean up code. 
    """
    init_date = str(year) + '-' + str(forecast_months[0]).zfill(2)
    time      = pd.date_range(init_date,periods=forecast_months.size,freq="MS")
    data      = np.zeros((lead_time_months.size,time.size,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims      = ["lead_time_month","time","latitude","longitude"]
    coords    = dict(lead_time_month=lead_time_months,time=time,latitude=dim.latitude,longitude=dim.longitude)
    name      = variable

    if variable == 'tp': attrs = dict(long_name='anomalies of total accumulated monthly precipitation',units='m')
    elif variable == 't2m': attrs = dict(long_name='anomalies of 2m temperature',units='K')

    forecast_format = xr.DataArray(data=data,dims=dims,coords=coords,name=name,attrs=attrs)

    forecast_format['time'].attrs['long_name']            = "initial time of forecast"
    forecast_format['lead_time_month'].attrs['long_name'] = "months since forecast_reference_time"

    return forecast_format


# INPUT -----------------------------------------------
variables        = ['tp','t2m']                 # tp & t2m
forecast_years   = np.arange(2017,2023,1)
forecast_months  = np.arange(1,13,1)
lead_time_months = np.arange(1,7,1)
comp_lev         = 5
write2file       = True
# -----------------------------------------------------         

dim = s2s.get_dim('1.0x1.0','time')

for variable in variables:
    for year in forecast_years:

            print('\nvariable: ' + variable + ', year: ' + str(year))

            # define some paths and strings   
            path_in_clim     = config.dirs['era5_seasonal_forecast_monthly_clim'] + variable + '/'
            path_in_forecast = config.dirs['era5_seasonal_forecast_monthly'] + variable + '/'
            path_out         = config.dirs['era5_seasonal_forecast_monthly_anomaly'] + variable + '/'
            
            filename_in_clim     = variable + '_' + str(year) + '.nc'
            filename_in_forecast = variable + '_' + str(year) + '.nc'
            filename_out         = variable + '_' + str(year) + '.nc'

            # initialize output array per year
            anomaly = init_forecast_format_array(dim,lead_time_months,year,forecast_months,variable)

            ds_clim     = xr.open_dataset(path_in_clim + filename_in_clim)
            ds_forecast = xr.open_dataset(path_in_forecast + filename_in_forecast)
                    
            # dump into yearly array
            anomaly[:,:,:,:] = ds_forecast[variable].values - ds_clim[variable].values

            ds_clim.close()
            ds_forecast.close()
            
            if write2file:
                print('writing to file..')
                s2s.to_netcdf_pack64bit(anomaly,path_out + filename_out)
                print('compress file to reduce space..')
                s2s.compress_file(comp_lev,3,filename_out,path_out)
                print('')

            anomaly.close()

