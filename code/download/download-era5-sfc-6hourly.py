"""
Downloads era5 6hourly data and agregates to yearly files.
"""

import numpy  as np
import xarray as xr
from dask.diagnostics import ProgressBar
import cdsapi
import pandas as pd
import os
from forsikring import config,s2s,misc

# INPUT -----------------------------------------------
area       = '73.5/-27/33/45' # or 'E' for europe
grid       = '0.25/0.25' # '0.25/0.25' or '0.5/0.5'
variables  = ['tp6'] # mwd6, swh6, hmax6
date_start = '2023-01-01'
date_end   = '2024-01-01'#'2023-01-01'
comp_lev   = 5 # file compression level
write2file = False
# -----------------------------------------------------

c         = cdsapi.Client()
data_type = 'reanalysis-era5-single-levels'

dic = {
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
            dic['variable'] = 'maximum_total_precipitation_rate_since_previous_post_processing'
        elif variable == 'swh6':
            dic['variable'] = 'significant_height_of_combined_wind_waves_and_swell'    
        elif variable == 'mwd6':
            dic['variable'] = 'mean_wave_direction'
        elif variable == 'hmax6':
            dic['variable'] = 'maximum_individual_wave_height'
        elif variable == 'bfi6':
            dic['variable'] = 'benjamin_feir_index'            
        elif variable == 'u10m6':
            dic['variable'] = '10m_u_component_of_wind'
        elif variable == 'v10m6':
            dic['variable'] = '10m_v_component_of_wind'
        elif variable == 't2m6':
            dic['variable'] = '2m_temperature'
            
        # download files    
        for i in range(0,dates.size-1):

            dic['year']  = str(dates[i].year)
            dic['month'] = str(dates[i].month)
            dic['day']   = str(dates[i].day)
            date         = str(dates[i].year) + '-' + str(dates[i].month).zfill(2) + '-' + str(dates[i].day).zfill(2)
            filename     = variable + '_' + gridstring + '_' + date + '.nc'            

            if write2file:
                    
                print('')
                print('downloading file: ' + date)
                print('')

                c.retrieve(data_type,dic,path + filename)
                ds = xr.open_dataset(path + filename)

                if variable == 'mx6tpr':
                        ds                              = ds.resample(time='6h').max('time')
                        ds                              = ds.rename({'mxtpr':variable})  
                        ds[variable].attrs['long_name'] = '6-hourly maximum precipitation rate'                
                        ds[variable].attrs['units']     = 'kg m**-2 s**-1'
                elif variable == 'swh6':
                        ds                              = ds.resample(time='6h').mean('time')
                        ds                              = ds.rename({'swh':variable})
                        ds[variable].attrs['long_name'] = '6-hourly mean significant height of combined wind waves and swell'
                        ds[variable].attrs['units']     = 'm'                        
                elif variable == 'mwd6':
                        ds                              = ds.resample(time='6h').mean('time')
                        ds                              = ds.rename({'mwd':variable})
                        ds[variable].attrs['long_name'] = '6-hourly mean mean wave direction'
                        ds[variable].attrs['units']     = 'degrees'
                elif variable == 'hmax6':
                        ds                              = ds.resample(time='6h').max('time')
                        ds                              = ds.rename({'hmax':variable})
                        ds[variable].attrs['long_name'] = '6-hourly maximum individual wave height'
                        ds[variable].attrs['units']     = 'm'
                elif variable == 'bfi6':
                        ds                              = ds.resample(time='6h').max('time')
                        ds                              = ds.rename({'bfi':variable})
                        ds[variable].attrs['long_name'] = '6-hourly maximum benjamin-feir index'
                        ds[variable].attrs['units']     = 'unitless'                        
                elif variable == 'u10m6':
                        ds                              = ds.resample(time='6h').mean('time')
                        ds                              = ds.rename({'u10':variable})
                        ds[variable].attrs['long_name'] = '6-hourly mean 10m u component of wind'
                        ds[variable].attrs['units']     = 'unitless'                        
                elif variable == 'v10m6':
                        ds                              = ds.resample(time='6h').mean('time')
                        ds                              = ds.rename({'v10':variable})
                        ds[variable].attrs['long_name'] = '6-hourly mean 10m v component of wind'
                        ds[variable].attrs['units']     = 'unitless'
                elif variable == 't2m6':
                        ds                              = ds.resample(time='6h').mean('time')
                        ds                              = ds.rename({'t2m':variable})
                        ds[variable].attrs['long_name'] = '6-hourly mean 2m temperature'
                        ds[variable].attrs['units']     = 'K'
                        
                ds.to_netcdf(path + filename)
                ds.close()
                
                if (dates[i+1].year - dates[i].year == 1) or (dates[i+1].strftime('%Y-%m-%d') == date_end): # if new year or end of dates

                        print('')
                        print('aggregate daily files to yearly file & delete daily files..')
                        year         = str(dates[i].year)
                        filenames    = variable + '_' + gridstring + '_' + str(year) + '-*'
                        filename_out = variable + '_' + gridstring + '_' + str(year) + '.nc'
                        ds           = xr.open_mfdataset(path + filenames)
                        with ProgressBar(): ds = ds.compute()
                        ds.to_netcdf(path + filename_out)
                        ds.close()
                        os.system('rm ' + path + filenames)

                        print('compress files to reduce space..')
                        print('')
                        misc.compress_file(comp_lev,3,filename_out,path)



