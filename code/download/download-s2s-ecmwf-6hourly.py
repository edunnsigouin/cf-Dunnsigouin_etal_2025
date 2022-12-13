"""
Downloads raw ecmwf S2S data following this procedure:
https://confluence.ecmwf.int/display/WEBAPI/Access+MARS

Basically, you need to populate a dictionary with specific
values/keywords and use it as input to the downloading api

Note: You need special access to download raw forecasts (at higher
resolution). Contact the person from Norway here:
https://www.ecmwf.int/en/about/contact-us/computing-representatives 
"""

from ecmwfapi                    import *
import os,sys
import pandas                    as pd
import xarray                    as xr
import numpy                     as np
from datetime                    import datetime
from forsikring                  import date_to_model  as d2m
from forsikring                  import config,misc,s2s

# input -----------------------------------
product       = 'vr_forecast' # hindcast/forecast/vr_forecast/vr_hindcast
mon_thu_start = ['20210104','20210107'] # first initialization date of forecast
num_i_weeks   = 52 # number of forecasts/hindcast intialization dates to download 
nhdates       = 20 # number of hindcast years  
grid          = '0.5/0.5' # degree lat/lon resolution
area          = '73.5/-27/33/45'# ecmwf european lat-lon bounds [73.5/-27/33/45]
var           = 'tp'
comp_lev      = 5 # file compression level
write2file    = True
# -----------------------------------------

# initialize mars server
server = ECMWFService("mars")

# define stuff
if product == 'hindcast':
    if grid == '0.25/0.25':
        step = '0/to/360/by/6'
    elif grid == '0.5/0.5':
        step = '360/to/1104/by/6'
    number = '1/to/10'
    stream = 'enfh'
    path   = config.dirs['hindcast_6hourly'] + var + '/'
    dtypes = ['pf']
elif product == 'forecast':
    if grid == '0.25/0.25':
        step = '0/to/360/by/6'
    elif grid == '0.5/0.5':
        step = '360/to/1104/by/6'
    number = '1/to/50'
    stream = 'enfo'
    path   = config.dirs['forecast_6hourly'] + var + '/'
    dtypes = ['cf','pf']
elif product == 'vr_forecast':
    step   = '360'
    number = '1/to/50'
    stream = 'efov'
    path   = config.dirs['forecast_6hourly'] + var + '/'
    dtypes = ['cf','pf']
    grid   = '0.5/0.5' # need to use low-res
elif product == 'vr_hindcast':
    step   = '360'
    number = '1/to/10'
    stream = 'efho'
    path   = config.dirs['hindcast_6hourly'] + var + '/'
    dtypes = ['cf','pf']
    grid   = '0.5/0.5' # need to use low-res
    
if grid == '0.25/0.25': gridstring = '0.25x0.25'
elif grid == '0.5/0.5': gridstring = '0.5x0.5'
    
if var == 'tp': # total precipitation per 6 hours (m)
    if (product == 'forecast') or (product == 'hindcast'):
        param = '228.128'
    elif (product == 'vr_forecast') or (product == 'vr_hindcast'):
        param = '228.230' # note different variable for variable resolution
elif var == 'sf': # snowfall per 6 hours (m)
    if (product == 'forecast') or (product == 'hindcast'):
        param = '144.128'
    elif (product == 'vr_forecast') or (product == 'vr_hindcast'):
        param = '144.230' # note different variable for variable resolution
elif var == 'mxtpr': # maximum daily precipitation rate after last post-processing (kgm-2s-1)
    param = '226.228'

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
    'type':'',
    'date':''
}    

# get all dates for monday and thursday forecast initializations
dates_monday_thursday = s2s.get_monday_thursday_dates(mon_thu_start,num_i_weeks)


# populate dictionary some more and download each hindcast/forcast one-by-one
for date in dates_monday_thursday:
    for dtype in dtypes:

        misc.tic()

        # define filenames & variables
        datestring       = date.strftime('%Y-%m-%d')
        refyear          = int(datestring[:4])
        hdate            = '/'.join([datestring.replace('%i'%refyear,'%i'%i) for i in range(refyear-nhdates,refyear)])
        forcastcycle     = d2m.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
        
        if (product == 'forecast') or (product == 'hindcast'): base_name = '%s_%s_%s_%s_%s'%(var,forcastcycle,gridstring,datestring,dtype)
        elif (product == 'vr_forecast') or (product == 'vr_hindcast'): base_name = '%s_%s_%s_%s_%s_%s'%(var,forcastcycle,'vr',gridstring,datestring,dtype)

        filename_grb     = base_name + '.grb'
        filename_nc      = base_name + '.nc'

        # populate dictionary some more
        dic['date']  = datestring
        dic['type']  = dtype
        dic['hdate'] = hdate # only usefull for hindcast downloads
        
        if write2file:
            print('downloading: ' + path + filename_grb)
            print(dic)
            server.execute(dic, path + filename_grb)
    
            print('convert grib to netcdf..')    
            s2s.grib_to_netcdf(path,filename_grb,filename_nc)

            print('compress files to reduce space..')
            s2s.compress_file(comp_lev,4,filename_nc,path)
    
        misc.toc()

