"""
Calculates smoothed climatology per xy grid point from era5 
s2s hindcast format data.
"""

import numpy               as np
import xarray              as xr
from Dunnsigouin_etal_2025 import misc,s2s,config,verify
import os

# input ----------------------------------------------
time_flag            = 'daily'
variable             = 't2m24'             # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
first_forecast_date  = '20210104'            # first initialization date of forecast (either a monday or thursday)   
number_forecasts     = 104                     # number of forecast initializations 
season               = 'annual'
grid                 = '0.5x0.5'         # '0.25x0.25' or '0.5x0.5'
box_sizes            = np.arange(1,61,2)        # smoothing box size in grid points per side. Must be odd!   
write2file           = True
# ----------------------------------------------------

# get all dates for monday and thursday forecast initializations
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')
print(forecast_dates)

for date in forecast_dates:
        
    misc.tic()
    print('\ncalculating smoothed climatology for era5 hindcast format data initialized ' + date + ' and grid: ' + grid)
        
    # define stuff
    path_in         = config.dirs['era5_hindcast_daily'] + variable + '/'
    path_out        = config.dirs['era5_hindcast_' + time_flag + '_climatology'] + variable + '/'
    filename_in     = variable + '_' + grid + '_' + date + '.nc'
    filename_out    = variable + '_' + grid + '_' + date + '.nc'

    # read in data
    da = xr.open_dataset(path_in + filename_in)[variable]

    # calculate climatological mean 
    da = da.mean(dim='hdate')

    # convert time to weekly if applicable
    da = verify.resample_daily_to_weekly(da, time_flag, grid)

    # smooth                                                                                                                                              
    da_smooth = verify.boxcar_smoother_xy_optimized(box_sizes, da, 'xarray')
    
    # modify metadata
    da_smooth = da_smooth.rename(variable)
    if variable == 'tp24':
        da.attrs['units']     = 'm'
        da.attrs['long_name'] = 'climatological mean daily accumulated precipitation'
    elif variable == 't2m24':
        da.attrs['units']     = 'K'
        da.attrs['long_name'] = 'climatological mean daily-mean 2-meter temperature'
    elif variable == 'rn24':
        da.attrs['units']     = 'm'
        da.attrs['long_name'] = 'climatological mean daily accumulated rainfall'
    elif variable == 'mx24tpr':
        da.attrs['units']     = 'kg m**-2 s**-1'
        da.attrs['long_name'] = 'climatological mean daily maximum timestep precipitation rate'
    elif variable == 'mx24tp6':
        da.attrs['units']     = 'm'
        da.attrs['long_name'] = 'climatological mean daily maximum 6 hour accumulated precipitation'
    elif variable == 'mx24rn6':
        da.attrs['units']     = 'm'
        da.attrs['long_name'] = 'climatological mean daily maximum 6 hour accumulated rainfall'

    if write2file: misc.to_netcdf_with_packing_and_compression(da_smooth, path_out + filename_out)

    da.close()
    da_smooth.close()

    misc.toc()

