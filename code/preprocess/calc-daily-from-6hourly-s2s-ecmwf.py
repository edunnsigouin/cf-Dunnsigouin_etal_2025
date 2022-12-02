"""
Calculates daily quantities based off of downloaded 6hourly 
s2s ecmwf mars data
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
import os
from forsikring import date_to_model  as d2m
from forsikring import config,misc,s2s
from matplotlib  import pyplot as plt

# INPUT ----------------------------------------------- 
variables     = ['sf']                  
dtypes        = ['cf']                  # control & perturbed forecasts/hindcasts
product       = 'hindcast'              # hindcast or forecast ?
mon_thu_start = ['20210104','20210107'] # first monday & thursday initialization date of forecast
num_i_weeks   = 1                       # number of forecasts/hindcast intialization dates to download
grid          = '0.25/0.25'             # '0.25/0.25' or '0.5/0.5'
comp_lev      = 5                       # level of compression with nccopy (1-10)
write2file    = False
# -----------------------------------------------------            

# get all dates for monday and thursday forecast initializations
dates_monday_thursday = s2s.get_monday_thursday_dates(mon_thu_start,num_i_weeks)

for variable in variables:
    for date in dates_monday_thursday:
        for dtype in dtypes:

            misc.tic()
            
            datestring = date.strftime('%Y-%m-%d')
            print('variable: ' + variable + ', date: ' + datestring + ', dtype: ' + dtype)
            
            path_in    = config.dirs[product + '_6hourly']
            path_out   = config.dirs[product + '_daily']

            if grid == '0.25/0.25': gridstring = '0.25x0.25'
            elif grid == '0.5/0.5': gridstring = '0.5x0.5'
                
            forcastcycle  = d2m.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
            basename      = '%s_%s_%s_%s'%(forcastcycle,gridstring,datestring,dtype)
                
            if variable == 'tp': # daily accumulated precip (m)
                filename_in                      = path_in + variable + '/' + variable + '_' + basename + '.nc'
                filename_out                     = path_out + variable + '/' + variable + '_' + basename + '.nc'
                ds                               = xr.open_dataset(filename_in)
                ds                               = ds.resample(time='1D').sum('time')
                ds[variable].attrs['units']      = 'm'
                ds[variable].attrs['long_name']  = 'daily accumulated precipitation'
                if write2file: ds.to_netcdf(filename_out)  
                ds.close()

            elif variable == 'rn': # daily accumulated rain (precip - snowfall, m)  
                filename1_in                     = path_in + 'tp/' + 'tp' + '_' + basename + '.nc'
                filename2_in                     = path_in + 'sf/' + 'sf' + '_' + basename + '.nc'
                filename_out                     = path_out + variable + '/' + variable + '_' + basename + '.nc' 
                ds1                              = xr.open_dataset(filename1_in)
                ds2                              = xr.open_dataset(filename2_in)
                ds1                              = ds1.resample(time='1D').sum('time')
                ds2                              = ds2.resample(time='1D').sum('time')
                ds1['tp']                        = ds1['tp'] - ds2['sf']
                ds1                              = ds1.rename({'tp':variable})
                ds1[variable].attrs['units']     = 'm'
                ds1[variable].attrs['long_name'] = 'daily accumulated rainfall'
                if write2file: ds1.to_netcdf(filename_out)
                ds1.close()
                ds2.close()

            elif variable == 'mxtp6': # daily maximum 6 hour accumulated precip (m)
                filename_in                      = path_in + 'tp/' + 'tp' + '_' + basename + '.nc'
                filename_out                     = path_out + variable + '/' + variable + '_' + basename + '.nc'
                ds                               = xr.open_dataset(filename_in)
                ds                               = ds.resample(time='1D').max('time')
                ds                               = ds.rename({'tp':variable})
                ds[variable].attrs['units']      = 'm'
                ds[variable].attrs['long_name']  = 'daily maximum 6 hour accumulated precipitation'
                if write2file: ds.to_netcdf(filename_out)
                ds.close()

            elif variable == 'mxtpr': # daily maximum timestep precipitation rate (kgm-2s-1)
                filename_in                     = path_in + variable + '/' + variable + '_' + basename + '.nc'
                filename_out                    = path_out + variable + '/' + variable + '_' + basename + '.nc'
                ds                              = xr.open_dataset(filename_in)
                ds                              = ds.resample(time='1D').max('time')
                ds[variable].attrs['units']     = 'kg m**-2 s**-1'
                ds[variable].attrs['long_name'] = 'daily maximum timestep precipitation rate'
                if write2file: ds.to_netcdf(filename_out)
                ds.close()
            
            elif variable == 'mxrn6': # daily maximum 6 hour accumulated rain (precip - snowfall, m)
                filename1_in              = path_in + 'tp/' + 'tp' + '_' + basename + '.nc'
                filename2_in              = path_in + 'sf/' + 'sf' + '_' + basename + '.nc'
                filename_out              = path_out + variable + '/' + variable + '_' + basename + '.nc'
                ds1                       = xr.open_dataset(filename1_in)
                ds2                       = xr.open_dataset(filename2_in)
                da                        = (ds1['tp'] - ds2['sf']).resample(time='1D').max('time')
                da.name                   = variable
                da.attrs['units']         = 'm'
                da.attrs['long_name']     = 'daily maximum 6 hour accumulated rainfall'
                if write2file: da.to_netcdf(filename_out)
                ds1.close()
                ds2.close()
                da.close()

            print('compress file to reduce space..')
            s2s.compress_file(comp_lev,3,filename_out,path_out + variable + '/')

            misc.toc()



