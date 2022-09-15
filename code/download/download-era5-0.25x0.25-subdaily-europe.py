"""
Downloads era5 subdaily at 0.25x0.25 resolution over europe
Europe defined following ecmwf 
"""

import numpy  as np
import xarray as xr
import cdsapi
import pandas as pd
from forsikring import config

# INPUT -----------------------------------------------
area       = '73.5/-27/33/45'
variables  = ['total_precipitation']
years      = np.array([2021])
months     = np.arange(1,13,1)
write2file = True
# -----------------------------------------------------

c         = cdsapi.Client()
data_type = 'reanalysis-era5-single-levels'

specs = {
    'product_type': 'reanalysis',
    'format': 'netcdf',
    'variable': '',
    'year': '',
    'month': '',
    'day': '',
    'time': '00:00/01:00/02:00/03:00/04:00/05:00/06:00/07:00/08:00/09:00/10:00/11:00/12:00/13:00/14:00/15:00/16:00/17:00/18:00/19:00/20:00/21:00/22:00/23:00',
    'area': area,
}

for variable in variables:
    for year in years:
        for month in months:
            days      = pd.Period(str(year) + '-' + str(month)).days_in_month
            for day in np.arange(1,days+1):

                specs['variable'] = variable
                specs['year']     = str(year)
                specs['month']    = str(month)
                specs['day']      = str(day)
                
                if write2file:
                    path     = config.dirs['era5'] + variable + '/'
                    filename = variable + '_' + str(year) + str(month).zfill(2) + str(day).zfill(2)
                    print('')
                    print('downloading: ' + filename)
                    print('')
                    c.retrieve(data_type,specs,path + filename)

