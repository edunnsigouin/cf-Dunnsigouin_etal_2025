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

# INPUT -----------------------------------------------
variables        = ['tp']                 # tp & t2m
years            = np.arange(2017,2018,1)
months           = np.arange(12,13,1)
leadtime_months  = np.arange(1,7,1)
comp_lev         = 5
write2file       = False
# -----------------------------------------------------         

dim = get_dim('1.0x1.0','time')

for variable in variables:
    for year in years:

            print('\nvariable: ' + variable + ', year: ' + str(year))

            # define some paths and strings   
            path_in      = config.dirs['era5_monthly'] + variable + '/'
            #path_out     = config.dirs['era5_forecast_monthly'] + variable + '/'
            filename1_in = variable + '_' + str(year) + '.nc'
            filename2_in = variable + '_' + str(int(year)+1) + '.nc'
            filename_out = variable + '_' + str(year) + '.nc'

            # initialize output array per year
            output = np.zeros((leadtime.size,12,dim.nlat,dim.nlon))
            
            for m, month in enumerate(months):
                # read data & pick out specific dates
                init_date      = str(year) + '-' + str(month).zfill(2)
                leadtime_dates = pd.date_range(init_date,periods=leadtime_months.size,freq="MS")
                ds             = xr.open_mfdataset([path_in + filename1_in,path_in + filename2_in]).sel(time=leadtime_dates)

                # calculate explicitely
                with ProgressBar():
                    ds = ds.compute()
                    
                # dump into yearly array
                output[:,m,:,:] = ds[variable].values 
                    
"""                    
            if write2file:
                print('writing to file..')
                s2s.to_netcdf_pack64bit(ds[variable],path_out + filename_out)
                print('compress file to reduce space..')
                s2s.compress_file(comp_lev,3,filename_out,path_out)
                print('')

            ds.close()
"""
