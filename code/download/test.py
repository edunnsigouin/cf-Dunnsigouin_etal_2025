"""
Downloads era5 monthly mean data from copernicus
"""

import numpy  as np
import xarray as xr
import cdsapi
from forsikring import config,s2s,misc
import calendar

def days_in_month(year, month):
    """
    Return the number of days in the specified month of the given year.
    """
    return calendar.monthrange(year, month)[1]


# INPUT -----------------------------------------------
area            = '74/-27/33/45' # or 'E' for europe
variables       = ['tp'] # 'tp' and 't2m'
years           = np.arange(1960,1961,1)
months          = np.arange(1,13,1)
grid            = '1.0/1.0'
comp_lev        = 5 # file compression level
write2file      = True
# -----------------------------------------------------

# loop through variables and create one file for each year       
for variable in variables:
    for year in years:

        # define stuff
        filename = variable + '_' + str(year) + '-old.nc'
        path     = config.dirs['era5_monthly'] + variable + '/'

        if write2file:    
            print('')
            print('downloading file: ' + filename)
            print('')

            ds = xr.open_dataset(path + filename)
            print(ds[variable][0,10,10].values)
            ds[variable] = ds[variable]*100 
            print(ds[variable][0,10,10].values)
            ds.to_netcdf(path + 'test.nc')
            ds.close()

            print('test!')
            ds2 = xr.open_dataset(path + 'test.nc')
            print(ds2[variable][0,10,10].values)
            ds2.close()    
                
            
                
