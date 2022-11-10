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
from forsikring                  import config

# input -----------------------------------
product       = 'hindcast' # hindcast/forecast
mon_thu_start = ['20210104','20210107'] # first initialization date of forecast
num_weeks     = 1 # number of forecasts to download
nhdates       = 1 # number of hindcast years
grid          = '0.25/0.25' # degree lat/lon resolution
area          = '73.5/-27/33/45'# ecmwf european lat-lon bounds [73.5/-27/33/45]
var           = 't2m'
step          = '0/to/24'#'0/to/1104/by/6' #  46 days at given time resolution
comp_lev      = 5 # file compression level
write2file    = False
# -----------------------------------------

# download stuff
server = ECMWFService("mars")

# define stuff
if product == 'hindcast':
    number = '1/to/10'
    stream = 'enfh'
    path   = config.dirs['raw_hindcast'] + var + '/'
    dtypes = ['cf','pf']
elif product == 'forecast':
    number = '1/to/50'
    stream = 'enfo'
    path   = config.dirs['raw_forecast'] + var + '/'
    dtypes = ['cf','pf']

# translate variable names to code    
if var == 'tpd': # total precipitation per day (m)
    param = '228.128'
elif var == 'mxtp6': # maximum daily total precipitation in 6 hour interval (m)
    param = '228.128'
elif var == 'mxtprd': # maximum daily precipitation rate at a given timestep (kgm-2s-1)
    param = '226.228'
elif var == 'sf': # total snowfall per day (m)
    param = '144.128'
elif var == 'mxsf6': # maximum daily total snowfall in 6 hour interval (m)
    param = '144.128'    
elif var == 't2m':
    param = '167.128' # two-meter temperature

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


# generate set of continuous monday and thursday dates starting on mon_thu_start[0] and mon_thu_start[1] respectively
#dates_monday          = pd.date_range("20210104", periods=num_weeks, freq="7D") # forecasts start Thursday
#dates_thursday        = pd.date_range("20210107", periods=num_weeks, freq="7D") # forecasts start Monday
#dates_monday_thursday = dates_monday.union(dates_thursday)

dates_monday          = pd.date_range(mon_thu_start[0], periods=num_weeks, freq="7D") # forecasts start Thursday
dates_monday_thursday = dates_monday

# populate dictionary some more and download each hindcast/forcast one-by-one
for date in dates_monday_thursday:
    for dtype in dtypes:
        
        datestring    = date.strftime('%Y-%m-%d')
        refyear       = int(datestring[:4])
        forcastcycle  = d2m.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
        base_name     = '%s_%s_%s_%s_%s'%(var,forcastcycle,'05x05',datestring,dtype)
        filename_grb  = path + base_name + '.grb'
        filename_nc   = path + base_name + '.nc'
        dic['date']   = datestring
        dic['type']   = dtype
        if product == 'hindcast':
            hdate        = '/'.join([datestring.replace('%i'%refyear,'%i'%i) for i in range(refyear-nhdates,refyear)])
            dic['hdate'] = hdate

        print('downloading: ' + filename_grb)
        print(dic)

        if write2file:
            server.execute(dic,filename_grb)
    
        print('convert grib to netcdf..')    
        os.system('grib_to_netcdf ' + filename_grb + ' -o ' + filename_nc)    
        os.system('rm ' +  filename_grb)
        
    print('merge cf and pf into new file...')
    filename_cf    = path + '%s_%s_%s_%s_%s.nc'%(var,forcastcycle,'05x05',datestring,'cf')
    filename_pf    = path + '%s_%s_%s_%s_%s.nc'%(var,forcastcycle,'05x05',datestring,'pf')
    filename_merge = path + '%s_%s_%s_%s.nc'%(var,forcastcycle,'05x05',datestring)
    ds_cf          = xr.open_dataset(filename_cf)
    ds_pf          = xr.open_dataset(filename_pf)
    ds_cf          = ds_cf.assign_coords(number=11).expand_dims("number",axis=1) # hard coded # of ensemble members
    ds             = xr.merge([ds_pf,ds_cf])
    ds_cf.close()
    ds_pf.close()

    ds.to_netcdf(filename_merge)
    os.system('rm ' + filename_cf)
    os.system('rm ' + filename_pf)
    
    print('compress file to reduce space..')
    cmd              = 'nccopy -k 4 -s -d ' + str(comp_lev) + ' '
    filename_nc_comp = path + 'compressed_' + '%s_%s_%s_%s.nc'%(var,forcastcycle,'05x05',datestring)
    os.system(cmd + filename_merge + ' ' + filename_nc_comp)
    os.system('rm ' + filename_merge)
    os.system('mv ' + filename_nc_comp + ' ' + filename_merge)
