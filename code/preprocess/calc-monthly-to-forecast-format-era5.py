"""
Converts monthly era5 data in yearly files into the same format as ecmwf 
seasonal forecasts for use as a forecast verification dataset.
i.e. for each lead time in a forecast file, we collect the analagous 
era5 dates and put them into a new file.
example: t2m_2021.nc is the forecast file and the new era5 file is 
t2m_2021.nc with the corresponding 12 initialization months and the 
6 lead time months.
"""

import numpy  as np
import xarray as xr
import pandas as pd
from dask.diagnostics   import ProgressBar
import os
from forsikring import config,misc,s2s


def init_forecast_format_array(dim,forecastMonth,year,months,variable):
    """  
    Initializes forecast format array used below.
    Written here to clean up code.
    """
    
    init_date = str(year) + '-' + str(months[0]).zfill(2)
    time      = pd.date_range(init_date,periods=months.size,freq="MS")
    data      = np.zeros((forecastMonth.size,time.size,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims      = ["forecastMonth","time","latitude","longitude"]
    coords    = dict(forecastMonth=forecastMonth,time=time,latitude=dim.latitude,longitude=dim.longitude)
    name      = variable

    if variable == 'tp': attrs = dict(long_name='total accumulated monthly precipitation',units='m')
    elif variable == 't2m': attrs = dict(long_name='2m temperature',units='K')

    forecast_format = xr.DataArray(data=data,dims=dims,coords=coords,name=name,attrs=attrs)

    forecast_format['time'].attrs['long_name']          = "initial time of forecast"
    forecast_format['forecastMonth'].attrs['long_name'] = "months since forecast_reference_time" 

    return forecast_format


# INPUT -----------------------------------------------
variables        = ['tp','t2m']                 # tp & t2m
years            = np.arange(2017,2023,1)
months           = np.arange(1,13,1)
forecastMonth    = np.arange(1,7,1)
comp_lev         = 5
write2file       = True
# -----------------------------------------------------         

dim = s2s.get_dim('1.0x1.0','time')

for variable in variables:
    for year in years:

            print('\nvariable: ' + variable + ', year: ' + str(year))

            # define some paths and strings   
            path_in      = config.dirs['era5_monthly'] + variable + '/'
            path_out     = config.dirs['era5_forecast_monthly'] + variable + '/'
            filename1_in = variable + '_' + str(year) + '.nc'
            filename2_in = variable + '_' + str(int(year)+1) + '.nc'
            filename_out = variable + '_' + str(year) + '.nc'

            # initialize output array per year
            forecast_format = init_forecast_format_array(dim,forecastMonth,year,months,variable)

            for m, month in enumerate(months):
                # read data & pick out specific dates
                init_date      = str(year) + '-' + str(month).zfill(2)
                leadtime_dates = pd.date_range(init_date,periods=forecastMonth.size,freq="MS")
                ds             = xr.open_mfdataset([path_in + filename1_in,path_in + filename2_in]).sel(time=leadtime_dates)

                # calculate explicitely
                with ProgressBar(): ds = ds.compute()
                
                # dump into yearly array
                forecast_format[:,m,:,:] = ds[variable].values 

                ds.close()
                
            if write2file:
                print('writing to file..')
                s2s.to_netcdf_pack64bit(forecast_format,path_out + filename_out)
                print('compress file to reduce space..')
                s2s.compress_file(comp_lev,3,filename_out,path_out)
                print('')

            forecast_format.close()

