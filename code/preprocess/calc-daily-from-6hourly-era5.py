"""
Calculates daily quantities based off of downloaded 6hourly 
ERA5 data 
"""

import numpy  as np
import xarray as xr
import os
from forsikring import config,misc,s2s

# INPUT ----------------------------------------------- 
variables  = ['tp24'] # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
years      = np.arange(2022,2023,1)
grid       = '0.5/0.5' # '0.25/0.25' or '0.5/0.5'
comp_lev   = 5
write2file = True
# -----------------------------------------------------            

for variable in variables:
    for year in years:
        
        misc.tic()
        print('variable: ' + variable + ', year: ' + str(year))

        if grid == '0.25/0.25':
            path_in    = config.dirs['era5_6hourly'] 
            path_out   = config.dirs['era5_daily_raw']
            gridstring = '0.25x0.25'
        elif grid == '0.5/0.5':
            path_in    = config.dirs['era5_6hourly'] 
            path_out   = config.dirs['era5_daily_raw'] 
            gridstring = '0.5x0.5'
            
        if variable == 'tp24': # daily accumulated precip (m)
            
            dir_in                          = path_in + 'tp6/'
            dir_out                         = path_out + variable + '/'
            filename_in                     = 'tp6_' + gridstring + '_' + str(year) + '.nc'
            filename_out                    = variable + '_' + gridstring + '_' + str(year) + '.nc'
            ds                              = xr.open_dataset(dir_in + filename_in)
            ds                              = ds.resample(time='1D').sum('time')
            ds                              = ds.rename({'tp6':variable})
            ds[variable].attrs['units']     = 'm'
            ds[variable].attrs['long_name'] = 'daily accumulated precipitation'
            if write2file: ds.to_netcdf(dir_out + filename_out)
            ds.close()
            
        elif variable == 'rn24': # daily accumulated rain (precip - snowfall, m)
            
            dir_in1      = path_in + 'tp6/'
            dir_in2      = path_in + 'sf6/'
            dir_out      = path_out + variable + '/'
            filename1_in = 'tp6_' + gridstring + '_' + str(year) + '.nc'
            filename2_in = 'sf6_' + gridstring + '_' + str(year) + '.nc'
            ds1          = xr.open_dataset(dir_in1 + filename1_in)
            ds2          = xr.open_dataset(dir_in2 + filename2_in)
            ds1          = ds1.resample(time='1D').sum('time')
            ds2          = ds2.resample(time='1D').sum('time')
            ds1['tp6']   = ds1['tp6'] - ds2['sf6']
            if write2file:
                filename_out                     = variable + '_' + gridstring + '_' + str(year) + '.nc'
                ds1                              = ds1.rename({'tp6':variable})
                ds1[variable].attrs['units']     = 'm'
                ds1[variable].attrs['long_name'] = 'daily accumulated rainfall'
                ds1.to_netcdf(dir_out + filename_out)
            ds1.close()
            ds2.close()
            
        elif variable == 'mx24tp6': # daily maximum 6 hour accumulated precip (m)
            
            dir_in                          = path_in + 'tp6/'
            dir_out                         = path_out + variable + '/'
            filename_in                     = 'tp6_' + gridstring + '_' + str(year) + '.nc'
            filename_out                    = variable + '_' + gridstring + '_' + str(year) + '.nc'
            ds                              = xr.open_dataset(dir_in + filename_in)
            ds                              = ds.rename({'tp6':variable})
            ds                              = ds.resample(time='1D').max('time')
            ds[variable].attrs['units']     = 'm'
            ds[variable].attrs['long_name'] = 'daily maximum 6 hour accumulated precipitation'
            if write2file: ds.to_netcdf(dir_out + filename_out)
            ds.close()
            
        elif variable == 'mx24rn6': # daily maximum 6 hour accumulated rain (precip - snowfall, m)
            
            dir_in1      = path_in + 'tp6/'
            dir_in2      = path_in + 'sf6/'
            dir_out      = path_out + variable + '/'
            filename1_in = 'tp6_' + gridstring + '_' + str(year) + '.nc'
            filename2_in = 'sf6_' + gridstring + '_' + str(year) + '.nc'
            ds1          = xr.open_dataset(dir_in1 + filename1_in)
            ds2          = xr.open_dataset(dir_in2 + filename2_in)
            da           = (ds1['tp6'] - ds2['sf6']).resample(time='1D').max('time')
            if write2file:
                filename_out             = variable + '_' + gridstring + '_' + str(year) + '.nc'
                da.name                  = variable
                da.attrs['units']        = 'm'
                da.attrs['long_name']    = 'daily maximum 6 hour accumulated rainfall'
                da.to_netcdf(dir_out + filename_out)
            ds1.close()
            ds2.close()
            da.close()

        elif variable == 'mx24tpr': # daily maximum timestep precipitation rate (kgm-2s-1)

            dir_in                          = path_in + 'mx6tpr/'
            dir_out                         = path_out + variable + '/'
            filename_in                     = 'mx6tpr_' + gridstring + '_' + str(year) + '.nc'
            filename_out                    = variable + '_' + gridstring + '_' + str(year) + '.nc'
            ds                              = xr.open_dataset(dir_in + filename_in)
            ds                              = ds.resample(time='1D').max('time')
            ds                              = ds.rename({'mx6tpr':variable})
            ds[variable].attrs['units']     = 'kg m**-2 s**-1'
            ds[variable].attrs['long_name'] = 'daily maximum timestep precipitation rate'
            if write2file: ds.to_netcdf(dir_out + filename_out)
            ds.close()
            

        if write2file:   
            print('compress file to reduce space..')
            s2s.compress_file(comp_lev,3,filename_out,dir_out)

        
        misc.toc()
