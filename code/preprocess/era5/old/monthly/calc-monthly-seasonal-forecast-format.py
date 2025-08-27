"""
converts era5 monthly data into seasonal forecast/hindcast format.
"""

import numpy  as np
import xarray as xr
import pandas as pd
from dask.diagnostics   import ProgressBar
from forsikring import config,misc,s2s

# INPUT -----------------------------------------------
variables        = ['tp'] # tp & t2m
data_flag        = 'forecast' # forecast or hindcast
forecast_years   = np.arange(2017,2023,1)
forecast_months  = np.arange(1,13,1)
lead_time_months = np.arange(1,7,1)
comp_lev         = 5
write2file       = True
# -----------------------------------------------------         

for variable in variables:
    for year in forecast_years:

            # define some paths and strings   
            path_in      = config.dirs['era5_monthly'] + variable + '/'
            path_out     = config.dirs['era5_seasonal_' + data_flag + '_monthly'] + variable + '/'
            filename1_in = variable + '_' + str(year) + '.nc'
            filename2_in = variable + '_' + str(int(year)+1) + '.nc'

            for m, month in enumerate(forecast_months):

                print('\nvariable: ' + variable + ', year: ' + str(year) + ', month: ' + str(month))
                
                date  = str(year) + '-' + str(month).zfill(2)
                time  = pd.date_range(date,periods=lead_time_months.size,freq="MS")
                with ProgressBar(): ds = xr.open_mfdataset([path_in + filename1_in,path_in + filename2_in]).sel(time=time)[variable].compute()

                if write2file:
                    filename_out = variable + '_' + date + '.nc' 
                    ds.to_netcdf(path_out + filename_out)
                    s2s.compress_file(comp_lev,3,filename_out,path_out)

                ds.close()

