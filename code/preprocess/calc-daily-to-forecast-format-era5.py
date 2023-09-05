"""
Converts era5 yearly files into the same format as ecmwf forecasts
initialized on mondays and thursdays for use as a forecast verification dataset.
i.e. for each lead time in a forecast file, we collect the analagous 
era5 dates and put them into a new file.
example: tp24_CY47R1_0.25x0.25_2021-01-04.nc is the forecast file
and the new era5 file is tp24_0.25x0.25_2021-01-04.nc with dates corresponding
to jan 04 to jan 04 + 46 days.
"""

import numpy  as np
import xarray as xr
import pandas as pd
from dask.diagnostics   import ProgressBar
import os
from forsikring import config,misc,s2s

# INPUT -----------------------------------------------
variables        = ['mx24tp6']             # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
init_start       = '20220103'              # first initialization date of forecast (either a monday or thursday)
init_n           = 104                    # number of forecasts   
grids            = ['0.25x0.25']           # '0.25x0.25' or '0.5x0.5'
comp_lev         = 5
write2file       = True
# -----------------------------------------------------         

# get all dates for monday and thursday forecast initializations 
init_dates = s2s.get_init_dates(init_start,init_n)
print(init_dates)

for variable in variables:
    for date in init_dates:
        for grid in grids:
            
            datestring = date.strftime('%Y-%m-%d')
            year       = date.strftime('%Y')
            print('\nvariable: ' + variable + ', date: ' + datestring)

            # define some paths and strings   
            path_in      = config.dirs['era5_cont_daily'] + variable + '/'
            path_out     = config.dirs['era5_forecast_daily'] + variable + '/'
            filename1_in = variable + '_' + grid + '_' + year + '.nc'
            filename2_in = variable + '_' + grid + '_' + str(int(year)+1) + '.nc'
            filename_out = '%s_%s_%s.nc'%(variable,grid,datestring)

            # read data & pick out specific dates (46 = # of days in ecmwf forecast)
            if grid == '0.25x0.25':
                era5_dates = pd.date_range(date,periods=15,freq="D")
            elif grid == '0.5x0.5':
                era5_dates = pd.date_range(date,periods=31,freq="D") + np.timedelta64(15,'D')
            ds = xr.open_mfdataset([path_in + filename1_in,path_in + filename2_in]).sel(time=era5_dates)

            # calculate explicitely
            with ProgressBar():
                ds = ds.compute()

            if write2file:
                print('writing to file..')
                s2s.to_netcdf_pack64bit(ds[variable],path_out + filename_out)
                print('compress file to reduce space..')
                s2s.compress_file(comp_lev,3,filename_out,path_out)
                print('')

            ds.close()

