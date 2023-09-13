"""
Creates persistence forecast files corresponding to the forecast initialization dates.
i.e. for each lead time in a forecast file, we collect the analagous 
era5 dates and put them into a new file, except that the files only have the initialization
date throughout so they can be used as a persistence reference forecast.
example: tp24_CY47R1_0.25x0.25_2021-01-04.nc is the forecast file
and the new era5 file is tp24_0.25x0.25_2021-01-04.nc with dates corresponding
to jan 04.
"""

import numpy  as np
import xarray as xr
import pandas as pd
from dask.diagnostics   import ProgressBar
import os
from forsikring import config,misc,s2s

# INPUT -----------------------------------------------
variables        = ['tp24']                # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
init_start       = '20210104'               # first initialization date of forecast (either a monday or thursday)
init_n           = 104                        # number of forecasts
grids            = ['0.5x0.5']             # '0.25x0.25' or '0.5x0.5'
comp_lev         = 5
write2file       = False
# -----------------------------------------------------         

# get all dates for monday and thursday forecast initializations 
init_dates = s2s.get_init_dates(init_start,init_n)

for variable in variables:
    for date in init_dates:
        for grid in grids:
            
            datestring = date.strftime('%Y-%m-%d')
            year       = date.strftime('%Y')
            print('\nvariable: ' + variable + ', date: ' + datestring)

            # define some paths and strings   
            path_in      = config.dirs['era5_cont_daily'] + variable + '/'
            path_out     = config.dirs['era5_forecast_pers'] + variable + '/'
            filename1_in = variable + '_' + grid + '_' + year + '.nc'
            filename2_in = variable + '_' + grid + '_' + str(int(year)+1) + '.nc'
            filename_out = '%s_%s_%s.nc'%(variable,grid,datestring)

            # read data & pick out specific dates (46 = # of days in ecmwf forecast)
            # NOTE: here dates are just dummy dates. They will be changed below
            if grid == '0.25x0.25':
                era5_dates = pd.date_range(date,periods=15,freq="D")
            elif grid == '0.5x0.5':
                era5_dates = pd.date_range(date,periods=31,freq="D") # not shifted by 15 days!!! 
            ds = xr.open_mfdataset([path_in + filename1_in,path_in + filename2_in]).sel(time=era5_dates)

            # calculate explicitely
            with ProgressBar():
                ds = ds.compute()

            # replace all lags with day 1 value
            ds[variable][:,:,:] = ds[variable][0,:,:]
            
            if write2file:
                print('writing to file..')
                s2s.to_netcdf_pack64bit(ds[variable],path_out + filename_out)
                print('compress file to reduce space..')
                s2s.compress_file(comp_lev,3,filename_out,path_out)
                print('')

            ds.close()
