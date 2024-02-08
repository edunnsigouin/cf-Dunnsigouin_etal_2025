"""
Collection of miscellaneous functions + look up dictionaries 
for ecmwf s2s model data 
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
import os
from datetime   import datetime
from scipy      import signal, ndimage
from forsikring  import misc



def boxcar_smoother_xy_optimized(box_sizes, da, output_type):
    """
    Smooths an array in xy using a boxcar smoother where the last two
    dimensions are latitude & longitude.
    Note: only performs calculation on odd sized box sizes (e.g., 1,3,5,...)
    where the size refers to the number of grid points per side of a square.  
    """
    # Ensure that the input is an xarray DataArray
    if not isinstance(da, xr.DataArray):
        raise ValueError("Input 'da' must be an xarray DataArray")

    # Check if the last two dimensions are latitude and longitude
    if (da.dims[-2], da.dims[-1]) != ('latitude', 'longitude'):
        raise ValueError("The last two dimensions of 'da' must be 'latitude' and 'longitude'")

    # Initialize output array
    smooth_values = np.full((len(box_sizes),) + da.shape, np.nan, dtype='float32')
    coords        = {'box_size': box_sizes, **da.coords}
    dims          = ['box_size'] + list(da.dims)
    
    # Apply the uniform filter for each box size
    for i, size in enumerate(box_sizes):
        if size % 2 != 0:  # Ensure the box size is odd
            filter_size           = [1] * (da.ndim - 2) + [size, size]
            smooth_values[i, ...] =  ndimage.uniform_filter(da, size=filter_size, mode='constant',cval=0.0)

    # Create the DataArray if desired. Else, remains numpy array
    if output_type == 'xarray':
        return xr.DataArray(smooth_values, coords=coords, dims=dims)
    elif output_type == 'numpy':
        return smooth_values
    

def boxcar_smoother_xy(box_sizes,da):
    """
    Smooths an array in xy using a boxcar smoother where the last two 
    dimensions are latitude & longitude.
    Note: only performs calculation on odd sized box sizes (e.g., 1,3,5,...)
    where the size refers to the number of grid points per side of a square.
    """
    # Ensure that the input is an xarray DataArray
    if not isinstance(da, xr.DataArray):
        raise ValueError("Input 'da' must be an xarray DataArray")

    # Check if the last two dimensions are latitude and longitude
    if (da.dims[-2], da.dims[-1]) != ('latitude', 'longitude'):
        raise ValueError("The last two dimensions of 'da' must be 'latitude' and 'longitude'")

    # initialize output array
    smooth_values = np.zeros((box_sizes.size,) + da.shape)
    coords        = {'box_size': box_sizes, **da.coords}
    dims          = ['box_size'] + list(da.dims)
    smooth        = xr.DataArray(smooth_values, coords=coords, dims=dims)

    # NOTE about loop below: when doing calculation for high res data (0.25x0.25),
    # all box sizes are odd numbered. But with low res data (0.5x0.5),
    # half the box sizes are even and only the odd ones are used for smoothing.
    # This is so that the dimension box_size is the same for both resolutions and
    # the odd box_sizes are those that correspond to the box sizes at high resolution.
    for i, n in enumerate(box_sizes):
        if n % 2 != 0:  # odd
            print(n)
            # Create kernel with the same number of dimensions as da
            kernel_shape     = [1] * len(da.dims)
            kernel_shape[-2] = kernel_shape[-1] = n
            kernel           = np.ones(kernel_shape) / (n**2)
            # smooth
            smooth[i, ...] = ndimage.convolve(da.values, kernel, mode='constant', cval=0.0)
        else: # even
            smooth[i, ...] = np.nan
    
    return smooth



def calc_score_bootstrap(reference_error, forecast_error, number_shuffle_bootstrap, box_sizes):
    """ 
    Calculates skill score and generates bootstrapped estimates by boostrapping 
    subsampling the forecast error term in the skill score.
    """

    number_forecasts = len(reference_error['forecast_dates'])
    
    # Compute the MSE
    reference_mse = reference_error.mean(dim='forecast_dates')
    forecast_mse = forecast_error.mean(dim='forecast_dates')
    
    # Initialize results arrays
    score           = np.empty((len(box_sizes), forecast_mse.time.size))
    score_bootstrap = np.empty((len(box_sizes), forecast_mse.time.size, number_shuffle_bootstrap))

    # compute score without bootstrap
    score[:,:] = 1.0 - forecast_mse / reference_mse
    
    # compute score with bootstrap
    for i in range(number_shuffle_bootstrap):
        
        # subsample forecast dates with replacement
        sampled_indices = np.random.choice(number_forecasts, number_forecasts, replace=True)
        
        # bootstrap forecast mse
        forecast_mse_bootstrap = forecast_error.isel(forecast_dates=sampled_indices).mean(dim='forecast_dates')
        score_bootstrap[:,:,i] = 1.0 - forecast_mse_bootstrap / reference_mse

    return score, score_bootstrap


def calc_score_bootstrap_xy(reference_error, forecast_error, number_shuffle_bootstrap):
    """
    Calculates skill score and generates bootstrapped estimates by boostrapping
    subsampling the forecast error term in the skill score.
    """

    number_forecasts = len(reference_error['forecast_dates'])

    # Compute the MSE
    reference_mse = reference_error.mean(dim='forecast_dates')
    forecast_mse = forecast_error.mean(dim='forecast_dates')

    # Initialize results arrays
    latitude        = forecast_error.latitude
    longitude       = forecast_error.longitude
    score           = np.empty((latitude.size,longitude.size))
    score_bootstrap = np.empty((number_shuffle_bootstrap,latitude.size,longitude.size))

    # compute score without bootstrap
    score[:,:] = 1.0 - forecast_mse / reference_mse

    # compute score with bootstrap
    for i in range(number_shuffle_bootstrap):

        # subsample forecast dates with replacement
        sampled_indices = np.random.choice(number_forecasts, number_forecasts, replace=True)

        # bootstrap forecast mse
        forecast_mse_bootstrap   = forecast_error.isel(forecast_dates=sampled_indices).mean(dim='forecast_dates')
        score_bootstrap[i, ...]  = 1.0 - forecast_mse_bootstrap / reference_mse

    return score, score_bootstrap



def calc_score_bootstrap_difference(reference_error1, reference_error2, forecast_error1, forecast_error2, number_shuffle_bootstrap, box_sizes):
    """
    Calculates skill scores for two sets of forecast and reference errors.
    Generates bootstrapped estimates of the DIFFERENCE in the fss values by bootsrapping
    the subsampled forecast_errors. 
    """

    # forecasts number can be different. Choose smallest amount for simplicity.
    number_forecasts = min(len(reference_error1['forecast_dates']),len(reference_error2['forecast_dates']))
    
    # Compute the MSE                                                                                                                                                   
    reference_mse1 = reference_error1.mean(dim='forecast_dates')
    reference_mse2 = reference_error2.mean(dim='forecast_dates')
    forecast_mse1  = forecast_error1.mean(dim='forecast_dates')
    forecast_mse2  = forecast_error2.mean(dim='forecast_dates')
    
    # Initialize results arrays
    score_difference           = np.empty((len(box_sizes), forecast_mse1.time.size))
    score_bootstrap_difference = np.empty((len(box_sizes), forecast_mse1.time.size, number_shuffle_bootstrap))
    
    # compute score without bootstrap
    score_difference[:,:] = (1.0 - forecast_mse1 / reference_mse1) - (1.0 - forecast_mse2 / reference_mse2)

    # compute score with bootstrap
    for i in range(number_shuffle_bootstrap):

        # subsample forecast dates with replacement
        sampled_indices = np.random.choice(number_forecasts, number_forecasts, replace=True)

        # bootstrap forecast mse
        forecast_mse_bootstrap1           = forecast_error1.isel(forecast_dates=sampled_indices).mean(dim='forecast_dates')
        forecast_mse_bootstrap2           = forecast_error2.isel(forecast_dates=sampled_indices).mean(dim='forecast_dates')
        score_bootstrap_difference[:,:,i] = (1.0 - forecast_mse_bootstrap1 / reference_mse1) - (1.0 - forecast_mse_bootstrap2 / reference_mse2)

    return score_difference, score_bootstrap_difference



def resample_daily_to_weekly(ds, time_flag, grid, variable):
    """
    Resamples daily time dimension into weekly 
    """
    def resample_days(ds,grid):
        original_dims = ds.dims
        if ((grid == '0.25x0.25') and (variable == 'tp24')):
            ds_resampled = xr.concat([
                ds.isel(time=slice(0, 7)).sum(dim='time'), # accumulated precip
                ds.isel(time=slice(7, 14)).sum(dim='time'),
            ], "time")
            ds_resampled['time'] = np.arange(1, 3, 1)
        elif ((grid == '0.25x0.25') and (variable == 't2m24')):
            ds_resampled = xr.concat([
                ds.isel(time=slice(0, 7)).mean(dim='time'), # mean temp
                ds.isel(time=slice(7, 14)).mean(dim='time'),
            ], "time")
            ds_resampled['time'] = np.arange(1, 3, 1)
        elif ((grid == '0.5x0.5') and (variable == 'tp24')):
            ds_resampled = xr.concat([
                ds.isel(time=slice(0, 6)).sum(dim='time'),
                ds.isel(time=slice(6, 13)).sum(dim='time'),
                ds.isel(time=slice(13, 20)).sum(dim='time'),
                ds.isel(time=slice(20, 27)).sum(dim='time'),
            ], "time")
            ds_resampled['time'] = np.arange(3, 7, 1)
        elif ((grid == '0.5x0.5') and (variable == 't2m24')):
            ds_resampled = xr.concat([
                ds.isel(time=slice(0, 6)).mean(dim='time'),
                ds.isel(time=slice(6, 13)).mean(dim='time'),
                ds.isel(time=slice(13, 20)).mean(dim='time'),
                ds.isel(time=slice(20, 27)).mean(dim='time'),
            ], "time")
            ds_resampled['time'] = np.arange(3, 7, 1)
            
        return ds_resampled.transpose(*original_dims)
    
    if time_flag != 'weekly':
        return ds
    elif (grid == '0.25x0.25') or (grid == '0.5x0.5'):
        return resample_days(ds,grid)
    else:
        raise ValueError(f"Unsupported grid: {grid}")



    
def resample_time_to_timescale(ds, time_flag):
    """Resamples daily time into timescales following Wheeler et al. 2016 QJRMS.
    Adjusted for hr to lr data occurring on day 15 not 14."""

    def resample_31_days(ds):
        """
        Resamples dataset time dimension with 31 days to timescales.
        """
        # Store the original dimension order
        original_dims = ds.dims

        ds_resampled = xr.concat([
            ds.isel(time=slice(0, 12)).mean(dim='time'),
            ds.isel(time=slice(13, 31)).mean(dim='time')
        ], "time")

        ds_resampled['time'] = np.arange(5, 7, 1)
        return ds_resampled.transpose(*original_dims) # keeps original dimension order

    def resample_15_days(ds):
        """
        Resamples dataset time dimension with 15 days to timescales.
        """
        # Store the original dimension order
        original_dims = ds.dims

        slices = [
            ds.isel(time=1).drop_vars('time'),
            ds.isel(time=slice(2, 3)).mean(dim='time'),
            ds.isel(time=slice(4, 7)).mean(dim='time'),
            ds.isel(time=slice(7, 13)).mean(dim='time'),
        ]

        ds_resampled         = xr.concat(slices, "time")
        ds_resampled['time'] = np.arange(1, 5, 1)
        return ds_resampled.transpose(*original_dims) # keeps original dimension order 
    
    if time_flag != 'timescale':
        return ds

    if ds.time.size == 15:
        return resample_15_days(ds)
    elif ds.time.size == 31:
        return resample_31_days(ds)
    else:
        raise ValueError(f"Unsupported time size: {ds.time.size}. Supported sizes are 15 or 31.")







    
def initialize_error_array(dim,box_sizes,forecast_dates):
    """
    Initializes error array.
    Written here to clean up code.
    """
    data   = np.zeros((forecast_dates.size,box_sizes.size,dim.ntime),dtype=np.float32)
    dims   = ["forecast_dates","box_size","time"]
    coords = dict(forecast_dates=np.arange(0,forecast_dates.size),box_size=box_sizes,time=dim.time)
    name   = 'error'
    error  = xr.DataArray(data=data,dims=dims,coords=coords,name=name)
    return error


def initialize_error_xy_array(dim,forecast_dates):
    """ 
    Initializes error array.
    Written here to clean up code.
    """
    data   = np.zeros((forecast_dates.size,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims   = ["forecast_dates","latitude","longitude"]
    coords = dict(forecast_dates=np.arange(0,forecast_dates.size),latitude=dim.latitude,longitude=dim.longitude)
    name   = 'error'
    error  = xr.DataArray(data=data,dims=dims,coords=coords,name=name)
    return error



def initialize_score_array(score_type,dim,box_sizes,number_shuffle_bootstrap):
    """
    Initializes score arrays.
    Written here to clean up code. 
    """
    data             = np.zeros((box_sizes.size,dim.ntime),dtype=np.float32)
    data_bootstrap   = np.zeros((box_sizes.size,dim.ntime,number_shuffle_bootstrap),dtype=np.float32)
    dims             = ["box_size","time"]
    dims_bootstrap   = ["box_size","time","number_shuffle_bootstrap"]
    coords           = dict(box_size=box_sizes,time=dim.time)
    coords_bootstrap = dict(box_size=box_sizes,time=dim.time,number_shuffle_bootstrap=np.arange(0,number_shuffle_bootstrap,1))
    if score_type == 'fss':
        attrs            = dict(description='fractions skill score of forecast',units='unitless')
        attrs_bootstrap  = dict(description='fractions skill score of forecast bootstrapped',units='unitless')
    elif score_type == 'fbss':
        attrs            = dict(description='fractions brier skill score of forecast',units='unitless')
        attrs_bootstrap  = dict(description='fractions brier skill score of forecast bootstrapped',units='unitless')
    name             = score_type
    name_bootstrap   = score_type + '_bootstrap'
    score            = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    score_bootstrap  = xr.DataArray(data=data_bootstrap,dims=dims_bootstrap,coords=coords_bootstrap,attrs=attrs_bootstrap,name=name_bootstrap)
    return score,score_bootstrap


def initialize_score_xy_array(score_type,dim,number_shuffle_bootstrap):
    """
    Initializes score arrays.
    Written here to clean up code.
    """
    data             = np.zeros((dim.nlatitude,dim.nlongitude),dtype=np.float32)
    data_bootstrap   = np.zeros((number_shuffle_bootstrap,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims             = ["latitude","longitude"]
    dims_bootstrap   = ["number_shuffle_bootstrap","latitude","longitude"]
    coords           = dict(latitude=dim.latitude,longitude=dim.longitude)
    coords_bootstrap = dict(number_shuffle_bootstrap=np.arange(0,number_shuffle_bootstrap,1),latitude=dim.latitude,longitude=dim.longitude)
    if score_type == 'fss':
        attrs            = dict(description='fractions skill score of forecast',units='unitless')
        attrs_bootstrap  = dict(description='fractions skill score of forecast bootstrapped',units='unitless')
    elif score_type == 'fbss':
        attrs            = dict(description='fractions brier skill score of forecast',units='unitless')
        attrs_bootstrap  = dict(description='fractions brier skill score of forecast bootstrapped',units='unitless')
    name             = score_type
    name_bootstrap   = score_type + '_bootstrap'
    score            = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    score_bootstrap  = xr.DataArray(data=data_bootstrap,dims=dims_bootstrap,coords=coords_bootstrap,attrs=attrs_bootstrap,name=name_bootstrap)
    return score,score_bootstrap



def match_box_sizes_high_to_low_resolution(grid,box_sizes):
    """
    Match neighborhood sizes between high (0.25x0.25 degree) and 
    low (0.5x0.5 degree) resolution data. For example, box size with 5 
    grid points per side in high res data is equivalent to 3 in low res
    data.
    Box_sizes for low res data ends up being the same length array,
    but has odd AND even values. The odd ones correspond to the high res
    box sizes. For example, high res box sizes [1,3,5,7] correspond to low
    res box sizes [1,2,3,4]. Here, only the odd numbered sizes are used in 
    the boxcar smoother (see function).
    """
    if grid == '0.5x0.5':
        box_sizes_lr = np.copy(np.ceil(box_sizes/2)).astype(int)
    else:
        box_sizes_lr = box_sizes
        
    return box_sizes_lr



def combine_high_and_low_res_files(filename_hr, filename_lr, filename, path, time_flag, write2file):

    hr_file_path  = path + filename_hr
    lr_file_path  = path + filename_lr
    out_file_path = path + filename

    if not os.path.exists(hr_file_path) or not os.path.exists(lr_file_path):
        print("Either the high-resolution or low-resolution file does not exist.")
        return

    if not write2file:
        print("Write to file is disabled. Exiting.")
        return

    try:
        print('Combining high & low-resolution files into one file...')
        with xr.open_dataset(hr_file_path) as ds_hr, xr.open_dataset(lr_file_path) as ds_lr:
            ds = xr.concat([ds_hr, ds_lr], 'time')
            misc.to_netcdf_with_packing_and_compression(ds, path + filename)
            
        print('Deleting original high and low-resolution files...')
        os.remove(hr_file_path)
        os.remove(lr_file_path)

    except Exception as e:
        print(f"An error occurred: {e}")


        
def get_data_dimensions(grid, time_flag, domain):
    dim = misc.get_dim(grid, time_flag)
    return misc.subselect_xy_domain_from_dim(dim, domain, grid)
        

def calc_forecast_and_reference_error(score_type, filename_verification, filename_forecast, variable, box_sizes_temp, pval=0.9):
    """
    calculates forecast and reference error for fractional skill score
    """
    # read data
    verification          = xr.open_dataset(filename_verification)[variable]
    forecast              = xr.open_dataset(filename_forecast)[variable]

    # calculate error terms
    if score_type == 'fss':
        forecast_error_xy  = (forecast - verification) ** 2
        reference_error_xy = (verification) ** 2
        
    elif score_type == 'fbss':
        if pval > 0.5: climatological_probability = 1 - pval # e.g. if 90th quantile, then probability is 10%
        elif pval < 0.5: climatological_probability = pval # if 10th quantile, then probability 10%
        forecast_error_xy  = (forecast - verification) ** 2
        reference_error_xy = (climatological_probability - verification) ** 2
    
    verification.close()
    forecast.close()

    return misc.xy_mean(forecast_error_xy).values, misc.xy_mean(reference_error_xy).values


def calc_forecast_and_reference_error_xy(score_type, filename_verification, filename_forecast, variable, box_size, lead_time, pval=0.9):
    """
    calculates forecast and reference error for fractional skill score
    """
    # read data 
    verification = xr.open_dataset(filename_verification)[variable].sel(box_size=box_size).isel(time=lead_time-1).squeeze()
    forecast     = xr.open_dataset(filename_forecast)[variable].sel(box_size=box_size).isel(time=lead_time-1).squeeze()
    
    # calculate error terms
    if score_type == 'fss':
        forecast_error_xy  = (forecast - verification) ** 2
        reference_error_xy = (verification) ** 2

    elif score_type == 'fbss':
        if pval > 0.5: climatological_probability = 1 - pval # e.g. if 90th quantile, then probability is 10%
        elif pval < 0.5: climatological_probability = pval # if 10th quantile, then probability 10%
        forecast_error_xy  = (forecast - verification) ** 2
        reference_error_xy = (climatological_probability - verification) ** 2

    verification.close()
    forecast.close()

    return forecast_error_xy.values, reference_error_xy.values



def write_score_to_file(score, score_bootstrap, forecast_error, reference_error, write2file, grid, box_sizes, time_flag, filename_out, path_out):
    """Kitchen sink function to write score and error to file""" 
    if write2file:
        forecast_error  = forecast_error.rename('forecast_error')
        reference_error = reference_error.rename('reference_error')
        ds              = xr.merge([score,score_bootstrap,forecast_error,reference_error])
        if grid == '0.5x0.5':
            ds['box_size'] = box_sizes
        if time_flag == 'timescale':
            ds = ds.rename({'time': 'timescale'})
        misc.to_netcdf_with_packing_and_compression(ds, path_out + filename_out)
        ds.close()
    return


def write_score_to_file_xy(score, sig, write2file, filename_out, path_out):
    """Kitchen sink function to write score and error to file"""
    if write2file:
        ds = xr.merge([score,sig])
        ds.to_netcdf(path_out + filename_out)
        #misc.to_netcdf_with_packing_and_compression(ds, path_out + filename_out)
        ds.close()
    return
