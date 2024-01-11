"""
Preprocesses forecast data for use by NHH masters students.
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
product             = 'forecast'          # forecast or hindcast
variable            = 'tp24'              # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
first_forecast_date = '20200102'          # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 313                   # number of forecasts 
season              = 'annual'
grid                = '0.25x0.25'          # '0.25x0.25' & '0.5x0.5'
domain              = 'oslo'
write2file          = True
# -----------------------------------------------------

# get forecast dates 
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season)
print(forecast_dates)

# define stuff  
path_in           = config.dirs['s2s_' + product + '_daily'] + variable + '/' 
path_out          = config.dirs['s2s_' + product + '_daily_student'] + variable + '/' 
filename_in       = variable + '_' + grid + '_' + forecast_dates.strftime('%Y-%m-%d') + '.nc'
timestamp         = forecast_dates[0].strftime('%Y-%m-%d') + '_' + forecast_dates[-1].strftime('%Y-%m-%d')
filename_out      = 'forecast_' + variable + '_' + domain + '_' + grid + '_' + timestamp  + '.nc' 

# read daily forecast data 
data = xr.open_mfdataset(path_in + filename_in,preprocess=preprocess,combine='nested',concat_dim='init_time')

# extract domain
dim  = verify.get_data_dimensions(grid, 'daily', domain)
data = data.sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')[variable] 

# calculate explicitely 
with ProgressBar(): data = data.compute()

# modify metadata - change time to lead-time and initialization date to time init
data = data.rename({'time':'lead_time'})
data = data.assign_coords({"init_time": forecast_dates})

if write2file: misc.to_netcdf_with_packing_and_compression(data, path_out + filename_out)

data.close()

