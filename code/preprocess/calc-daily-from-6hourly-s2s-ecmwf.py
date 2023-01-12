"""
Calculates daily quantities based off of downloaded 6hourly 
s2s ecmwf mars data
"""


import numpy    as np
import xarray   as xr
import pandas   as pd
import os
from forsikring import config,misc,s2s
from matplotlib  import pyplot as plt

# INPUT ----------------------------------------------- 
variables     = ['tp6']
dtypes        = ['cf']                  # control & perturbed forecasts/hindcasts
product       = 'forecast'              # hindcast or forecast ?
mon_thu_start = ['20210104','20210107'] # first monday & thursday initialization date of forecast
num_i_weeks   = 1                       # number of forecasts/hindcast intialization dates to download
grid          = '0.5/0.5'             # '0.25/0.25' or '0.5/0.5'
comp_lev      = 5                       # level of compression with nccopy (1-10)
write2file    = True
# -----------------------------------------------------            

# get all dates for monday and thursday forecast initializations
dates_monday_thursday = s2s.get_monday_thursday_dates(mon_thu_start,num_i_weeks)

dates_monday_thursday = dates_monday_thursday[:1]
#print(dates_monday_thursday)
      

for variable in variables:
    for date in dates_monday_thursday:
        for dtype in dtypes:

            misc.tic()
            
            datestring = date.strftime('%Y-%m-%d')
            print('variable: ' + variable + ', date: ' + datestring + ', dtype: ' + dtype)
            
            path_in    = config.dirs[product + '_6hourly']
            path_out   = config.dirs[product + '_daily']
            if grid == '0.25/0.25': gridstring = '0.25x0.25'
            elif grid == '0.5/0.5': gridstring = '0.5x0.5'
                
            forcastcycle  = s2s.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
            basename      = '%s_%s_%s_%s'%(forcastcycle,gridstring,datestring,dtype)
                
            if variable == 'tp6': # daily accumulated precip (m)

                new_variable                     = 'tp24'
                filename_in                      = path_in + variable + '/' + variable + '_' + basename + '.nc'
                filename_out                     = path_out + new_variable + '/' + new_variable + '_' + basename + '.nc'
                ds                               = xr.open_dataset(filename_in)

                # shift time back by 6 hours. This means that for data on day 0 with hours 0,6,12,18,24,
                # hour 24 (accumulated from hour 18-24) is counted in day 0 not day 1. Basically,
                # sum of hours 6,12,18,24 instead of 0,6,12,18 on a given day
                ds['time'] = ds.time - np.timedelta64(6,'h')
                ds         = ds.resample(time='1D').sum('time')
                if gridstring == '0.25x0.25':
                    # drop first 'day' for high res data since it accumulates data when
                    # there is no data (i.e. initialization time)
                    ds = ds.isel(time=slice(1,ds.time.size)) 

                # metadata    
                ds                                   = ds.rename({variable:new_variable})    
                ds[new_variable].attrs['units']      = 'm'
                ds[new_variable].attrs['long_name']  = 'daily accumulated precipitation'
                
                if write2file: s2s.to_netcdf_pack64bit(ds[new_variable],filename_out) 
                ds.close()

            elif variable == 'rn6': # daily accumulated rain (precip - snowfall, m)  
                filename1_in                     = path_in + 'tp/' + 'tp' + '_' + basename + '.nc'
                filename2_in                     = path_in + 'sf/' + 'sf' + '_' + basename + '.nc'
                filename_out                     = path_out + variable + '/' + variable + '_' + basename + '.nc' 
                ds1                              = xr.open_dataset(filename1_in)
                ds2                              = xr.open_dataset(filename2_in)
                ds1                              = ds1.resample(time='1D').sum('time')
                ds2                              = ds2.resample(time='1D').sum('time')
                ds1['tp']                        = ds1['tp'] - ds2['sf']
                ds1                              = ds1.rename({'tp':variable})
                ds1[variable].attrs['units']     = 'm'
                ds1[variable].attrs['long_name'] = 'daily accumulated rainfall'
                if write2file: s2s.to_netcdf_pack64bit(ds1[variable],filename_out) 
                ds1.close()
                ds2.close()

            elif variable == 'mxtp6': # daily maximum 6 hour accumulated precip (m)
                filename_in                      = path_in + 'tp/' + 'tp' + '_' + basename + '.nc'
                filename_out                     = path_out + variable + '/' + variable + '_' + basename + '.nc'
                ds                               = xr.open_dataset(filename_in)
                ds                               = ds.resample(time='1D').max('time')
                ds                               = ds.rename({'tp':variable})
                ds[variable].attrs['units']      = 'm'
                ds[variable].attrs['long_name']  = 'daily maximum 6 hour accumulated precipitation'
                if write2file: s2s.to_netcdf_pack64bit(ds[variable],filename_out) 
                ds.close()

            elif variable == 'mxtpr': # daily maximum timestep precipitation rate (kgm-2s-1)
                filename_in                     = path_in + variable + '/' + variable + '_' + basename + '.nc'
                filename_out                    = path_out + variable + '/' + variable + '_' + basename + '.nc'
                ds                              = xr.open_dataset(filename_in)
                ds                              = ds.resample(time='1D').max('time')
                ds[variable].attrs['units']     = 'kg m**-2 s**-1'
                ds[variable].attrs['long_name'] = 'daily maximum timestep precipitation rate'
                if write2file: s2s.to_netcdf_pack64bit(ds[variable],filename_out) 
                ds.close()
            
            elif variable == 'mxrn6': # daily maximum 6 hour accumulated rain (precip - snowfall, m)
                filename1_in              = path_in + 'tp/' + 'tp' + '_' + basename + '.nc'
                filename2_in              = path_in + 'sf/' + 'sf' + '_' + basename + '.nc'
                filename_out              = path_out + variable + '/' + variable + '_' + basename + '.nc'
                ds1                       = xr.open_dataset(filename1_in)
                ds2                       = xr.open_dataset(filename2_in)
                da                        = (ds1['tp'] - ds2['sf']).resample(time='1D').max('time')
                da.name                   = variable
                da.attrs['units']         = 'm'
                da.attrs['long_name']     = 'daily maximum 6 hour accumulated rainfall'
                if write2file: s2s.to_netcdf_pack64bit(da,filename_out) 
                ds1.close()
                ds2.close()
                da.close()

            if write2file:    
                print('compress file to reduce space..')
                s2s.compress_file(comp_lev,3,filename_out,path_out + variable + '/')

            misc.toc()



