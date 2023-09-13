"""

"""

import numpy  as np
import xarray as xr
import pandas as pd
import os
from forsikring import config,misc,s2s

# INPUT -----------------------------------------------
variables        = ['tp','t2m']                 # tp & t2m  
forecast_years   = np.arange(2017,2023,1)
clim_years       = np.arange(1993,2017,1) 
comp_lev         = 5
write2file       = True
# -----------------------------------------------------

for variable in variables:
        
        # define stuff
        path_in  = config.dirs['seasonal_hindcast_monthly'] + variable + '/'
        path_out = config.dirs['seasonal_hindcast_monthly_clim'] + variable + '/'
    
        # calculate climatology
        filenames = [path_in + variable + '_' + str(year) + '.nc' for year in clim_years]
        ds_clim = xr.open_mfdataset(filenames).groupby('time.month').mean(dim='time').mean(dim='number').compute()
        ds_clim = ds_clim.rename({'month':'time'})

        for year in forecast_years:

            print('\nvariable: ' + variable + ', year: ' + str(year))
            
            temp_date       = str(year) + '-' + str(1).zfill(2)
            dates           = pd.date_range(temp_date,periods=12,freq="MS")
            ds_clim['time'] = dates

            print(ds_clim)
            if write2file:
                print('writing to file..')
                filename_out = variable + '_' + str(year) + '.nc'
                #s2s.to_netcdf_pack64bit(ds_clim,path_out + filename_out)
                ds_clim.to_netcdf(path_out + filename_out)
                print('compress file to reduce space..')
                s2s.compress_file(comp_lev,3,filename_out,path_out)
                print('')

        ds_clim.close()

