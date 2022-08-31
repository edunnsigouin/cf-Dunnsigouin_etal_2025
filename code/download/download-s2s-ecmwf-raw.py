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
import forsikring.date_to_model  as d2m

# input -----------------------------------
dclass  = 'od' # operational archive/expert access data
expver  = 1    # operational version (not sure what this is)
stream  = 'enfh' # enfh=ensemble hindcast,enfo=ensemble forecast
time    = '00:00:00' # time of day for start of forecast
grid    = '0.5/0.5' # degree lat/lon resolution
area    = '89/-45/20/50' #lat-lon limits for download
param   = '228.128' # total precip=228.128,
levtype = 'sfc' # surface variable 
step    = '0/to/1104/by/6' #  46 days at given time resolution
dformat = 'netcdf'
# -----------------------------------------

# define ensemble number    
if stream == 'enfh':
    number = '1/to/10'
elif stream == 'enfo':
    number = '1/to/50'
    
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
    'date':'',
    'hdate':''
}    

# When is the best time to choose start dates?
# is there a list of model version history?
# need to ask Silje
# define start dates
# generate set of continuous monday and thursday dates  
dates_monday   = pd.date_range("20200123", periods=52, freq="7D") # forecasts start Thursday
dates_thursday = pd.date_range("20200127", periods=52, freq="7D") # forecasts start Monday
dates_fcycle   = dates_monday.union(dates_thursday)

print(dates_fcycle)

# define hindcast dates


# populate dictionary
dic['number'] = number


# define output file
target = ''


# download
#server = ECMWFService("mars")
#server.execute(dic,target)



"""
server = ECMWFService("mars")

product = 'hindcast' # forecast, hincast
dirbase = '/nird/projects/nird/NS9853K/DATA/S2S/MARS'
dir = '%s/%s/%s/'%(dirbase,product,'/ECMWF/sfc')


if product == 'hindcast':
    STREAM =  'enfh' 
if product == 'forecast':
    STREAM = 'enfo' 
  



basedict = {
    'class': 'od',
    'expver': '1',
    'stream': STREAM ,
    'time': '00:00:00',
    'grid': '0.5/0.5',
    'area': '89/-45/20/50'
    
}

# timestep stuff
l = range(0,1128,24)
paired = ['-'.join([str(v) for v in l[i:i + 2]]) for i in range(len(l))]
final = '/'.join(paired[0:-1])


meta = {
    'tp': {
        'param': '228228',  
        'levtype': 'sfc',
        #'step': '/'.join(['%i'%i for i in range(0,1128,24)]) 
        'step': '0/to/1104/by/24'
    },
    
     't2m': {
        'param': '167',  
        'levtype': 'sfc',
        'step': '/'.join([final]) 
    },
    
     'sst': {
        'param': '34.128',  
        'levtype': 'sfc',
        'step': '0/to/1104/by/24'
       # 'step': '/'.join([final]) 
    },
    
     'u10': {
        'param': '165',  
        'levtype': 'sfc',
        'step': '0/to/1104/by/24'
    },
    
    'v10': {
        'param': '166',  
        'levtype': 'sfc',
        'step': '0/to/1104/by/24'
    },
  
    'mslp': {
        'param': '151',  
        'levtype': 'sfc',
        'step': '0/to/1104/by/24'
    },
     
    'sal': {
        'param': '151175',  
        'levtype': 'o2d',
        'step': '/'.join([final]) 
    }
}

# generate set of continuous monday and thursday dates 
dates_monday = pd.date_range("20200123", periods=52, freq="7D") # forecasts start Thursday
dates_thursday = pd.date_range("20200127", periods=52, freq="7D") # forecasts start Monday
dates_fcycle = dates_monday.union(dates_thursday) 



# Program start
for filename in (
    'sst',
    
):
    for prefix in (
        'pf',
        'cf',
    ):
        for dates in dates_fcycle:
            d       = dates.strftime('%Y-%m-%d')
            refyear = int(d[:4])
            datadir = '%s/%s'%(dir,filename)
            
            #if not os.path.exists(datadir)  :
            #    os.makedirs(datadir)

            # hindcast dates for past twenty years
            hdate = '/'.join([d.replace('%i'%refyear,'%i'%i) for i in range(refyear-20,refyear)])

            # model version for given hindcast dates
            forcastcycle = d2m.which_mv_for_init(d,model='ECMWF',fmt='%Y-%m-%d')

            # name of output directory + filename 
            target = '%s/%s_%s_%s_%s_%s_%s.grb'%(datadir,filename,forcastcycle,'05x05',d,prefix,product)


            if not os.path.isfile(target):
               dic = basedict.copy()
               for k,v in meta[filename].items():
                   dic[k] = v
                   #print(dic)
               dic['date'] = d
               dic['type'] = prefix
               if ( product == 'hindcast' ):
                   dic['hdate'] = hdate
                   if prefix == 'pf':
                       dic['number'] =  '1/to/10'
               if ( product == 'forecast' ):
                   if prefix == 'pf':
                       dic['number'] =  '1/to/50'
              # out = '%s,%s=%s'%(dic, '"target"',target)
              # out= '%s=%s'%('target', target) 
               out= '%s%s%s'%('"', target,'"')
               print(dic)

            
               if server is not None:
                   server.execute(dic,target)
                    
print('DONE')
"""
