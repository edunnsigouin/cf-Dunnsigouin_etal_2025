"""
Preprocesses forecast data for use by NHH masters students.
Extracts data by city.

NOTE: here the data was downloaded on two different domains with the same grid.
One format for pre-2020 and another for post-2020. This code
combines them for a given city.
"""

import numpy          as np
import xarray         as xr
from dask.diagnostics import ProgressBar
from forsikring       import misc,s2s,config,verify

def preprocess(ds):
    '''change time dim from calendar dates to numbers'''
    if ds.time.size == 15:
        ds['time'] = np.arange(1,ds.time.size+1,1) # high resolution lead times
    elif ds.time.size == 31:
        ds['time'] = np.arange(16,47,1) # low resolution lead times  
    return ds

# INPUT -----------------------------------------------
product               = 'forecast'          # forecast or hindcast
variable              = 'tp24'              # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
first_forecast_date_1 = '20170102'          # first initialization date of forecast (either a monday or thursday) 
number_forecasts_1    = 313                   # number of forecasts
first_forecast_date_2 = '20200102'          # first initialization date of forecast (either a monday or thursday)
number_forecasts_2    = 313                   # number of forecasts 
season                = 'annual'
grid                  = '0.25x0.25'          # '0.25x0.25' & '0.5x0.5'
domain                = 'bergen'
write2file            = True
# -----------------------------------------------------

# get forecast dates 
forecast_dates_1 = s2s.get_forecast_dates(first_forecast_date_1,number_forecasts_1,season)
forecast_dates_2 = s2s.get_forecast_dates(first_forecast_date_2,number_forecasts_2,season)

# define stuff  
path_in_2           = config.dirs['s2s_' + product + '_daily'] + variable + '/' 
path_in_1           = config.dirs['s2s_' + product + '_daily_student'] + variable + '/'
filenames_in_1      = variable + '_' + grid + '_' + forecast_dates_1.strftime('%Y-%m-%d') + '.nc'
filenames_in_2      = variable + '_' + grid + '_' + forecast_dates_2.strftime('%Y-%m-%d') + '.nc'

timestamp         = forecast_dates_1[0].strftime('%Y-%m-%d') + '_' + forecast_dates_2[-1].strftime('%Y-%m-%d')
filename_out      = 'forecast_' + variable + '_' + domain + '_' + grid + '_' + timestamp  + '.nc' 
path_out          = config.dirs['s2s_' + product + '_daily_student_combined']

# read daily forecast data 
data1 = xr.open_mfdataset(path_in_1 + filenames_in_1,preprocess=preprocess,combine='nested',concat_dim='init_time')
data2 = xr.open_mfdataset(path_in_2 + filenames_in_2,preprocess=preprocess,combine='nested',concat_dim='init_time')

# extract domain
dim   = verify.get_data_dimensions(grid, 'daily', domain)
data1 = data1.sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')[variable] 
data2 = data2.sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')[variable]

# calculate explicitely 
with ProgressBar():
    data1 = data1.compute()
    data2 = data2.compute()
    
# modify metadata - change time to lead-time and initialization date to time init
data1 = data1.rename({'time':'lead_time'})
data2 = data2.rename({'time':'lead_time'})
data1 = data1.assign_coords({"init_time": forecast_dates_1})
data2 = data2.assign_coords({"init_time": forecast_dates_2})

# write2file two files into one
if write2file: misc.to_netcdf_with_packing_and_compression(xr.concat([data1,data2],dim='init_time'), path_out + filename_out)

data1.close()
data2.close()

