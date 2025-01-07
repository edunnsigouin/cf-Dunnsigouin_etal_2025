"""
Converts era5 forecast format data into binary if greater or smaller 
than a quantile threshold calculated from its corresponding hindcast
format data
"""

import xarray   as xr
import numpy    as np
import pandas   as pd
from forsikring import config,misc,s2s, verify


def initialize_quantile_array(variable,box_sizes,time_flag,dim):
    """ 
    Initializes output array used below.
    Written here to clean up code. 
    """

    # hack. need to fix.
    if time_flag == 'daily': time = dim.time
    elif time_flag == 'weekly': time = dim.timescale

    data       = np.zeros((box_sizes.size,time.size,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims       = ["box_size","time","latitude","longitude"]
    coords     = dict(box_size=box_sizes,time=time,latitude=dim.latitude,longitude=dim.longitude)

    if variable == 't2m24':
        units       = 'K'
        description = 'climatological quantiles of daily-mean 2-meter temperature'
    elif variable == 'tp24':
        units       = 'm'
        description = 'climatological quantiles of daily accumulated precipitation'

    attrs      = dict(description=description,units=units)
    name       = 'quantile'
    return xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)


# input ----------------------------------------------
time_flag           = 'daily'                   # daily or weekly
variable            = 'tp24'                  # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
first_forecast_date = '20200102'               # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 313                        # number of forecast initializations
season              = 'annual'
grid                = '0.25x0.25'              # '0.25x0.25' or '0.5x0.5'
pval                = 0.9                      # percentile values
domain              = 'scandinavia'
box_sizes           = np.arange(1,61,2)        # smoothing box size in grid points per side. Must be odd!
write2file          = True
# ----------------------------------------------------

forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d').values
#forecast_dates = pd.date_range(first_forecast_date, periods=number_forecasts).strftime('%Y-%m-%d')
print(forecast_dates)

for date in forecast_dates:

    misc.tic()
    print('\n ' + variable + ', ' + grid + ', ' + date)

    # define stuff                                                                                                                                                         
    path_in_forecast     = config.dirs['era5_forecast_daily'] + variable + '/'
    path_in_hindcast     = config.dirs['era5_hindcast_daily'] + variable + '/'
    path_out             = config.dirs['era5_forecast_' + time_flag + '_binary'] + str(pval) + '/' + domain + '/' + variable + '/'
    filename_in_forecast = variable + '_' + grid + '_' + date + '.nc'
    filename_in_hindcast = variable + '_' + grid + '_' + date + '.nc'
    filename_out         = variable + '_' + grid + '_' + date + '.nc'

    # read data
    dim      = verify.get_data_dimensions(grid, time_flag, domain)
    forecast = xr.open_dataset(path_in_forecast + filename_in_forecast).sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')[variable]
    hindcast = xr.open_dataset(path_in_hindcast + filename_in_hindcast).sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')[variable]

    # convert time to weekly if applicable     
    forecast = verify.resample_daily_to_weekly(forecast, time_flag, grid, variable)
    hindcast = verify.resample_daily_to_weekly(hindcast, time_flag, grid, variable)
    
    # spatial smoothing 
    forecast_smooth = verify.boxcar_smoother_xy_optimized(box_sizes, forecast, 'xarray')
    hindcast_smooth = verify.boxcar_smoother_xy_optimized(box_sizes, hindcast, 'numpy')

    # calculate quantiles - use numpy arrays for speed
    quantile            = initialize_quantile_array(variable,box_sizes,time_flag,dim)
    quantile[:,:,:,:]   = np.quantile(hindcast_smooth,pval,axis=1)
    quantile['time']    = forecast['time'] # match time dimensions    

    # convert to binary
    if pval > 0.5: binary = forecast_smooth.where(forecast_smooth < quantile, 1.0).where(forecast_smooth >= quantile, 0.0)   
    elif pval <= 0.5: binary = forecast_smooth.where(forecast_smooth > quantile, 1.0).where(forecast_smooth <= quantile, 0.0)
    
    # fix metadata
    binary = binary.rename(variable)
    if variable == 'tp24':
        binary.attrs['units']     = 'unitless'
        binary.attrs['long_name'] = 'binary daily accumulated precipitation over quantile pval'
    elif variable == 't2m24':
        binary.attrs['units']     = 'unitless'
        binary.attrs['long_name'] = 'binary daily-mean temperature over quantile pval'
    elif variable == 'rn24':
        binary.attrs['units']     = 'unitless'
        binary.attrs['long_name'] = 'binary daily accumulated rain over quantile pval'

    if write2file: misc.to_netcdf_with_packing_and_compression(binary, path_out + filename_out)
    
    forecast.close()
    hindcast.close()
    quantile.close()
    forecast_smooth.close()
    binary.close()

    misc.toc()
