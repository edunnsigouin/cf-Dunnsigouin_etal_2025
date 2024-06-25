"""
Preprocesses era5 continuous data for use by NHH masters students.
Extracts data by city.
"""

import numpy          as np
import xarray         as xr
from dask.diagnostics import ProgressBar
from forsikring       import misc,s2s,config,verify

# INPUT -----------------------------------------------
variable            = 'tp24'              # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
years               = np.arange(1960,2023,1)
grid                = '0.25x0.25'          # '0.25x0.25' & '0.5x0.5'
domain              = 'bergen'
write2file          = True
# -----------------------------------------------------

# define stuff  
path_in           = config.dirs['era5_daily'] + variable + '/' 
path_out          = config.dirs['era5_daily_student'] + variable + '/' 
filename_in       = [path_in + variable + '_' + grid + '_' + str(year) + '.nc' for year in years]
filename_out      = path_out + 'continuous_observation_' + variable + '_' + domain + '_' + grid + '_' + str(years[0]) + '-' + str(years[-1]) + '.nc'

# read daily forecast data 
data = xr.open_mfdataset(filename_in)

# extract domain
dim  = verify.get_data_dimensions(grid, 'daily', domain)
data = data.sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')[variable] 

# calculate explicitely 
with ProgressBar(): data = data.compute()

if write2file: misc.to_netcdf_with_packing_and_compression(data, filename_out)

data.close()

