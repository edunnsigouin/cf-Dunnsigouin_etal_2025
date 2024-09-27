"""
Preprocesses era5 forecast format data for use by NHH masters students.
Extracts data by city.
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
first_forecast_date   = '20120102'          # first initialization date of forecast (either a monday or thursday) 
number_forecasts      = 1148                 # number of forecasts
season                = 'annual'
grid                  = '0.25x0.25'          # '0.25x0.25' & '0.5x0.5'
domain                = 'oslo'
write2file            = True
# -----------------------------------------------------

# get forecast dates 
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season)
print(forecast_dates)

forecast_dates = forecast_dates.delete(22) # missing forecast on 2012-03-19 
forecast_dates = forecast_dates.delete(357) # missing forecast on 2015-06-08 

# define stuff  
path_in           = config.dirs['era5_' + product + '_daily_student'] + variable + '/'
path_out          = config.dirs['era5_' + product + '_daily_student_combined']
filenames_in      = variable + '_' + grid + '_' + forecast_dates.strftime('%Y-%m-%d') + '.nc'
timestamp         = forecast_dates[0].strftime('%Y-%m-%d') + '_' + forecast_dates[-1].strftime('%Y-%m-%d')
filename_out      = 'observation_' + variable + '_' + domain + '_' + grid + '_' + timestamp  + '.nc' 

# extract domain 
dim = verify.get_data_dimensions(grid, 'daily', domain)

# read daily forecast data 
ds = xr.open_mfdataset(path_in + filenames_in,preprocess=preprocess,combine='nested',concat_dim='init_time').sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')

# calculate explicitely 
with ProgressBar(): ds = ds.compute()
    
# modify metadata - change time to lead-time and initialization date to time init
ds = ds.rename({'time':'lead_time'})
ds = ds.assign_coords({"init_time": forecast_dates})
            
# write2file two files into one
if write2file: misc.to_netcdf_with_packing_and_compression(ds, path_out + filename_out)

ds.close()

