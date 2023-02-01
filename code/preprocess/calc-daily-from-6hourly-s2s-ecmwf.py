"""
Calculates daily quantities based off of downloaded 6hourly 
s2s ecmwf mars data (forecasts and hindcasts). 
Combines cf and pf files into one.
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
import os
from forsikring import config,misc,s2s
from matplotlib  import pyplot as plt

# INPUT ----------------------------------------------- 
variables     = ['mx24tp6']                # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
dtypes        = ['cf','pf']             # control & perturbed forecasts/hindcasts
product       = 'hindcast'              # hindcast or forecast ?
mon_thu_start = ['20210104','20210107'] # first monday & thursday initialization date of forecast
num_i_weeks   = 52                       # number of forecasts/hindcast intialization dates to download
grid          = '0.5/0.5'             # '0.25/0.25' or '0.5/0.5'
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
            
            if grid == '0.25/0.25': gridstring = '0.25x0.25'
            elif grid == '0.5/0.5': gridstring = '0.5x0.5'
                
            forcastcycle  = s2s.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
            basename      = '%s_%s_%s_%s'%(forcastcycle,gridstring,datestring,dtype)
                
            if variable == 'tp24': # daily accumulated precip (m)

                path_in                          = config.dirs[product + '_6hourly'] + 'tp6/'
                path_out                         = config.dirs[product + '_daily'] + variable + '/'
                filename_in                      = 'tp6_' + basename + '.nc'
                filename_out                     = variable + '_' + basename + '.nc'
                ds                               = xr.open_dataset(path_in + filename_in)

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
                ds                               = ds.rename({'tp6':variable})    
                ds[variable].attrs['units']      = 'm'
                ds[variable].attrs['long_name']  = 'daily accumulated precipitation'

                if write2file: s2s.to_netcdf_pack64bit(ds[variable],path_out + filename_out) 
                ds.close()

            elif variable == 'rn24': # daily accumulated rain (precip - snowfall, m)

                path1_in                         = config.dirs[product + '_6hourly'] + 'tp6/'
                path2_in                         = config.dirs[product + '_6hourly'] + 'sf6/'
                path_out                         = config.dirs[product + '_daily'] + variable + '/'
                filename1_in                     = 'tp6' + '_' + basename + '.nc'
                filename2_in                     = 'sf6' + '_' + basename + '.nc'
                filename_out                     = variable + '_' + basename + '.nc'
                ds1                              = xr.open_dataset(path1_in + filename1_in)
                ds2                              = xr.open_dataset(path2_in + filename2_in)

                # shift time back by 6 hours so that accumulated quantities correspond
                # to correct day
                ds1['time'] = ds1.time - np.timedelta64(6,'h')
                ds2['time'] = ds2.time - np.timedelta64(6,'h')
                ds1         = ds1.resample(time='1D').sum('time')
                ds2         = ds2.resample(time='1D').sum('time')
                if gridstring == '0.25x0.25':
                    ds1 = ds1.isel(time=slice(1,ds1.time.size))
                    ds2 = ds2.isel(time=slice(1,ds2.time.size))
                    
                ds1['tp6']                       = ds1['tp6'] - ds2['sf6']
                ds1                              = ds1.rename({'tp6':variable})
                ds1[variable].attrs['units']     = 'm'
                ds1[variable].attrs['long_name'] = 'daily accumulated rainfall'
                if write2file: s2s.to_netcdf_pack64bit(ds1[variable],path_out + filename_out) 
                ds1.close()
                ds2.close()

            elif variable == 'mx24tp6': # daily maximum 6 hour accumulated precip (m)

                path_in                          = config.dirs[product + '_6hourly'] + 'tp6/'
                path_out                         = config.dirs[product + '_daily'] + variable + '/'
                filename_in                      = 'tp6' + '_' + basename + '.nc'
                filename_out                     = variable + '_' + basename + '.nc'
                ds                               = xr.open_dataset(path_in + filename_in)

                # shift time back by 6 hours so that accumulated quantities correspond
                # to correct day   
                ds['time'] = ds.time - np.timedelta64(6,'h')
                ds         = ds.resample(time='1D').max('time')
                if gridstring == '0.25x0.25':
                    ds = ds.isel(time=slice(1,ds.time.size))

                ds                               = ds.rename({'tp6':variable})
                ds[variable].attrs['units']      = 'm'
                ds[variable].attrs['long_name']  = 'daily maximum 6 hour accumulated precipitation'
                if write2file: s2s.to_netcdf_pack64bit(ds[variable],path_out + filename_out) 
                ds.close()

            elif variable == 'mx24rn6': # daily maximum 6 hour accumulated rainfall (m)

                path1_in                         = config.dirs[product + '_6hourly'] + 'tp6/'
                path2_in                         = config.dirs[product + '_6hourly'] + 'sf6/'
                path_out                         = config.dirs[product + '_daily'] + variable + '/'
                
                filename1_in                     = 'tp6_' + basename + '.nc'
                filename2_in                     = 'sf6_' + basename + '.nc'
                filename_out                     = variable + '_' + basename + '.nc'

                ds1                              = xr.open_dataset(path1_in + filename1_in)
                ds2                              = xr.open_dataset(path2_in + filename2_in)

                # shift time back by 6 hours so that accumulated quantities correspond
                # to correct day                                                                                                                                                
                ds1['time'] = ds1.time - np.timedelta64(6,'h')
                ds2['time'] = ds2.time - np.timedelta64(6,'h')
                da          = (ds1['tp6'] - ds2['sf6']).resample(time='1D').max('time')
                if gridstring == '0.25x0.25':
                    da = da.isel(time=slice(1,da.time.size))
                    
                da.name                          = variable
                da.attrs['units']                = 'm'
                da.attrs['long_name']            = 'daily maximum 6 hour accumulated rainfall'
                if write2file: s2s.to_netcdf_pack64bit(da,path_out + filename_out) 
                ds1.close()
                ds2.close()
                da.close()

            elif variable == 'mx24tpr': # daily maximum timestep precipitation rate (kgm-2s-1)

                path_in                         = config.dirs[product + '_6hourly'] + 'mxtpr/'
                path_out                        = config.dirs[product + '_daily'] + variable + '/'
                filename_in                     = 'mxtpr_' + basename + '.nc'
                filename_out                    = variable + '_' + basename + '.nc'
                ds                              = xr.open_dataset(path_in + filename_in)
                ds                              = ds.resample(time='1D').max('time')                
                ds                              = ds.rename({'mxtpr':variable})
                ds[variable].attrs['units']     = 'kg m**-2 s**-1'
                ds[variable].attrs['long_name'] = 'daily maximum timestep precipitation rate'
                if write2file: s2s.to_netcdf_pack64bit(ds[variable],path_out + filename_out)
                ds.close()

                
        if write2file:
            
            print('combine cf and pf files into one file..')
            basename_cf     = '%s_%s_%s_%s'%(forcastcycle,gridstring,datestring,'cf')
            basename_pf     = '%s_%s_%s_%s'%(forcastcycle,gridstring,datestring,'pf')
            basename        = '%s_%s_%s'%(forcastcycle,gridstring,datestring)
            filename_out_cf = variable + '_' + basename_cf + '.nc'
            filename_out_pf = variable + '_' + basename_pf + '.nc'
            filename_out    = variable + '_' + basename + '.nc'
            ds_cf           = xr.open_dataset(path_out + filename_out_cf)
            ds_pf           = xr.open_dataset(path_out + filename_out_pf)
            ds_cf           = ds_cf.assign_coords(number=51).expand_dims(dim={"number": 1},axis=1)
            ds              = xr.concat([ds_pf,ds_cf], dim="number")
            s2s.to_netcdf_pack64bit(ds[variable],path_out + filename_out)
            ds_pf.close()
            ds_cf.close()
            ds.close()
            os.system('rm ' + path_out + filename_out_cf)
            os.system('rm ' + path_out + filename_out_pf)
            
            print('compress file to reduce space..')
            print('')
            s2s.compress_file(comp_lev,3,filename_out,path_out)

            
        misc.toc()



