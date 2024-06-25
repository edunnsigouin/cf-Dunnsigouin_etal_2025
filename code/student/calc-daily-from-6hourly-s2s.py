"""
Calculates daily quantities from 6hourly s2s ecmwf mars data (forecasts and hindcasts). 
Also combines cf and pf files into one.

NOTE: this version of the code is meant to handle the subset of forecasts downloaded for NHH masters students
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
import os
from forsikring import config,misc,s2s,verify
from matplotlib  import pyplot as plt
from datetime import datetime, timedelta

# INPUT ----------------------------------------------- 
variables           = ['tp24']                # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
product             = 'forecast'              # hindcast or forecast ?
first_forecast_date = '20150611' # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 59        # number of forecast initializations  
season              = 'annual'
grid                = '0.25x0.25'             # '0.25x0.25' or '0.5x0.5'
domain              = 'southern_norway'
write2file          = True
# -----------------------------------------------------            

# get all dates for monday and thursday forecast initializations
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season)
print(forecast_dates)

for variable in variables:
    for date in forecast_dates:
        for dtype in ['cf','pf']:

            misc.tic()
            datestring = date.strftime('%Y-%m-%d')
            print('variable: ' + variable + ', date: ' + datestring + ', dtype: ' + dtype)
            
            forecastcycle = s2s.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
            basename      = '%s_%s_%s_%s'%(forecastcycle,grid,datestring,dtype)
                
            if variable == 'tp24': # daily accumulated precip (m)

                # files downloaded into different paths if before our after 2020
                if date >= datetime(2020,1,2):
                    path_in = config.dirs['s2s_' + product + '_6hourly'] + 'tp6/'
                else:
                    path_in = config.dirs['s2s_' + product + '_6hourly_student'] + 'tp6/'

                path_out                         = config.dirs['s2s_' + product + '_daily_student'] + variable + '/'
                filename_in                      = 'tp6_' + basename + '.nc'
                filename_out                     = variable + '_' + basename + '.nc'
                ds                               = xr.open_dataset(path_in + filename_in)

                # extract domain
                dim = verify.get_data_dimensions(grid, 'daily', domain)
                ds  = ds.sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')

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

        if write2file:
            
            print('combine cf and pf files into one file..')
            basename_cf     = '%s_%s_%s_%s'%(forecastcycle,grid,datestring,'cf')
            basename_pf     = '%s_%s_%s_%s'%(forecastcycle,grid,datestring,'pf')
            basename        = '%s_%s'%(grid,datestring) 
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



