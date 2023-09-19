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

                # units of tp in era5 monthly are total accumulated precip per day
                # so here I multiply by days_in_month to get monthly accumulated values. 
                if variable == 'tp':
                    ds   = xr.open_dataset(path + filename)[variable]
                    temp = np.zeros(ds.shape)
                    for m in range(ds.shape[0]):
                        temp[m,:,:] = days_in_month(year, m+1)
                    ds = ds*temp
                    ds.to_netcdf(path + filename)
                    ds.close()

                # compress netcdf
                s2s.compress_file(comp_lev,3,filename,path)     
            
                
