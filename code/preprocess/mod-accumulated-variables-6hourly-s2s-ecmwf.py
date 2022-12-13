"""
Modifies 6hourly accumulated variables (sf,tp) so that they record values accumulated in a given 6 hour chunk
rather than accumulated from time 0 (cumsum) of the forecast/hindcast. Data from s2s ecmwf mars. 
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
import os
from forsikring import date_to_model  as d2m
from forsikring import config,misc,s2s
from matplotlib  import pyplot as plt

# INPUT ----------------------------------------------- 
variables     = ['tp']                  
dtypes        = ['cf']                  # control & perturbed forecasts/hindcasts
product       = 'hindcast'              # hindcast or forecast ?
mon_thu_start = ['20210104','20210107'] # first monday & thursday initialization date of forecast
num_i_weeks   = 2                       # number of forecasts/hindcast intialization dates to download
grid          = '0.5/0.5'               # '0.25/0.25' or '0.5/0.5'
comp_lev      = 5                       # level of compression with nccopy (1-10)
write2file    = False
# -----------------------------------------------------            

# get all dates for monday and thursday forecast initializations
dates_monday_thursday = s2s.get_monday_thursday_dates(mon_thu_start,num_i_weeks)

dates_monday_thursday = dates_monday_thursday[:1]

for variable in variables:
    for date in dates_monday_thursday:
        for dtype in dtypes:

            misc.tic()
            
            datestring = date.strftime('%Y-%m-%d')
            print('variable: ' + variable + ', date: ' + datestring + ', dtype: ' + dtype)

            # define some paths and strings
            path_in    = config.dirs[product + '_6hourly'] + variable + '/'
            path_out   = config.dirs['forecast_temp'] + variable + '/'
            if grid == '0.25/0.25': gridstring = '0.25x0.25'
            elif grid == '0.5/0.5': gridstring = '0.5x0.5'

            # read data
            forcastcycle   = d2m.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
            basename       = '%s_%s_%s_%s_%s'%(variable,forcastcycle,gridstring,datestring,dtype)
            filename_in    = basename + '.nc'
            filename_out   = 'mod_' + basename + '.nc'
            ds             = xr.open_dataset(path_in + filename_in)

            if grid == '0.25/0.25': # first 15 days of hindcast/forecast @ high-resolution
                
                # to get 6 hour accumulated values do var(t) - var(t-1)
                ds[variable] = ds[variable].pad(time=1,mode='edge')[:-1,:].diff('time') 



                
                # need to find a solution so that the time indexing is xarray style not numpy
                # since hindcasts have hdate as the first variable, not time!!!




                
            elif grid == '0.5/0.5': # last 30 days of hindcast/forecast @ low-resolution

                print(ds[variable])
                # remove hour 360 from low-resolution hindcast files if they downloaded hour 360
		# so all files start at hour 366 
                if ds['time'].size == 125:
                    ds = ds.isel(time = slice(1,125))
                    
                # to get 6 hour accumulated values do var(t) = var(t) - var(t-1).
                # note: var(t=0) = 0
                temp         = ds[variable][0,:] # to be used below (var_old(366))
                ds[variable] = ds[variable].pad(time=1,mode='edge')[:-1,:].diff('time')

                # Fix hour 366 in LR data using variable resolution data, var_new(366) = var_old(366) - var_variable_res(360)
                variable_vr       = variable + 'var'
                basename_vr       = '%s_%s_%s_%s_%s_%s'%(variable,forcastcycle,'vr',gridstring,datestring,dtype)
                filename_in_vr    = basename_vr + '.nc'
                ds_vr             = xr.open_dataset(path_in + filename_in_vr)
                ds[variable][0,:] = temp - ds_vr[variable_vr][0,:]
                ds_vr.close()

            if variable == 'tp':
                ds[variable].attrs['units']      = 'm'
                ds[variable].attrs['long_name']  = 'accumulated precipitation'
            elif variable == 'sf':
                ds[variable].attrs['units']      = 'm'
                ds[variable].attrs['long_name']  = 'accumulated snowfall'
                    
            if write2file: s2s.to_netcdf_pack64bit(ds[variable],path_out + filename_out)
            ds.close()
            
            print('compress file to reduce space..')
            s2s.compress_file(comp_lev,4,filename_out,path_out)

            misc.toc()



