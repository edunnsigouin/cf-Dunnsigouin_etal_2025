"""
Downloads raw ecmwf S2S data following this procedure:
https://confluence.ecmwf.int/display/WEBAPI/Access+MARS

Basically, you need to populate a dictionary with specific
values/keywords and use it as input to the downloading api

Note: You need special access to download raw forecasts (at higher
resolution). Contact the person from Norway here:
https://www.ecmwf.int/en/about/contact-us/computing-representatives 

Note: this code is only to download forecast data (not hindcasts)
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
first_forecast_date = '20230803' # first initialization date of forecast (either a monday or thursday)
number_forecast     = 6        # number of forecast initializations   
grid                = '0.25/0.25' # degree lat/lon resolution
area                = '73.5/-27/33/45'# ecmwf european lat-lon bounds [73.5/-27/33/45]
var                 = 'tp'
comp_lev            = 5 # file compression level
write2file          = True
# -----------------------------------------

# initialize mars server
server = ECMWFService("mars")

# define stuff
if product == 'forecast':
    if grid == '0.25/0.25':
        step = '0/to/360/by/6'
    elif grid == '0.5/0.5':
        step = '366/to/1104/by/6'
    number = '1/to/50'
    stream = 'enfo'
    path   = config.dirs['s2s_forecast_6hourly'] + var + '/'
    dtypes = ['cf','pf']
elif product == 'vr_forecast':
    step   = '360'
    number = '1/to/50'
    stream = 'efov'
    path   = config.dirs['s2s_forecast_6hourly'] + var + '/'
    dtypes = ['cf','pf']
    grid   = '0.5/0.5' # need to use low-res
    
if grid == '0.25/0.25': gridstring = '0.25x0.25'
elif grid == '0.5/0.5': gridstring = '0.5x0.5'
    
if var == 'tp': # total precipitation per 6 hours (m)
    if product == 'forecast':
        param = '228.128'
    elif product == 'vr_forecast':
        param = '228.230' # note different variable for variable resolution
elif var == 'sf': # snowfall per 6 hours (m)
    if product == 'forecast':
        param = '144.128'
    elif product == 'vr_forecast':
        param = '144.230' # note different variable for variable resolution
elif var == 'mx6tpr': # maximum 6-hourly precipitation rate after last post-processing (kgm-2s-1)
    param = '226.228'
elif var =='t2m': # 2 meter temperature
    param = '167.128'

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
#forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecast,'annual')
forecast_dates = pd.date_range(first_forecast_date, periods=number_forecast, freq="D")
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
        
            if product == 'forecast': base_name = '%s_%s_%s_%s_%s'%(var,forcastcycle,gridstring,datestring,dtype)
            elif product == 'vr_forecast': base_name = '%s_%s_%s_%s_%s_%s'%(var,forcastcycle,'vr',gridstring,datestring,dtype)

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


