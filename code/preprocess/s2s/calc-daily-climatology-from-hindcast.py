"""
Calculates smoothed climatology per xy grid point 
from ecmwf hindcast data
"""

import numpy           as np
import xarray          as xr
from forsikring        import misc,s2s,config,verify
import os

# input ----------------------------------------------
variable             = 't2m24'                  # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
first_forecast_date  = '20210104'              # first initialization date of forecast (either a monday or thursday)   
number_forecasts     = 1                     # number of forecast initializations 
season               = 'annual'
grid                 = '0.25x0.25' # '0.25x0.25' or '0.5x0.5'
box_sizes            = np.arange(1,61,2)        # smoothing box size in grid points per side. Must be odd!
write2file           = True
# ----------------------------------------------------

# get all dates for monday and thursday forecast initializations
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')
print(forecast_dates)

for date in forecast_dates:
        
    misc.tic()
    print('\ncalculating climatology for hindcast ' + date + ' and grid: ' + grid)
        
    # define stuff
    dim             = misc.get_dim(grid,'time')
    path_in         = config.dirs['s2s_hindcast_daily'] + variable + '/'
    path_out        = config.dirs['s2s_hindcast_climatology'] + variable + '/'
    filename_in     = variable + '_' + grid + '_' + date + '.nc'
    filename_out    = 'climatology_' + variable + '_' + grid + '_' + date + '.nc'

    # read in data
    da = xr.open_dataset(path_in + filename_in)[variable]

    # calculate climatological and ensemble mean
    da = da.mean(dim='hdate').mean(dim='number')

    # smooth
    da_smooth = verify.boxcar_smoother_xy_optimized(box_sizes, da, 'xarray')

    print(da_smooth)
    # modify metadata
    if variable == 'tp24':
        da_smooth.attrs['units']     = 'm'
        da_smooth.attrs['long_name'] = 'climatological and ensemble mean daily accumulated precipitation'
    elif variable == 't2m24':
        da_smooth.attrs['units']     = 'K'
        da_smooth.attrs['long_name'] = 'climatological and ensemble mean daily-mean 2-meter temperature'
    elif variable == 'rn24':
        da_smooth.attrs['units']     = 'm'
        da_smooth.attrs['long_name'] = 'climatological and ensemble mean daily accumulated rainfall'
    elif variable == 'mx24tpr':
        da_smooth.attrs['units']     = 'kg m**-2 s**-1'
        da_smooth.attrs['long_name'] = 'climatological and ensemble mean daily maximum timestep precipitation rate'
    elif variable == 'mx24tp6':
        da_smooth.attrs['units']     = 'm'
        da_smooth.attrs['long_name'] = 'climatological and ensemble mean daily maximum 6 hour accumulated precipitation'
    elif variable == 'mx24rn6':
        da_smooth.attrs['units']     = 'm'
        da_smooth.attrs['long_name'] = 'climatological and ensemble mean daily maximum 6 hour accumulated rainfall'
        
    if write2file: misc.to_netcdf_with_packing_and_compression(da_smooth, path_out + filename_out)

    da.close()
    da_smooth.close()
    
    misc.toc()

