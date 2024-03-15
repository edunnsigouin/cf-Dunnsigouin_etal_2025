"""
Modifies 6hourly accumulated variables (sf,tp) so that they record values accumulated in a given 6 hour chunk
rather than accumulated from time 0 (cumsum) of the forecast/hindcast. Data from s2s ecmwf mars. 

This code also fixes the accumulated data on day 360 when the resolution of the model changes from 
0.25x0.25 to 0.5x0.5. It does so using the 'variable resolution data'. An explanation on how to do this 
can be found here: https://confluence.ecmwf.int/display/UDOC/MARS+FAQ

NOTE: this version of the code is meant to handle the subset of forecasts downloaded for NHH masters students
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
product             = 'forecast'              # hindcast or forecast
first_forecast_date = '20190103' # first initialization date of forecast (either a monday or thursday) 
number_forecasts    = 104        # number of forecast initializations 
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
            path_in      = config.dirs['s2s_' + product + '_6hourly_student'] 
            path_out     = config.dirs['s2s_' + product + '_6hourly_student'] + variable_out + '/'
            forcastcycle = s2s.which_mv_for_init(date,model='ECMWF',fmt='%Y-%m-%d')
            filename_in  = 'tp-t2m-sd_' + '%s_%s_%s_%s.nc'%(forcastcycle,grid,date,dtype)
            filename_out = variable_out + '_' + '%s_%s_%s_%s.nc'%(forcastcycle,grid,date,dtype)
            
            # read data
            da = xr.open_dataset(path_in + filename_in)[variable]
                
            # to get 6 hour accumulated values do var(t) - var(t-1)
            # note: var(t=0) = 0
            da = da.pad(time=1,mode='edge').diff('time').isel(time=slice(None,da.time.size))                

            # rename variable and attributes    
            da = da.rename(variable_out)
            if variable == 'tp':
                da.attrs['units']      = 'm'
                da.attrs['long_name']  = '6-hourly accumulated precipitation'

            if write2file:
                print('writing to file..')
                da.to_netcdf(path_out + filename_out)
                misc.compress_file(comp_lev,3,filename_out,path_out)
                print('')
                
            da.close()
            
            misc.toc()



