"""
Downloads raw ecmwf S2S data following this procedure:
https://confluence.ecmwf.int/display/WEBAPI/Access+MARS

Basically, you need to populate a dictionary with specific
values/keywords and use it as input to the downloading software.

Note: You need special access to download raw forecasts (at higher
resolution). Contact the person from Norway here:
https://www.ecmwf.int/en/about/contact-us/computing-representatives 
"""

from ecmwfapi                    import *
import os,sys
import pandas                    as pd
from datetime                    import datetime
from forsikring                  import date_to_model  as d2m
from forsikring                  import config

# input -----------------------------------
product = 'hindcast' # hindcast/forecast
dclass  = 'od' # operational archive/expert access data
expver  = 1    # operational version (not sure what this is)
stream  = 'enfh' # enfh=ensemble hindcast,enfo=ensemble forecast
time    = '00:00:00' # time of day for start of forecast
grid    = '0.5/0.5' # degree lat/lon resolution
area    = '89/-45/20/50' #lat-lon limits for download
var     = 'tp'
levtype = 'sfc' # surface variable 
step    = '0/to/1104/by/6' #  46 days at given time resolution
dformat = 'netcdf'
# -----------------------------------------

# download stuff
server = ECMWFService("mars")

# define stuff
if product == 'hindcast':
    number = '1/to/10'
    stream = 'enfh'
elif product == 'forecast':
    number = '1/to/50'
    stream = 'enfo'

if var == 'tp':
    param = '228.128'

# populate dictionary
dic = {
    'class': dclass,
    'expver': expver,
    'stream': stream,
    'time': time,
    'grid': grid,
    'area': area,
    'param':param,
    'levtype':levtype,
    'step':step,
    'format':dformat,
    'number':number,
    'type':'',
    'date':''
}    

# generate set of continuous monday and thursday dates  
dates_monday   = pd.date_range("20210104", periods=52, freq="7D") # forecasts start Thursday
dates_thursday = pd.date_range("20210107", periods=52, freq="7D") # forecasts start Monday
dates_fcycle   = dates_monday.union(dates_thursday)

# populate dictionary some more and download each hindcast/forcast one-by-one
for dates in dates_fcycle:
    for dtype in ('cf','pf'):
        
        path         = config.dirs[product]
        datestring   = dates.strftime('%Y-%m-%d')
        refyear      = int(datestring[:4])
        datadir      = path + var + '/' 
        forcastcycle = d2m.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
        filename     = '%s/%s_%s_%s_%s_%s.nc'%(datadir,var,forcastcycle,'05x05',datestring,dtype) 
        dic['date']  = datestring
        dic['type']  = dtype
        if product == 'hindcast':
            hdate        = '/'.join([datestring.replace('%i'%refyear,'%i'%i) for i in range(refyear-20,refyear)])
            dic['hdate'] = hdate

        print(filename)
        #server.execute(dic,filename)


