"""
Converts ecmwf forecast format data into probability of ensemble members greater or smaller
than a quantile threshold calculated from its corresponding hindcast data.
"""

import numpy           as np
import xarray          as xr
from dask.diagnostics  import ProgressBar
from forsikring        import misc,s2s,config,verify
import os


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
        description = 'climatological quantiles of 2-meter temperature'
    elif variable == 'tp24':
        units       = 'm'
        description = 'climatological quantiles of daily accumulated precipitation'
        
    attrs      = dict(description=description,units=units)
    name       = 'quantile'
    return xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)


# input ----------------------------------------------
time_flag           = 'daily'                   # daily or weekly
variable            = 'tp24'                  # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
first_forecast_date = '20210104'               # first initialization date of forecast (either a monday or thursday)   
number_forecasts    = 104                        # number of forecast initializations 
season              = 'annual'
grid                = '0.5x0.5'              # '0.25x0.25' or '0.5x0.5'
box_sizes           = np.arange(1,61,2)        # smoothing box size in grid points per side. Must be odd!
pval                = 0.1                     # percentile value  
domain              = 'europe'
write2file          = True
# ----------------------------------------------------

# get all dates for monday and thursday forecast initializations
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d').values
dim            = misc.get_dim(grid,time_flag)
print(forecast_dates)

for date in forecast_dates:

    misc.tic()
    print('\n ' + variable + ', ' + grid + ', ' + date)
        
    # define stuff
    path_in_forecast     = config.dirs['s2s_forecast_daily'] + variable + '/'
    path_in_hindcast     = config.dirs['s2s_hindcast_daily'] + variable + '/'
    path_out             = config.dirs['s2s_forecast_' + time_flag + '_probability'] + str(pval) + '/' + domain + '/' + variable + '/'
    filename_in_forecast = variable + '_' + grid + '_' + date + '.nc'
    filename_in_hindcast = variable + '_' + grid + '_' + date + '.nc'
    filename_out         = variable + '_' + grid + '_' + date + '.nc'
    
    # read data 
    dim      = verify.get_data_dimensions(grid, time_flag, domain)
    forecast = xr.open_dataset(path_in_forecast + filename_in_forecast).sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')[variable]
    hindcast = xr.open_dataset(path_in_hindcast + filename_in_hindcast).sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')[variable]
    
    # convert time to weekly if applicable
    forecast = verify.resample_daily_to_weekly(forecast, time_flag, grid)
    hindcast = verify.resample_daily_to_weekly(hindcast, time_flag, grid)

    # spatial smoothing of forecast                                                                                                                                                       
    forecast_smooth = verify.boxcar_smoother_xy_optimized(box_sizes, forecast, 'xarray')

    # calculate quantiles.
    # loop through each hindcast smoothing size to reduce memory.
    quantile = initialize_quantile_array(variable,box_sizes,time_flag,dim)
    for bs, box_size in enumerate(box_sizes):
        print('box size = ' + str(box_size))
        hindcast_smooth      = verify.boxcar_smoother_xy_optimized(np.array([box_size]), hindcast, 'numpy').squeeze()
        dim_sizes            = hindcast_smooth.shape
        hindcast_smooth      = np.reshape(hindcast_smooth,[dim_sizes[0],dim_sizes[1]*dim_sizes[2],dim_sizes[3],dim_sizes[4]]) # concatenate hdate and number dims for sample
        quantile[bs,:,:,:]   = np.quantile(hindcast_smooth,pval,axis=1)
        quantile['time']     = forecast['time'] # match time dimensions
        
    # convert to probability (number of ensemble members > or < quantile)
    if pval > 0.5: probability = (forecast_smooth >= quantile).mean(dim='number')
    elif pval <= 0.5: probability = (forecast_smooth < quantile).mean(dim='number')

    # fix metadata
    probability = probability.rename(variable)
    if variable == 'tp24':
        probability.attrs['units']     = 'unitless'
        probability.attrs['long_name'] = 'probability of daily accumulated precipitation over quantile pval'
    elif variable == 't2m24':
        probability.attrs['units']     = 'unitless'
        probability.attrs['long_name'] = 'probability of daily-mean temperature over quantile pval'
    elif variable == 'rn24':
        probability.attrs['units']     = 'unitless'
        probability.attrs['long_name'] = 'probability of daily accumulated rain over quantile pval'

    if write2file: misc.to_netcdf_with_packing_and_compression(probability, path_out + filename_out)

    forecast_smooth.close()
    hindcast.close()
    forecast.close()
    probability.close()
    quantile.close()
    
    misc.toc()
    
