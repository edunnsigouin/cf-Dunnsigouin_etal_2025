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
            forcastcycle  = d2m.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
            basename      = '%s_%s_%s_%s'%(forcastcycle,gridstring,datestring,dtype)
            filename_in   = path_in + variable + '/' + variable + '_' + basename + '.nc'
            filename_out  = path_out + variable + '/mod_' + variable + '_' + basename + '.nc'
            ds            = xr.open_dataset(filename_in)

            if grid == '0.25/0.25': # first 15 days of hindcast/forecast
                ds[variable] = ds[variable].pad(time=1,mode='edge')[:,:-1,:,:].diff('time') # key operation
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



