"""
Calculates daily quantities based off of downloaded 6hourly 
ERA5 data 
"""

import numpy  as np
import xarray as xr
import os
from forsikring import config,misc

# INPUT ----------------------------------------------- 
variables  = ['mxtp6']
years      = np.arange(1995,1996,1)
comp_lev   = 5
write2file = True
# -----------------------------------------------------            


for variable in variables:
    for year in years:
        misc.tic()
        print('variable: ' + variable + ', year: ' + str(year))
        
        if variable == 'tp': # daily accumulated precip (m)
            dir_in                    = config.dirs['era5_6hourly'] + variable + '/'
            dir_out                   = config.dirs['era5_daily'] + variable + '/'
            filename                  = variable + '_' + str(year) + '.nc'
            filename_out              = variable + '_' + str(year) + '.nc'
            ds                        = xr.open_dataset(dir_in + filename)
            ds                        = ds.resample(time='1D').sum('time')
            ds.tp.attrs['units']      = 'm'
            ds.tp.attrs['long_name']  = 'daily accumulated precipitation'
            if write2file:
                ds.to_netcdf(dir_out + filename)
            ds.close()
            
        elif variable == 'rn': # daily accumulated rain (precip - snowfall, m)
            dir_in1   = config.dirs['era5_6hourly'] + 'tp/'
            dir_in2   = config.dirs['era5_6hourly'] + 'sf/'
            dir_out   = config.dirs['era5_daily'] + variable + '/'
            filename1 = 'tp_' + str(year) + '.nc'
            filename2 = 'sf_' + str(year) + '.nc'
            ds1       = xr.open_dataset(dir_in1 + filename1)
            ds2       = xr.open_dataset(dir_in2 + filename2)
            ds1       = ds1.resample(time='1D').sum('time')
            ds2       = ds2.resample(time='1D').sum('time')
            ds1['tp'] = ds1['tp'] - ds2['sf']
            if write2file:
                filename_out              = 'rn_' + str(year) + '.nc'
                ds1                       = ds1.rename({'tp':'rn'})
                ds1.rn.attrs['units']     = 'm'
                ds1.rn.attrs['long_name'] = 'daily accumulated rainfall'
                ds1.to_netcdf(dir_out + filename_out)
            ds1.close()
            ds2.close()
            
        elif variable == 'mxtp6': # daily maximum 6 hour accumulated precip (m)
            dir_in                    = config.dirs['era5_6hourly'] + 'tp/'
            dir_out                   = config.dirs['era5_daily'] + variable + '/'
            filename                  = 'tp_' + str(year) + '.nc'
            filename_out              =	variable + '_' + str(year) + '.nc'
            ds                        = xr.open_dataset(dir_in + filename)
            ds                        = ds.resample(time='1D').max('time')
            ds.tp.attrs['units']      = 'm'
            ds.tp.attrs['long_name']  = 'daily maximum 6 hour accumulated precipitation'
            if write2file:
                ds.to_netcdf(dir_out + filename_out)
            ds.close()

        elif variable == 'mxtpr': # daily maximum timestep precipitation rate (kgm-2s-1)
            dir_in                    = config.dirs['era5_6hourly'] + variable + '/'
            dir_out                   = config.dirs['era5_daily'] + variable + '/'
            filename                  = variable + '_' + str(year) + '.nc'
            filename_out              = variable + '_' + str(year) + '.nc'
            ds                        = xr.open_dataset(dir_in + filename)
            ds                        = ds.resample(time='1D').max('time')
            ds.tp.attrs['units']      = 'kg m**-2 s**-1'
            ds.tp.attrs['long_name']  = 'daily maximum timestep precipitation rate'
            if write2file:
                ds.to_netcdf(dir_out + filename_out)
            ds.close()
            
        elif variable == 'mxrn6': # daily maximum 6 hour accumulated rain (precip - snowfall, m)
            dir_in1   = config.dirs['era5_6hourly'] + 'tp/'
            dir_in2   = config.dirs['era5_6hourly'] + 'sf/'
            dir_out   = config.dirs['era5_daily'] + variable + '/'
            filename1 = 'tp_' + str(year) + '.nc'
            filename2 = 'sf_' + str(year) + '.nc'
            ds1       = xr.open_dataset(dir_in1 + filename1)
            ds2       = xr.open_dataset(dir_in2 + filename2)
            da        = (ds1['tp'] - ds2['sf']).resample(time='1D').max('time')
            if write2file:
                filename_out             = variable + '_' + str(year) + '.nc'
                da.name                  = variable
                da.attrs['units']        = 'm'
                da.attrs['long_name']    = 'daily maximum 6 hour accumulated rainfall'
                da.to_netcdf(dir_out + filename_out)
            ds1.close()
            ds2.close()
            da.close()
            
        print('compress file to reduce space..')
        cmd               = 'nccopy -k 3 -s -d ' + str(comp_lev) + ' '
        filename_out_comp = 'compressed_' + variable + '_' + str(year) + '.nc'
        os.system(cmd + dir_out + filename_out + ' ' + dir_out + filename_out_comp)
        os.system('mv ' + dir_out + filename_out_comp + ' ' + dir_out + filename_out)
        
        misc.toc()
