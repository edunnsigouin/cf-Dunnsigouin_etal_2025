"""
Performs a spatial (x,y) smoothing on a range of spatial scales
of daily forecast/hindcast data and outputs the smoothed forecast 
fields to file.
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
from Dunnsigouin_etal_2025 import s2s, verify, misc, config

# Input -----------------------------------
variables           = ['tp24']                  # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
first_forecast_date = '20230807'               # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 1                      # number of forecasts
season              = 'annual'
grids               = ['0.25x0.25']            # '0.25x0.25' & '0.5x0.5'
box_sizes           = np.arange(1,61,2)        # smoothing box size in grid points per side. Must be odd! 
write2file          = False
# -----------------------------------------

misc.tic()

# define stuff 
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d').values
#forecast_dates = pd.date_range(first_forecast_date, periods=1).strftime('%Y-%m-%d').values     
print(forecast_dates)

for variable in variables:
    for grid in grids:
        for date in forecast_dates:
            
            print('\nsmoothing forecast ' + variable + ' for ' + date + ' and grid ' + grid)

            # define stuff
            path_in      = config.dirs['era5_forecast_daily'] + variable + '/'
            path_out     = config.dirs['era5_forecast_daily_smooth'] + variable + '/'
            filename_in  = variable + '_' + grid + '_' + date + '.nc'
            filename_out = variable + '_' + grid + '_' + date + '.nc'

            # read data
            da = xr.open_dataset(path_in + filename_in)[variable]

            # smooth
            da_smooth = verify.boxcar_smoother_xy_optimized(box_sizes, da, 'xarray')

            # modify metadata
            da_smooth = da_smooth.rename(variable)
            if variable == 'tp24':
                da_smooth.attrs['units']     = 'm'
                da_smooth.attrs['long_name'] = 'daily accumulated precipitation'
            elif variable == 't2m24':
                da_smooth.attrs['units']     = 'K'
                da_smooth.attrs['long_name'] = 'daily mean 2m-temperature'

            # write output 
            if write2file: misc.to_netcdf_with_packing_and_compression(da_smooth, path_out + filename_out)
            
            da.close()
            da_smooth.close()
                
misc.toc()
