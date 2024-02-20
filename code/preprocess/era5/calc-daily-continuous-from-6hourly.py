"""
Calculates daily quantities based off of downloaded 6hourly 
ERA5 data and outputs yearly files of continuous data. 
"""

import numpy  as np
import xarray as xr
import os
from forsikring import config,misc,s2s

# INPUT ----------------------------------------------- 
variables  = ['tp24'] # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
years      = np.arange(2023,2024,1)
grid       = '0.25x0.25' # '0.25x0.25' or '0.5x0.5'
comp_lev   = 5
write2file = False
# -----------------------------------------------------            

for variable in variables:
    for year in years:
        
        misc.tic()
        print('processing variable: ' + variable + ', year: ' + str(year))

        if variable == 'tp24': # daily accumulated precip (m)
            
            dir_in                          = config.dirs['era5_6hourly'] + 'tp6/'
            dir_out                         = config.dirs['era5_daily'] + variable + '/'
            filename_in                     = 'tp6_' + grid + '_' + str(year) + '.nc'
            filename_out                    = variable + '_' + grid + '_' + str(year) + '.nc'
            ds                              = xr.open_dataset(dir_in + filename_in)
            ds                              = ds.resample(time='1D').sum('time')
            ds                              = ds.rename({'tp6':variable})
            ds[variable].attrs['units']     = 'm'
            ds[variable].attrs['long_name'] = 'daily accumulated precipitation'
            if write2file: ds.to_netcdf(dir_out + filename_out)
            ds.close()
            
        elif variable == 'rn24': # daily accumulated rain (precip - snowfall, m)
            
            dir_in1      = config.dirs['era5_6hourly'] + 'tp6/'
            dir_in2      = config.dirs['era5_6hourly'] + 'sf6/'
            dir_out      = config.dirs['era5_daily'] + variable + '/'
            filename1_in = 'tp6_' + grid + '_' + str(year) + '.nc'
            filename2_in = 'sf6_' + grid + '_' + str(year) + '.nc'
            ds1          = xr.open_dataset(dir_in1 + filename1_in)
            ds2          = xr.open_dataset(dir_in2 + filename2_in)
            ds1          = ds1.resample(time='1D').sum('time')
            ds2          = ds2.resample(time='1D').sum('time')
            ds1['tp6']   = ds1['tp6'] - ds2['sf6']
            if write2file:
                filename_out                     = variable + '_' + grid + '_' + str(year) + '.nc'
                ds1                              = ds1.rename({'tp6':variable})
                ds1[variable].attrs['units']     = 'm'
                ds1[variable].attrs['long_name'] = 'daily accumulated rainfall'
                ds1.to_netcdf(dir_out + filename_out)
            ds1.close()
            ds2.close()
            
        elif variable == 'mx24tp6': # daily maximum 6 hour accumulated precip (m)
            
            dir_in                          = config.dirs['era5_6hourly'] + 'tp6/'
            dir_out                         = config.dirs['era5_daily'] + variable + '/'
            filename_in                     = 'tp6_' + grid + '_' + str(year) + '.nc'
            filename_out                    = variable + '_' + grid + '_' + str(year) + '.nc'
            ds                              = xr.open_dataset(dir_in + filename_in)
            ds                              = ds.rename({'tp6':variable})
            ds                              = ds.resample(time='1D').max('time')
            ds[variable].attrs['units']     = 'm'
            ds[variable].attrs['long_name'] = 'daily maximum 6 hour accumulated precipitation'
            if write2file: ds.to_netcdf(dir_out + filename_out)
            ds.close()
            
        elif variable == 'mx24rn6': # daily maximum 6 hour accumulated rain (precip - snowfall, m)
            
            dir_in1      = config.dirs['era5_6hourly'] + 'tp6/'
            dir_in2      = config.dirs['era5_6hourly'] + 'sf6/'
            dir_out      = config.dirs['era5_daily'] + variable + '/'
            filename1_in = 'tp6_' + grid + '_' + str(year) + '.nc'
            filename2_in = 'sf6_' + grid + '_' + str(year) + '.nc'
            ds1          = xr.open_dataset(dir_in1 + filename1_in)
            ds2          = xr.open_dataset(dir_in2 + filename2_in)
            da           = (ds1['tp6'] - ds2['sf6']).resample(time='1D').max('time')
            if write2file:
                filename_out             = variable + '_' + grid + '_' + str(year) + '.nc'
                da.name                  = variable
                da.attrs['units']        = 'm'
                da.attrs['long_name']    = 'daily maximum 6 hour accumulated rainfall'
                da.to_netcdf(dir_out + filename_out)
            ds1.close()
            ds2.close()
            da.close()

        elif variable == 'mx24tpr': # daily maximum timestep precipitation rate (kgm-2s-1)

            dir_in                          = config.dirs['era5_6hourly'] + 'mx6tpr/'
            dir_out                         = config.dirs['era5_daily'] + variable + '/'
            filename_in                     = 'mx6tpr_' + grid + '_' + str(year) + '.nc'
            filename_out                    = variable + '_' + grid + '_' + str(year) + '.nc'
            ds                              = xr.open_dataset(dir_in + filename_in)
            ds                              = ds.resample(time='1D').max('time')
            ds                              = ds.rename({'mx6tpr':variable})
            ds[variable].attrs['units']     = 'kg m**-2 s**-1'
            ds[variable].attrs['long_name'] = 'daily maximum timestep precipitation rate'
            if write2file: ds.to_netcdf(dir_out + filename_out)
            ds.close()
        elif variable == 't2m24': # daily-mean 2-meter temperature
            dir_in                          = config.dirs['era5_6hourly'] + 't2m6/'
            dir_out                         = config.dirs['era5_daily'] + variable + '/'
            filename_in                     = 't2m6_' + grid + '_' + str(year) + '.nc'
            filename_out                    = variable + '_' + grid + '_' + str(year) + '.nc'
            ds                              = xr.open_dataset(dir_in + filename_in)
            ds                              = ds.rename({'t2m6':variable})
            ds                              = ds.resample(time='1D').mean('time')
            ds[variable].attrs['units']     = 'K'
            ds[variable].attrs['long_name'] = 'daily-mean 2-meter temperature'
            if write2file: ds.to_netcdf(dir_out + filename_out)
            ds.close()
            

        if write2file: misc.compress_file(comp_lev,3,filename_out,dir_out)

        
        misc.toc()
