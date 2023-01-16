"""
Downloads era5 6hourly data at 0.25x0.25 resolution over europe
Europe defined following ecmwf. 
"""

import numpy  as np
import xarray as xr
from dask.diagnostics import ProgressBar
import cdsapi
import pandas as pd
import os
from forsikring import config,s2s

# INPUT -----------------------------------------------
area       = '73.5/-27/33/45' # or 'E' for europe
grid       = '0.5/0.5' # '0.25/0.25' or '0.5/0.5'
variables  = ['tp6'] # tp6,sf6,mx6tpr
years      = np.arange(1960,2023,1)
months     = np.arange(1,13,1)
comp_lev   = 5 # file compression level
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
    
    if grid == '0.25/0.25':
        path       = config.dirs['era5_6hourly'] + variable + '/'
        gridstring = '0.25x0.25'
    elif grid == '0.5/0.5':
        path       = config.dirs['era5_6hourly'] + variable + '/'
        gridstring = '0.5x0.5'
        
    for year in years:
        for month in months:
            days      = pd.Period(str(year) + '-' + str(month)).days_in_month
            for day in np.arange(1,days+1):

                if variable == 'mx6tpr':
                    # api doesn't recognize short variable name..
                    specs['variable'] = 'maximum_total_precipitation_rate_since_previous_post_processing'
                elif variable == 'tp6':
                    specs['variable'] = 'tp'
                elif variable == 'sf6':
                    specs['variable'] =	'sf'
                    
                specs['year']     = str(year)
                specs['month']    = str(month)
                specs['day']      = str(day)
                filename          = variable + '_' + gridstring + '_' + str(year) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) + '.nc'

                if write2file:
                    print('')
                    print('downloading: ' + filename)
                    print('')
                    c.retrieve(data_type,specs,path + filename)

                    print('aggregate from hourly to 6 hourly..')
                    ds = xr.open_dataset(path + filename)

                    with xr.set_options(keep_attrs=True):
                        if variable == 'tp6':
                            ds                              = ds.resample(time='6H').sum('time') # accumulated
                            ds                              = ds.rename({'tp':variable})
                            ds[variable].attrs['long_name'] = '6-hourly accumulated precipitation'
                        elif variable == 'sf6':
                            ds                              = ds.resample(time='6H').sum('time') # accumulated
                            ds                              = ds.rename({'sf':variable})
                            ds[variable].attrs['long_name'] = '6-hourly accumulated snowfall'
                        elif (variable == 'mx6tpr'):
                            ds                              = ds.resample(time='6H').max('time')
                            ds                              = ds.rename({'maximum_total_precipitation_rate_since_previous_post_processing':variable})
                            ds[variable].attrs['long_name'] = '6-hourly maximum precipitation rate'
                            
                    ds.to_netcdf(path + filename)
                    ds.close()

        print('')
        print('')
        print('')
        print('')            
        print('aggregate to yearly files & delete daily files..')
        filenames    = variable + '_' + gridstring + '_' + str(year) + '-*'
        filename_out = variable + '_' + gridstring + '_' + str(year) + '.nc'
        ds           = xr.open_mfdataset(path + filenames)
        with ProgressBar():
            ds = ds.compute()
        ds.to_netcdf(path + filename_out)
        ds.close()
        os.system('rm ' + path + filenames)

        print('compress files to reduce space..')
        s2s.compress_file(comp_lev,3,filename_out,path)

