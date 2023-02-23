"""
Creates era5 climatology files with same format as ecmwf forecast file.
example: tp24_CY47R1_0.25x0.25_2021-01-04.nc is the forecast file
and the new era5 clim file associated with this forecast is 
tp24_clim_0.25x0.25_2021-01-04.nc with dates corresponding
to climatological jan 04 to jan 04 + 46 days.

NOTE: climatology is calculated over available hindcast period: 2001-2020
and for simple calandar day mean climatology
"""

import numpy  as np
import xarray as xr
import pandas as pd
from dask.diagnostics   import ProgressBar
import os
from forsikring import config,misc,s2s

# INPUT -----------------------------------------------
variables        = ['tp24']             # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
years            = np.arange(2001,2021,1)  # years for climatology calculation
mon_thu_start    = ['20210104','20210107'] # first monday & thursday initialization date of forecast
num_i_weeks      = 52                      # number of weeks withe forecasts
grids            = ['0.25x0.25']          # '0.25x0.25' or '0.5x0.5'
comp_lev         = 5
write2file       = False
# -----------------------------------------------------         

# get all dates for monday and thursday forecast initializations
dates_monday_thursday = s2s.get_monday_thursday_dates(mon_thu_start,num_i_weeks)

for variable in variables:
    for grid in grids:
        
        # define stuff
        path_in  = config.dirs['era5_cont_daily'] + variable + '/'
        path_out = config.dirs['era5_model_clim'] + variable + '/'
    
        print('calculate climatology (excluding 2021)..')
        filenames = [path_in + variable + '_' + grid + '_' + str(years[0]) + '.nc']
        for year in years[1:]:
            filenames = filenames + [path_in + variable + '_' + grid + '_' + str(year) + '.nc']
            
        # is this the right way to calculate the climatology for this project?    
        with ProgressBar():
            ds_clim = xr.open_mfdataset(filenames).groupby('time.dayofyear').mean(dim='time').compute()
        ds_clim = ds_clim.drop_sel(dayofyear=366) # drop leap year day
        ds_clim = ds_clim.rename({'dayofyear':'time'}) 
    
        print('picking out dates corresponding to forecast/hindcast..')
        for date in dates_monday_thursday:

            datestring = date.strftime('%Y-%m-%d')
            print('\nvariable: ' + variable + ', date: ' + datestring,', grid: ' + grid)

            if grid == '0.25x0.25':
                era5_dates = pd.date_range(date,periods=15,freq="D").dayofyear.values
                ds         = ds_clim.sel(time=era5_dates)
                ds['time'] = pd.date_range(date,periods=15,freq="D") # make dates correspond to forecast for convenience later on
            elif grid == '0.5x0.5':
                era5_dates = (pd.date_range(date,periods=31,freq="D") + np.timedelta64(15,'D')).dayofyear.values
                ds         = ds_clim.sel(time=era5_dates)
                ds['time'] = pd.date_range(date,periods=31,freq="D") + np.timedelta64(15,'D') # make dates correspond to forecast for convenience later on
                
            if write2file:
                print('writing to file..')
                filename_out = '%s_%s_%s.nc'%(variable,grid,datestring)
                s2s.to_netcdf_pack64bit(ds[variable],path_out + filename_out)
                print('compress file to reduce space..')
                s2s.compress_file(comp_lev,3,filename_out,path_out)
                print('')

            ds.close()
        
        ds_clim.close()

