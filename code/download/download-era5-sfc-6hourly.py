"""
Downloads era5 6hourly data over europe and agregates to yearly files.
Since many of the quantities i'm interested in are accumulated,
I need to download two consecutive days at a time to get the correct
accumulations on a given day. For example, hourly data in one day has hours
0 to 23, where hour 0 is data accumulated from the last hour of the previous day. 
So to get 6 hourly accumulated data, I need to sum hours 1-6, 7-12, 13-18, 19-24 
where hour 24 is from the first our of the next day. 
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
grid       = '0.25/0.25' # '0.25/0.25' or '0.5/0.5'
variables  = ['sf6','mx6tpr'] # tp6,sf6,mx6tpr
date_start = '2022-01-01'
date_end   = '2022-10-01'
comp_lev   = 5 # file compression level
write2file = True
# -----------------------------------------------------

c         = cdsapi.Client()
data_type = 'reanalysis-era5-single-levels'

dic1 = {
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

# create list of daily dates to download
dates = pd.date_range(start=date_start,end=date_end, freq="1D")

for variable in variables:
    
        if grid == '0.25/0.25': 
            path       = config.dirs['era5_6hourly'] + variable + '/'
            gridstring = '0.25x0.25'
        elif grid == '0.5/0.5':                                                                                                                                       
            path       = config.dirs['era5_6hourly'] + variable + '/'
            gridstring = '0.5x0.5'

        if variable == 'mx6tpr':
            # api doesn't recognize short variable name..                                                                                                          
            dic1['variable'] = 'maximum_total_precipitation_rate_since_previous_post_processing'
        elif variable == 'tp6':
            dic1['variable'] = 'tp'
        elif variable == 'sf6':
            dic1['variable'] = 'sf'

        # download files    
        for i in range(0,dates.size-1):

            dic1['year']  = str(dates[i].year)
            dic1['month'] = str(dates[i].month)
            dic1['day']   = str(dates[i].day)
            date1         = str(dates[i].year) + '-' + str(dates[i].month).zfill(2) + '-' + str(dates[i].day).zfill(2)
            filename1     = 'temp_' + variable + '_' + gridstring + '_' + date1 + '.nc'            

            dic2          = dic1.copy()
            dic2['year']  = str(dates[i+1].year)
            dic2['month'] = str(dates[i+1].month)
            dic2['day']   = str(dates[i+1].day)
            date2         = str(dates[i+1].year) + '-' + str(dates[i+1].month).zfill(2) + '-' + str(dates[i+1].day).zfill(2)
            filename2     = 'temp_' + variable + '_' + gridstring + '_' + date2 + '.nc'

            filename3     = variable + '_' + gridstring + '_' + date1 + '.nc'

            if write2file:
                    
                print('')
                print('downloading file: ' + date1)
                print('')

                c.retrieve(data_type,dic1,path + filename1)
                c.retrieve(data_type,dic2,path + filename2)

                ds         = xr.open_mfdataset([path + filename1,path + filename2])
                ds['time'] = ds.time - np.timedelta64(1,'h') # shift time to put all required data on same day

                if variable == 'tp6':                
                        ds                              = ds.resample(time='6h').sum('time')
                        ds                              = ds.isel(time=slice(1,5))
                        ds                              = ds.rename({'tp':variable})
                        ds[variable].attrs['long_name'] = '6-hourly accumulated precipitation'
                        ds[variable].attrs['units']     = 'm'
                elif variable == 'sf6':
                        ds                              = ds.resample(time='6h').sum('time')
                        ds                              = ds.isel(time=slice(1,5))
                        ds                              = ds.rename({'sf':variable})
                        ds[variable].attrs['long_name'] = '6-hourly accumulated snowfall'
                        ds[variable].attrs['units']     = 'm'
                elif variable == 'mx6tpr':
                        ds                              = ds.resample(time='6h').max('time')
                        ds                              = ds.isel(time=slice(1,5))
                        ds                              = ds.rename({'mxtpr':variable})  
                        ds[variable].attrs['long_name'] = '6-hourly maximum precipitation rate'                
                        ds[variable].attrs['units']     = 'kg m**-2 s**-1'
                        
                ds.to_netcdf(path + filename3)
                os.system('rm ' + path + filename1 + ' ' + path + filename2)
                ds.close()
                
                if (dates[i+1].year - dates[i].year == 1) or (dates[i+1].strftime('%Y-%m-%d') == date_end): # if new year or end of dates

                        print('')
                        print('aggregate daily files to yearly file & delete daily files..')
                        year         = str(dates[i].year)
                        filenames    = variable + '_' + gridstring + '_' + str(year) + '-*'
                        filename_out = variable + '_' + gridstring + '_' + str(year) + '.nc'
                        ds           = xr.open_mfdataset(path + filenames)
                        with ProgressBar():
                                ds = ds.compute()
                        ds.to_netcdf(path + filename_out)
                        ds.close()
                        os.system('rm ' + path + filenames)

                        print('compress files to reduce space..')
                        print('')
                        s2s.compress_file(comp_lev,3,filename_out,path)



