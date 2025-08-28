"""
Calculates the hindcast calendar month climatology.
Outputs the same climatology in different monthly timestamped
files for ease of use when calculating anomalies (another code).
"""

import numpy  as np
import xarray as xr
import pandas as pd
import os
from forsikring import config,misc,s2s

# INPUT -----------------------------------------------
variables        = ['tp','t2m']                 # tp & t2m  
forecast_years   = np.arange(2017,2023,1)
forecast_months  = np.arange(1,13,1)
lead_time_months = np.arange(1,7,1)
clim_years       = np.arange(1993,2017,1) 
comp_lev         = 5
write2file       = True
# -----------------------------------------------------

for variable in variables:
        
        # define stuff
        path_in  = config.dirs['seasonal_hindcast'] + variable + '/'
        path_out = config.dirs['seasonal_hindcast_monthly_clim'] + variable + '/'
    
        # calculate climatology
        filenames = [path_in + variable + '_' + str(year) + '.nc' for year in clim_years]
        ds_clim   = xr.open_mfdataset(filenames).groupby('time.month').mean(dim='time').mean(dim='number').compute()
        ds_clim   = ds_clim.rename({'month':'time'})

        for year in forecast_years:
                for m, month in enumerate(forecast_months):
                        
                        print('\nvariable: ' + variable + ', year: ' + str(year) + ', month: ' +str(month))

                        ds                            = ds_clim.sel(time=month).squeeze().drop('time')
                        date                          = str(year) + '-' + str(month).zfill(2)
                        ds                            = ds.rename({'lead_time_month':'time'})
                        time                          = pd.date_range(date,periods=lead_time_months.size,freq="MS")
                        ds['time']                    = time
                        ds['time'].attrs['long_name'] = 'months since forecast_reference_time'

                        # fix metadata
                        if variable == 'tp':
                                ds[variable].attrs['long_name'] = 'total accumulated monthly precipitation'
                                ds[variable].attrs['units']     = 'm'
                        elif variable == 't2m':
                                ds[variable].attrs['long_name'] = '2m temperature'
                                ds[variable].attrs['units']     = 'K'
                                
                        if write2file:
                                filename_out = variable + '_' + date + '.nc'
                                ds.to_netcdf(path_out + filename_out)
                                s2s.compress_file(comp_lev,3,filename_out,path_out)

                        ds.close()
        ds_clim.close()


