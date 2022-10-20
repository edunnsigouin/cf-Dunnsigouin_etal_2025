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
from datetime                    import datetime
from forsikring                  import date_to_model  as d2m
from forsikring                  import config

# input -----------------------------------
product    = 'hindcast' # hindcast/forecast
nhdates    = 1 # number of hindcast years
grid       = '0.25/0.25' # degree lat/lon resolution
area       = '73.5/-27/33/45'# ecmwf european lat-lon bounds [73.5/-27/33/45]
var        = 'tp'
step       = '0'#'0/to/1104/by/6' #  46 days at given time resolution
write2file = True
# -----------------------------------------

# download stuff
server = ECMWFService("mars")

# define stuff
if product == 'hindcast':
    number = '1'#'1/to/10'
    stream = 'enfh'
    path   = config.dirs['raw_hindcast'] + var + '/'
elif product == 'forecast':
    number = '1/to/50'
    stream = 'enfo'
    path   = config.dirs['raw_forecast'] + var + '/'
    
dtypes = ['pf']

if var == 'tp': # total precipitation (m)
    param = '228.128'
elif var == 'mxtpr6': # maximum precipitation rate over the last 6 hours (kg/m2/s)
    param = '228.224'
elif var == 'sf': # snowfall (m)
    param = '144.128'
    
# populate dictionary

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




# generate set of continuous monday and thursday dates for the year 2021  
#dates_monday          = pd.date_range("20210104", periods=52, freq="7D") # forecasts start Thursday
#dates_thursday        = pd.date_range("20210107", periods=52, freq="7D") # forecasts start Monday
#dates_monday_thursday = dates_monday.union(dates_thursday)

dates_monday          = pd.date_range("20210104", periods=1, freq="7D") # forecasts start Thursday
dates_monday_thursday = dates_monday

# populate dictionary some more and download each hindcast/forcast one-by-one
for date in dates_monday_thursday:
    for dtype in dtypes:
        
        datestring   = date.strftime('%Y-%m-%d')
        refyear      = int(datestring[:4])
        forcastcycle = d2m.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
        filename     = '%s_%s_%s_%s_%s.grb'%(var,forcastcycle,'05x05',datestring,dtype) 
        dic['date']  = datestring
        dic['type']  = dtype
        if product == 'hindcast':
            hdate        = '/'.join([datestring.replace('%i'%refyear,'%i'%i) for i in range(refyear-nhdates,refyear)])
            dic['hdate'] = hdate

        print('downloading: ' + filename)
        print(dic)
        if write2file:
            server.execute(dic,path + filename)

        # merge cf and pf into new file & delete old files



