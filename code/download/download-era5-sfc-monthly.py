"""
Downloads era5 monthly mean data from copernicus
"""

import numpy  as np
import xarray as xr
import cdsapi
from forsikring import config,s2s,misc

# INPUT -----------------------------------------------
area            = '74/-27/33/45' # or 'E' for europe
variables       = ['tp','t2m'] # 'tp' and 't2m'
years           = np.arange(2023,2024,1)
months          = np.arange(1,13,1)
grid            = '1.0/1.0'
comp_lev        = 5 # file compression level
write2file      = True
# -----------------------------------------------------

# loop through variables and create one file for each year       
for variable in variables:
    for year in years:

        # define stuff
        filename = variable + '_' + str(year) + '.nc'
        path     = config.dirs['era5_monthly'] + variable + '/'

        # populate dictionary
        months_string = [str(month) for month in months]
        dic = {
                'format':'netcdf',
                'product_type':'monthly_averaged_reanalysis',
                'year':[str(year)],
                'month':months_string,
                'time':'00:00',
                'area':area,
                'grid':grid,
        }
        if variable == 'tp': dic['variable'] = 'total_precipitation'
        if variable == 't2m': dic['variable'] = '2m_temperature'

        if write2file:    
                print('')
                print('downloading file: ' + filename)
                print('')

                # download
                c = cdsapi.Client()
                c.retrieve('reanalysis-era5-single-levels-monthly-means', dic, path + filename)

                # compress netcdf
                s2s.compress_file(comp_lev,3,filename,path)     
            
                
