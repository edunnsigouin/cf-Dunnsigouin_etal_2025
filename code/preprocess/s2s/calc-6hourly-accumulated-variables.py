"""
Modifies 6hourly accumulated variables (sf,tp) so that they record values accumulated in a given 6 hour chunk
rather than accumulated from time 0 (cumsum) of the forecast/hindcast. Data from s2s ecmwf mars. 

This code also fixes the accumulated data on day 360 when the resolution of the model changes from 
0.25x0.25 to 0.5x0.5. It does so using the 'variable resolution data'. An explanation on how to do this 
can be found here: https://confluence.ecmwf.int/display/UDOC/MARS+FAQ
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
import os
from forsikring import config,misc,s2s
from matplotlib  import pyplot as plt

# INPUT ----------------------------------------------- 
variables           = ['tp']                  
dtypes              = ['cf','pf']             # control & perturbed forecasts/hindcasts
product             = 'hindcast'              # hindcast or forecast
first_forecast_date = '20200102' # first initialization date of forecast (either a monday or thursday) 
number_forecasts    = 313        # number of forecast initializations 
season              = 'annual'
grid                = '0.25x0.25'             # '0.25x0.25' or '0.5x0.5'
comp_lev            = 5                       # level of compression with nccopy (1-10)
write2file          = True
# -----------------------------------------------------            

# get all dates for monday and thursday forecast initializations
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')
print(forecast_dates)

for variable in variables:
    for date in forecast_dates:
        for dtype in dtypes:

            misc.tic()
            
            print('')
            print('variable: ' + variable + ', date: ' + date + ', dtype: ' + dtype)

            # define some paths and strings
            variable_out = variable + '6' 
            path_in      = config.dirs['s2s_' + product + '_6hourly'] + variable + '/'
            path_out     = config.dirs['s2s_' + product + '_6hourly'] + variable_out + '/'
            forcastcycle = s2s.which_mv_for_init(date,model='ECMWF',fmt='%Y-%m-%d')
            filename_in  = '%s_%s_%s_%s_%s.nc'%(variable,forcastcycle,grid,date,dtype)
            filename_out = '%s_%s_%s_%s_%s.nc'%(variable_out,forcastcycle,grid,date,dtype)
            
            # read data
            ds = xr.open_dataset(path_in + filename_in)

            if grid == '0.25x0.25': # first 15 days of hindcast/forecast @ high-resolution
                
                # to get 6 hour accumulated values do var(t) - var(t-1)
                # note: var(t=0) = 0
                ds[variable] = ds[variable].pad(time=1,mode='edge').diff('time').isel(time=slice(None,ds.time.size))                

            elif grid == '0.5x0.5': # last 30 days of hindcast/forecast @ low-resolution

                # remove hour 360 from low-resolution hindcast files if they downloaded hour 360
		# so all files start at hour 366
                if ds['time'].size == 125:
                    ds = ds.isel(time = slice(1,125))
                    
                # to get 6 hour accumulated values do var(t) = var(t) - var(t-1).
                # note: var(t=0) = 0
                temp         = ds[variable][dict(time=0)] # to be used below (var_old(366))
                ds[variable] = ds[variable].pad(time=1,mode='edge').diff('time').isel(time=slice(None,ds.time.size))
                
                # Fix hour 366 in LR data using variable resolution data, var_new(366) = var_old(366) - var_variable_res(360)
                variable_vr                = variable + 'var'
                filename_in_vr             = '%s_%s_%s_%s_%s_%s.nc'%(variable,forcastcycle,'vr',grid,date,dtype)
                ds_vr                      = xr.open_dataset(path_in + filename_in_vr)
                ds[variable][dict(time=0)] = temp - ds_vr[variable_vr][dict(time=0)]
                ds_vr.close()

            # rename variable and attributes    
            ds = ds.rename({variable:variable_out})    
            if variable == 'tp':
                ds[variable_out].attrs['units']      = 'm'
                ds[variable_out].attrs['long_name']  = '6-hourly accumulated precipitation'
            elif variable == 'sf':
                ds[variable_out].attrs['units']      = 'm'
                ds[variable_out].attrs['long_name']  = '6-hourly accumulated snowfall'

            if write2file:
                print('writing to file..')
                #misc.to_netcdf_pack64bit(ds[variable_out],path_out + filename_out)
                ds.to_netcdf(path_out + filename_out)
                misc.compress_file(comp_lev,3,filename_out,path_out)
                print('')
                
            ds.close()
            
            misc.toc()



