"""
Calculates the Mean-square-error statistic as a function of x,y and 
lead time for ecmwf forecasts, era5 climatology and era5 persistence
"""

import numpy  as np
import xarray as xr
from dask.diagnostics   import ProgressBar
from forsikring import config,misc,s2s

# INPUT -----------------------------------------------
data_flag        = 'ecmwf'                  # ecwmf,clim,pers
variables        = ['tp24']                 # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
mon_thu_start    = ['20210104','20210107']  # first monday & thursday initialization date of forecast
num_i_weeks      = 1                        # number of weeks withe forecasts
comp_lev         = 5
write2file       = False
# -----------------------------------------------------      

# get all dates for monday and thursday forecast initializations
dates_monday_thursday = s2s.get_monday_thursday_dates(mon_thu_start,num_i_weeks)

for variable in variables
    for date in dates_monday_thursday:

        datestring = date.strftime('%Y-%m-%d')
        print('\nvariable: ' + variable + ', date: ' + datestring)

        # define some paths and strings
        if data_flag == 'forecast':
            path_forecast        = config.dirs['forecast_daily'] + variable + '/'
            forcastcycle         = s2s.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
            filename_forecast_hr = variable + '_' + forcastcycle + '_0.25x0.25_' + datestring + '.nc'
            filename_forecast_lr = variable + '_' + forcastcycle + '_0.5x0.5_' + datestring + '.nc'
            
        filename_verification_hr = variable + '_0.25x0.25_' + datestring + '.nc'
        filename_verification_lr = variable + '_0.5x0.5_' + datestring + '.nc'
