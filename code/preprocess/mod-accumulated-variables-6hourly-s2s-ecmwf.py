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
dtypes        = ['cf','pf']             # control & perturbed forecasts/hindcasts
product       = 'hindcast'              # hindcast or forecast ?
mon_thu_start = ['20210104','20210107'] # first monday & thursday initialization date of forecast
num_i_weeks   = 2                       # number of forecasts/hindcast intialization dates to download
grid          = '0.25/0.25'             # '0.25/0.25' or '0.5/0.5'
comp_lev      = 5                       # level of compression with nccopy (1-10)
write2file    = True
# -----------------------------------------------------            

# get all dates for monday and thursday forecast initializations
dates_monday_thursday = s2s.get_monday_thursday_dates(mon_thu_start,num_i_weeks)

for variable in variables:
    for date in dates_monday_thursday:
        for dtype in dtypes:

            misc.tic()
            
            datestring = date.strftime('%Y-%m-%d')
            print('variable: ' + variable + ', date: ' + datestring + ', dtype: ' + dtype)

            # define some paths and strings
            path_in    = config.dirs[product + '_6hourly']
            path_out   = config.dirs[product + '_temp']
            if grid == '0.25/0.25': gridstring = '0.25x0.25'
            elif grid == '0.5/0.5': gridstring = '0.5x0.5'

            # read data
            forcastcycle   = d2m.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
            basename       = '%s_%s_%s_%s_%s'%(var,forcastcycle,gridstring,datestring,dtype)
            basename_vr    = '%s_%s_%s_%s_%s_%s'%(var,forcastcycle,'vr',gridstring,datestring,dtype)
            filename_in    = path_in + variable + '/' + basename + '.nc'
            filename_in_vr = path_in + variable + '/' + basename_vr + '.nc' 
            filename_out   = path_out + variable + '/mod_' + variable + '_' + basename + '.nc'
            ds             = xr.open_dataset(filename_in)

            if grid == '0.25/0.25': # first 15 days of hindcast/forecast @ high-resolution
                # to get 6 hour accumulated values do var(t) - var(t-1)
                ds[variable] = ds[variable].pad(time=1,mode='edge')[:,:-1,:,:].diff('time') 

            elif grid == '0.5/0.5': # last 30 days of hindcast/forecast @ low-resolution
                # to get 6 hour accumulated values do var(t) = var(t) - var(t-1)
                ds[variable] = ds[variable].pad(time=1,mode='edge')[:,:-1,:,:].diff('time')

                # 1) fix hour 366 in LR data using variable resolution data, var_new(366) = var_old(366) - var_variable_res(360)
                # 2) Add day 360 from variable resolution data to LR data.
                ds_vr                 = xr.open_dataset(filename_in_vr)
                ds[variable][1,:,:,:] = ds[variable][1,:,:,:] - ds_vr[variable][-1,:,:,:]
                ds[variable][0,:,:,:] = ds_vr[variable][-1,:,:,:] - ds_vr[variable][-2,:,:,:]
                ds_vr.close()
                
            if variable == 'tp':
                ds[variable].attrs['units']      = 'm'
                ds[variable].attrs['long_name']  = 'accumulated precipitation'
            elif variable == 'sf':
                ds[variable].attrs['units']      = 'm'
                ds[variable].attrs['long_name']  = 'accumulated snowfall'
                    
            if write2file: s2s.to_netcdf_pack64bit(ds[variable],filename_out)
            ds.close()
            
            print('compress file to reduce space..')
            s2s.compress_file(comp_lev,3,filename_out,path_out + variable + '/')

            misc.toc()



