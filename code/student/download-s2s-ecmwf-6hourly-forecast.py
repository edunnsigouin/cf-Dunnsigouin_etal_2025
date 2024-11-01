"""
Downloads raw ecmwf S2S data following this procedure:
https://confluence.ecmwf.int/display/WEBAPI/Access+MARS

Basically, you need to populate a dictionary with specific
values/keywords and use it as input to the downloading api

Note: You need special access to download raw forecasts (at higher
resolution). Contact the person from Norway here:
https://www.ecmwf.int/en/about/contact-us/computing-representatives 

Note: this code is only to download forecast data (not hindcasts) & is 
used to download the data for NHH masters students.
"""

from ecmwfapi                    import *
import os,sys
import pandas                    as pd
import xarray                    as xr
import numpy                     as np
from datetime                    import datetime
from forsikring                  import config,misc,s2s

# input -----------------------------------
product             = 'forecast' # forecast/vr_forecast
first_forecast_date = '20230102' # first initialization date of forecast (either a monday or thursday)
number_forecast     = 104        # number of forecast initializations   
grid                = '0.25/0.25' # degree lat/lon resolution
domain              = 'southern_norway'
variables           = ['tp','t2m','sd']
comp_lev            = 5 # file compression level
write2file          = True
# -----------------------------------------

# initialize mars server
server = ECMWFService("mars")

# define stuff
if grid == '0.25/0.25': step = '0/to/360/by/6'
elif grid == '0.5/0.5': step = '366/to/1104/by/6'
number = '1/to/50'
stream = 'enfo'
path   = config.dirs['s2s_forecast_6hourly_student'] 
dtypes = ['cf','pf']

if domain == 'bergen': area = '60.75/5/60.25/5.5'
elif domain == 'oslo': area = '60/10.25/59.5/10.75'
elif domain == 'southern_norway': area = '66/3.5/57/12.5'

if grid == '0.25/0.25': gridstring = '0.25x0.25'
elif grid == '0.5/0.5': gridstring = '0.5x0.5'

param = ''
for variable in variables:
    if variable == 'tp':
        param = param + '228.128/'
    elif variable == 't2m':
        param =	param + '167.128/'
    elif variable == 'sd':
        param = param + '141.128/'
    elif variable == 'mwg6':
        param = param + '123.128/'
    elif variable == 'mwg':
        param = param + '49.128/'
    elif variable == 'u10':
        param = param + '165.128/'
    elif variable == 'v10':
        param = param + '166.128/'
    elif variable == 'sf':
        param = param + '144.128/'
    if variable == variables[-1]: param = param[:-1]

# populate API dictionary
dic = {
    'class': 'od',
    'expver': '1',
    'stream': stream,
    'time': '00:00:00',
    'grid': grid,
    'area': area,
    'param': param,
    'levtype': 'sfc',
    'step': step,
    'number': number,
    'use':'infrequent',
    'type':'',
    'date':''
}    

# get all dates for monday and thursday forecast initializations
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecast,'annual')
print(forecast_dates)

# populate dictionary some more and download eachforcast one-by-one
if write2file:
    for date in forecast_dates:
        for dtype in dtypes:

            misc.tic()
            
            # define filenames & variables
            datestring       = date.strftime('%Y-%m-%d')
            refyear          = int(datestring[:4])
            forcastcycle     = s2s.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')

            variable_string  = '-'.join(variables)
            base_name        = '%s_%s_%s_%s_%s'%(variable_string,forcastcycle,gridstring,datestring,dtype)
            filename_grb     = base_name + '.grb'
            filename_nc      = base_name + '.nc'

            # populate dictionary some more
            dic['date']  = datestring
            dic['type']  = dtype

            print('downloading: ' + path + filename_grb)
            print(dic)
            server.execute(dic, path + filename_grb)
    
            print('convert grib to netcdf..')    
            s2s.grib_to_netcdf(path,filename_grb,filename_nc)

            print('compress files to reduce space..')
            misc.compress_file(comp_lev,4,filename_nc,path)

            misc.toc()


