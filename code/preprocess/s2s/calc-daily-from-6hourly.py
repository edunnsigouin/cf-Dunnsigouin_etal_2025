"""
Calculates daily quantities from 6hourly s2s ecmwf mars data (forecasts and hindcasts). 
Also combines cf and pf files into one.
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
import os
from forsikring import config,misc,s2s
from matplotlib  import pyplot as plt

# INPUT ----------------------------------------------- 
variables           = ['t2m24']                # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
product             = 'hindcast'              # hindcast or forecast ?
first_forecast_date = '20201228' # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 2        # number of forecast initializations  
season              = 'annual'
grid                = '0.25x0.25'             # '0.25x0.25' or '0.5x0.5'
write2file          = True
# -----------------------------------------------------            

# get all dates for monday and thursday forecast initializations
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')
#forecast_dates = pd.date_range(first_forecast_date, periods=number_forecasts).strftime('%Y-%m-%d')
print(forecast_dates)


for variable in variables:
    for date in forecast_dates:
        for dtype in ['cf','pf']:

            misc.tic()
            print('variable: ' + variable + ', date: ' + date + ', dtype: ' + dtype)
            
            forecastcycle = s2s.which_mv_for_init(date,model='ECMWF',fmt='%Y-%m-%d')
            basename      = '%s_%s_%s_%s'%(forecastcycle,grid,date,dtype)
                
            if variable == 'tp24': # daily accumulated precip (m)

                path_in                          = config.dirs['s2s_' + product + '_6hourly'] + 'tp6/'
                path_out                         = config.dirs['s2s_' + product + '_daily'] + variable + '/'
                filename_in                      = 'tp6_' + basename + '.nc'
                filename_out                     = variable + '_' + basename + '.nc'
                ds                               = xr.open_dataset(path_in + filename_in)

                # shift time back by 6 hours. This means that for data on day 0 with hours 0,6,12,18,24,
                # hour 24 (accumulated from hour 18-24) is counted in day 0 not day 1. Basically,
                # sum of hours 6,12,18,24 instead of 0,6,12,18 on a given day.
                ds['time'] = ds.time - np.timedelta64(6,'h')
                ds         = ds.resample(time='1D').sum('time')
                if grid == '0.25x0.25':
                    # drop first 'day' for high res data since it accumulates data when
                    # there is no data (i.e. initialization time)
                    ds = ds.isel(time=slice(1,ds.time.size)) 
                # metadata    
                ds                                  = ds.rename({'tp6':variable})    
                ds[variable].attrs['units']         = 'm'
                ds[variable].attrs['long_name']     = 'daily accumulated precipitation'
                ds[variable].attrs['forecastcycle'] = forecastcycle

                if write2file: misc.to_netcdf_with_packing_and_compression(ds, path_out + filename_out)
                    
                ds.close()

            elif variable == 'rn24': # daily accumulated rain (precip - snowfall, m)

                path1_in                         = config.dirs['s2s_' + product + '_6hourly'] + 'tp6/'
                path2_in                         = config.dirs['s2s_' + product + '_6hourly'] + 'sf6/'
                path_out                         = config.dirs['s2s_' + product + '_daily'] + variable + '/'
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
                if grid == '0.25x0.25':
                    ds1 = ds1.isel(time=slice(1,ds1.time.size))
                    ds2 = ds2.isel(time=slice(1,ds2.time.size))
                    
                ds1['tp6']                           = ds1['tp6'] - ds2['sf6']
                ds1                                  = ds1.rename({'tp6':variable})
                ds1[variable].attrs['units']         = 'm'
                ds1[variable].attrs['long_name']     = 'daily accumulated rainfall'
                ds1[variable].attrs['forecastcycle'] = forecastcycle
                
                if write2file: misc.to_netcdf_with_packing_and_compression(ds1, path_out + filename_out)
                    
                ds1.close()
                ds2.close()

            elif variable == 'mx24tp6': # daily maximum 6 hour accumulated precip (m)

                path_in                          = config.dirs['s2s_' + product + '_6hourly'] + 'tp6/'
                path_out                         = config.dirs['s2s_' + product + '_daily'] + variable + '/'
                filename_in                      = 'tp6' + '_' + basename + '.nc'
                filename_out                     = variable + '_' + basename + '.nc'
                ds                               = xr.open_dataset(path_in + filename_in)

                # shift time back by 6 hours so that accumulated quantities correspond
                # to correct day   
                ds['time'] = ds.time - np.timedelta64(6,'h')
                ds         = ds.resample(time='1D').max('time')
                if grid == '0.25x0.25':
                    ds = ds.isel(time=slice(1,ds.time.size))

                ds                                  = ds.rename({'tp6':variable})
                ds[variable].attrs['units']         = 'm'
                ds[variable].attrs['long_name']     = 'daily maximum 6 hour accumulated precipitation'
                ds[variable].attrs['forecastcycle'] = forecastcycle
                
                if write2file: misc.to_netcdf_with_packing_and_compression(ds, path_out + filename_out)
                    
                ds.close()

            elif variable == 'mx24rn6': # daily maximum 6 hour accumulated rainfall (m)

                path1_in                         = config.dirs['s2s_' + product + '_6hourly'] + 'tp6/'
                path2_in                         = config.dirs['s2s_' + product + '_6hourly'] + 'sf6/'
                path_out                         = config.dirs['s2s_' + product + '_daily'] + variable + '/'
                
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
                if grid == '0.25x0.25':
                    da = da.isel(time=slice(1,da.time.size))
                    
                da.name                          = variable
                da.attrs['units']                = 'm'
                da.attrs['long_name']            = 'daily maximum 6 hour accumulated rainfall'
                da.attrs['forecastcycle']        = forecastcycle
                
                if write2file: misc.to_netcdf_with_packing_and_compression(da, path_out + filename_out)
                    
                ds1.close()
                ds2.close()
                da.close()

            elif variable == 'mx24tpr': # daily maximum timestep precipitation rate (kgm-2s-1)

                path_in                             = config.dirs['s2s_' + product + '_6hourly'] + 'mxtpr/'
                path_out                            = config.dirs['s2s_' + product + '_daily'] + variable + '/'
                filename_in                         = 'mxtpr_' + basename + '.nc'
                filename_out                        = variable + '_' + basename + '.nc'
                ds                                  = xr.open_dataset(path_in + filename_in)
                ds                                  = ds.resample(time='1D').max('time')                
                ds                                  = ds.rename({'mxtpr':variable})
                ds[variable].attrs['units']         = 'kg m**-2 s**-1'
                ds[variable].attrs['long_name']     = 'daily maximum timestep precipitation rate'
                ds[variable].attrs['forecastcycle'] = forecastcycle
                if write2file: misc.to_netcdf_with_packing_and_compression(ds, path_out + filename_out)
                    
                ds.close()
                
            elif variable == 't2m24': # daily-mean 2-meter temperature (K)

                path_in                             = config.dirs['s2s_' + product + '_6hourly'] + 't2m/'
                path_out                            = config.dirs['s2s_' + product + '_daily'] + variable + '/'
                filename_in                         = 't2m_' + basename + '.nc'
                filename_out                        = variable + '_' + basename + '.nc'
                ds                                  = xr.open_dataset(path_in + filename_in)                
                ds                                  = ds.resample(time='1D').mean('time')
                ds                                  = ds.rename({'t2m':variable})

                # remove last day since it only does an average of the first 6 hours
                # of the last day
                ds = ds.isel(time=slice(0,ds.time.size-1))

                ds[variable].attrs['units']         = 'K'
                ds[variable].attrs['long_name']     = 'daily-mean 2-meter temperature'
                ds[variable].attrs['forecastcycle'] = forecastcycle
                
                if write2file: misc.to_netcdf_with_packing_and_compression(ds, path_out + filename_out)
                    
                ds.close()

                

        if write2file:
            
            print('combine cf and pf files into one file..')
            basename_cf     = '%s_%s_%s_%s'%(forecastcycle,grid,date,'cf')
            basename_pf     = '%s_%s_%s_%s'%(forecastcycle,grid,date,'pf')
            basename        = '%s_%s'%(grid,date) 
            filename_out_cf = variable + '_' + basename_cf + '.nc'
            filename_out_pf = variable + '_' + basename_pf + '.nc'
            filename_out    = variable + '_' + basename + '.nc'
            ds_cf           = xr.open_dataset(path_out + filename_out_cf)
            ds_pf           = xr.open_dataset(path_out + filename_out_pf)
            ds_cf           = ds_cf.assign_coords(number=51).expand_dims(dim={"number": 1},axis=1)
            ds              = xr.concat([ds_pf,ds_cf], dim="number")
            misc.to_netcdf_with_packing_and_compression(ds, path_out + filename_out)
            ds_pf.close()
            ds_cf.close()
            ds.close()
            os.system('rm ' + path_out + filename_out_cf)
            os.system('rm ' + path_out + filename_out_pf)


            
        misc.toc()



