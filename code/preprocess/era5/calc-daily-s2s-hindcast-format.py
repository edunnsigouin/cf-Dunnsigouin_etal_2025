"""
Converts daily continuous era5 data in yearly files into the same format as ecmwf hindcasts
initialized on mondays and thursdays.
i.e. for each lead time in a hindcast file, we collect the analagous 
era5 dates and put them into a new file.
example: tp24_CY47R1_0.25x0.25_2021-01-04.nc is the hindcast file
and the new era5 file is tp24_0.25x0.25_2021-01-04.nc with dates corresponding
to jan 04 to jan 04 + 15 days.
"""

import numpy  as np
import xarray as xr
import pandas as pd
from dask.diagnostics   import ProgressBar
import os
from Dunnsigouin_etal_2025 import config,misc,s2s


def initialize_hindcast_array(date,number_hdate,variable,dim):
    """
    Initializes hindcast array used below.
    Written here to clean up code.
    """

    # define lead time dim
    if grid == '0.25x0.25': time = pd.date_range(date,periods=15,freq="D")
    elif grid == '0.5x0.5': time = pd.date_range(date,periods=31,freq="D") + np.timedelta64(15,'D')

    # define hindcast initialization dim
    start_date = (date - np.timedelta64(int(number_hdate*365.25),'D')) # need to convert timedelta to days instead of years (pandas doesnt allow 'Y' anymore..)
    hdate      = [(start_date.replace(year=start_date.year + i)).strftime('%Y%m%d') for i in range(0, number_hdate)]
    hdate      = [int(x) for x in hdate]
    
    # create array
    data       = np.zeros((len(hdate),time.size,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims       = ["hdate","time","latitude","longitude"]
    coords     = dict(hdate=hdate,time=time,latitude=dim.latitude,longitude=dim.longitude)

    if variable == 't2m24':
        units       = 'K'
        description = 'daily mean 2-meter temperature'
    elif variable == 'tp24':
        units       = 'm'
        description = 'daily accumulated precipitation'

    attrs      = dict(description=description,units=units)
    name       = variable
    
    return xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)



# INPUT -----------------------------------------------
variables           = ['tp24']             # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
first_forecast_date = '20230102'           # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 104                    # number of forecasts   
number_hdate        = 20
season              = 'annual'
grid                = '0.5x0.5'        # '0.25x0.25' or '0.5x0.5'
write2file          = True
# -----------------------------------------------------         

# get all dates for monday and thursday forecast initializations 
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season)
#forecast_dates = pd.date_range(first_forecast_date, periods=number_forecasts)
print(forecast_dates)

for variable in variables:
    for date in forecast_dates:

        print('\nvariable: ' + variable + ', date: ' + date.strftime('%Y-%m-%d'))

        # define some paths and strings
        path_in      = config.dirs['era5_daily'] + variable + '/'
        path_out     = config.dirs['era5_hindcast_daily'] + variable + '/'
        datestring   = date.strftime('%Y-%m-%d')            
        filename_out = '%s_%s_%s.nc'%(variable,grid,datestring)
        dim          = misc.get_dim(grid,'time')
        hindcast     = initialize_hindcast_array(date,number_hdate,variable,dim)

        # open forecast calendar dates for corresponding hindcasts
        for i in range(0,number_hdate):

            temp_date = date - np.timedelta64(int((i+1)*365.25),'D') # need to convert timedelta to days instead of years 

            # pick out specific dates (46 = # of days in ecmwf forecast)
            if grid == '0.25x0.25': era5_dates = pd.date_range(temp_date,periods=15,freq="D").strftime('%Y-%m-%d')
            elif grid == '0.5x0.5': era5_dates = (pd.date_range(temp_date,periods=31,freq="D") + np.timedelta64(15,'D')).strftime('%Y-%m-%d')

            # define input filenames
            years        = pd.date_range(temp_date,periods=2,freq="Y").strftime('%Y')
            filenames_in = path_in + variable + '_' + grid + '_' + years + '.nc'
            
            # get data corresponding to era5 dates
            with ProgressBar():
                hindcast[i,...] = xr.open_mfdataset(filenames_in).sel(time=era5_dates,method='nearest')[variable].compute().values
            
	# write to file
        if write2file: misc.to_netcdf_with_packing_and_compression(hindcast, path_out + filename_out)

        

