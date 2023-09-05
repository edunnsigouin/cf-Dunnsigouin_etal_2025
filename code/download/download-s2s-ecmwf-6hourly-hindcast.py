"""
Downloads raw ecmwf S2S data following this procedure:
https://confluence.ecmwf.int/display/WEBAPI/Access+MARS

Basically, you need to populate a dictionary with specific
values/keywords and use it as input to the downloading api

Note: You need special access to download raw forecasts (at higher
resolution). Contact the person from Norway here:
https://www.ecmwf.int/en/about/contact-us/computing-representatives 

NOTE2: This specific script downloads only hindcast data
and splits each download request into the first 10 years of hindcasts
and the last 10 years, then combines the files into one. This is
an attempt to download less fields at a once, to speed up the downloads
on the mars server.
"""

from ecmwfapi                    import *
import os,sys
import pandas                    as pd
import xarray                    as xr
import numpy                     as np
from datetime                    import datetime
from forsikring                  import config,misc,s2s

# input -----------------------------------
product       = 'hindcast' # hindcast/vr_hindcast
init_start    = '20210830' # first initialization date of forecast (either a monday or thursday)
init_n        = 36          # number of forecast initializations      
nhdates       = 20 # number of hindcast years  
grid          = '0.5/0.5' # degree lat/lon resolution
area          = '73.5/-27/33/45'# ecmwf european lat-lon bounds [73.5/-27/33/45]
var           = 't2m'
comp_lev      = 5 # file compression level
write2file    = True
# -----------------------------------------

# initialize mars server
server = ECMWFService("mars")

# define stuff
if product == 'hindcast':
    if grid == '0.25/0.25':
        step = '0/to/360/by/6'
        #step = '0/to/168/by/6'
    elif grid == '0.5/0.5':
        step = '366/to/1104/by/6'
    number = '1/to/10'
    stream = 'enfh'
    path   = config.dirs['hindcast_6hourly'] + var + '/'
    dtypes = ['cf','pf']
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
    if product == 'hindcast':
        param = '228.128'
    elif product == 'vr_hindcast':
        param = '228.230' # note different variable for variable resolution
elif var == 'sf': # snowfall per 6 hours (m)
    if product == 'hindcast':
        param = '144.128'
    elif product == 'vr_hindcast':
        param = '144.230' # note different variable for variable resolution
elif var == 'mx6tpr': # maximum 6-hourly precipitation rate after last post-processing (kgm-2s-1)
    param = '226.228'
elif var =='t2m': # 2 meter temperature
    param = '167.128'

    
# populate API dictionary
dic1 = {
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
    'use':'infrequent',
    'date':''
}    

# get all dates for monday and thursday forecast initializations
init_dates = s2s.get_init_dates(init_start,init_n)
print(init_dates)

#init_dates  = pd.date_range(init_start, periods=init_n)
#print(init_dates)

# populate dictionary some more and download each hindcast/forcast one-by-one
if write2file:
    for date in init_dates:
        for dtype in dtypes:
            
            misc.tic()

            if product == 'hindcast':

                # NOTE: here I seperated the hindcast downloads into the requests for the
                # first and last 10 years of hindcasts (2001-2010,2011-2020). This makes the
                # downloads much faster on the mars server.
            
                # define filenames & variables
                datestring       = date.strftime('%Y-%m-%d')
                refyear          = int(datestring[:4])
                hdate1           = '/'.join([datestring.replace('%i'%refyear,'%i'%i) for i in range(refyear-nhdates,refyear-int(nhdates/2))]) # first 10 years
                hdate2           = '/'.join([datestring.replace('%i'%refyear,'%i'%i) for i in range(refyear-int(nhdates/2),refyear)]) # last 10 years
                forcastcycle     = s2s.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
                base_name        = '%s_%s_%s_%s_%s'%(var,forcastcycle,gridstring,datestring,dtype)
                filename1_grb    = base_name + '_01' + '.grb' 
                filename2_grb    = base_name + '_02' + '.grb'
                filename3_grb    = base_name + '.grb'
                filename_nc      = base_name + '.nc'
        
                # populate dictionary with first half of hindcast years
                dic1['date']     = datestring
                dic1['type']     = dtype
                dic1['hdate']    = hdate1 # only usefull for hindcast downloads

                # create dictionary with other half of hindcast years
                dic2             = dic1.copy()
                dic2['hdate']    = hdate2
            
                print('downloading..')
                server.execute(dic1, path + filename1_grb)
                server.execute(dic2, path + filename2_grb)

                print('convert grib to netcdf..')
                os.system('grib_copy ' + path + filename1_grb + ' ' + path + filename2_grb + ' ' + path + filename3_grb)
                os.system('rm ' + path + filename1_grb)
                os.system('rm ' + path + filename2_grb)
                s2s.grib_to_netcdf(path,filename3_grb,filename_nc)
            
                print('compress files to reduce space..')
                s2s.compress_file(comp_lev,4,filename_nc,path)

            elif product == 'vr_hindcast':
            
                datestring       = date.strftime('%Y-%m-%d')
                refyear          = int(datestring[:4])
                hdate            = '/'.join([datestring.replace('%i'%refyear,'%i'%i) for i in range(refyear-nhdates,refyear)])
                forcastcycle     = s2s.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
                base_name        = '%s_%s_%s_%s_%s_%s'%(var,forcastcycle,'vr',gridstring,datestring,dtype)
                filename_grb     = base_name + '.grb'
                filename_nc      = base_name + '.nc'
                dic1['date']     = datestring
                dic1['type']     = dtype
                dic1['hdate']    = hdate 

                print('downloading..')
                server.execute(dic1, path + filename_grb)

                print('convert grib to netcdf..')
                s2s.grib_to_netcdf(path,filename_grb,filename_nc)

                print('compress files to reduce space..')
                s2s.compress_file(comp_lev,4,filename_nc,path)

            
            misc.toc()


