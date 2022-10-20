"""
Downloads era5 subdaily at 0.25x0.25 resolution over europe
Europe defined following ecmwf. 
Some interesting variables are:
- total precipitation
- snowfall
- maximum total precipitation rate since last post-processing
- mean snowfall rate
- mean total precipitation rate
- convective and large scale snowfall rate (instantaneous)
- convective and large scale rain rate (instantaneous) 
- runoff (surface & sub-surface)
- soil moisture 

"""

import numpy  as np
import xarray as xr
import cdsapi
import pandas as pd
import os
from forsikring import config

# INPUT -----------------------------------------------
area       = '73.5/-27/33/45' # or 'E' for europe
grid       = '0.25/0.25'
variables  = ['maximum_total_precipitation_rate_since_previous_post_processing']
years      = np.arange(2000,2022,1)
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
    'grid': grid,
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
                path              = config.dirs['era5'] + variable + '/'
                filename          = variable + '_' + str(year) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) + '.nc'

                if write2file:
                    print('')
                    print('downloading: ' + filename)
                    print('')
                    c.retrieve(data_type,specs,path + filename)

                    # aggregate from hourly to daily
                    da = xr.open_dataarray(path + filename)
                    
                    with xr.set_options(keep_attrs=True):
                        if variable == 'total_precipitation':
                            da = da.resample(time='1D').sum('time') # accumulated
                        elif variable == 'snowfall':
                            da = da.resample(time='1D').sum('time') # accumulated
                        elif variable == 'surface_runoff':
                            da = da.resample(time='1D').max('time') # accumulated
                        elif (variable == 'maximum_total_precipitation_rate_since_previous_post_processing'):
                            da = da.resample(time='1D').max('time')
                        elif variable == 'convective_rain_rate': # instantaneous
                            da = da.resample(time='1D').max('time')
                        elif variable == 'large_scale_rain_rate': # instantaneous
                            da = da.resample(time='1D').max('time')
                        elif variable == 'mean_total_precipitation_rate': # could calc max here maybe?
                            da = da.resample(time='1D').mean('time')
                        elif variable == 'mean_snowfall_rate': 
                            da = da.resample(time='1D').mean('time')
                        
                    da.to_netcdf(path + filename)
                    da.close()

        # aggregate to yearly files & delete daily files
        with xr.set_options(keep_attrs=True):
            filenames    = variable + '_' + str(year) + '-*'
            filename_out = variable + '_' + str(year) + '.nc'
            da           = xr.open_mfdataset(path + filenames)
            da.to_netcdf(path + filename_out)
            da.close()
            os.system('rm ' + path + filenames)

