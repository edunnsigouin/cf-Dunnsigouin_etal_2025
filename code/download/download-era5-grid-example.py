"""
Downloads example grid data from era5 over europe 
so that Sondre from NHH can bin insurance data onto 
the same grid
"""

import numpy  as np
import xarray as xr
import cdsapi
from forsikring import config

path      = config.dirs['nhh']
filename  = 'era5-example-grid-for-sondre-2022-01-01.nc'
data_type = 'reanalysis-era5-single-levels'

specs = {
    'product_type': 'reanalysis',
    'format': 'netcdf',
    'variable': 'total_precipitation',
    'year': '2022',
    'month': '01',
    'day': '01',
    'time': '00:00/01:00/02:00/03:00/04:00/05:00/06:00/07:00/08:00/09:00/10:00/11:00/12:00/13:00/14:00/15:00/16:00/17:00/18:00/19:00/20:00/21:00/22:00/23:00',
    'area': '73.5/-27/33/45',
}

c = cdsapi.Client()
c.retrieve(data_type,specs,path + filename)

