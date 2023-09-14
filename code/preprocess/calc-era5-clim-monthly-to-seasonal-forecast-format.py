"""
converts climatological era5 into seasonal forecast formatted data
"""

import numpy  as np
import xarray as xr
import pandas as pd
from dask.diagnostics   import ProgressBar
from forsikring import config,misc,s2s

# INPUT -----------------------------------------------
variables        = ['t2m','tp']                 # tp & t2m  
forecast_years   = np.arange(2017,2023,1)
forecast_months  = np.arange(1,13,1)
lead_time_months = np.arange(1,7,1)
clim_years       = np.arange(1993,2017,1) 
comp_lev         = 5
write2file       = True
# -----------------------------------------------------

for variable in variables:
        
        # define stuff
        path_in  = config.dirs['era5_monthly'] + variable + '/'
        path_out = config.dirs['era5_seasonal_forecast_monthly_clim'] + variable + '/'
    
        # calculate climatology
        filenames = [path_in + variable + '_' + str(year) + '.nc' for year in clim_years]
        with ProgressBar(): ds_clim = xr.open_mfdataset(filenames).groupby('time.month').mean(dim='time').compute()
        ds_clim = ds_clim.rename({'month':'time'}) 

        for year in forecast_years:
            for m, month in enumerate(forecast_months): 

                print('\nvariable: ' + variable + ', year: ' + str(year), ', month: ' + str(month))
                date       = str(year) + '-' + str(month).zfill(2)
                time       = pd.date_range(date,periods=lead_time_months.size,freq="MS")
                ds         = ds_clim.sel(time=time.month.values,method='nearest')
                ds['time'] = time

                if write2file:
                    filename_out = variable + '_' + date + '.nc'
                    ds.to_netcdf(path_out + filename_out)
                    s2s.compress_file(comp_lev,3,filename_out,path_out)

                ds.close()
        ds_clim.close()

