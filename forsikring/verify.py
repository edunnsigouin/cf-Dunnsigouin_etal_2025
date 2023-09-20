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
    #smooth = np.zeros((box_sizes.size,) + da.shape)

    smooth_values = np.zeros((box_sizes.size,) + da.shape)
    coords        = {'box_size': box_sizes, **da.coords}
    dims          = ['box_size'] + list(da.dims)
    smooth        = xr.DataArray(smooth_values, coords=coords, dims=dims)
    
    for i, n in enumerate(box_sizes):
        if n % 2 != 0:  # odd
            # Create kernel with the same number of dimensions as da
            kernel_shape     = [1] * len(da.dims)
            kernel_shape[-2] = kernel_shape[-1] = n
            kernel           = np.ones(kernel_shape) / (n**2)
            # smooth
            smooth[i, ...] = ndimage.convolve(da.values, kernel, mode='constant', cval=0.0)
        else:  # even
            smooth[i, ...] = np.nan
    
    return smooth


def calc_fss_bootstrap(fss,fss_bootstrap,reference_error,forecast_error,number_shuffle_bootstrap,number_sample_bootstrap,forecast_dates,box_sizes):
    """
    calculates fractions skill score and generates bootstrapped estimates by boostrapping
    subsampling the forecasts/mse_forecasts
    """

    forecast_dates_index  = np.arange(0,forecast_dates.size)
    forecast_dates_random = forecast_dates_index.copy()
    reference_mse         = (1/forecast_dates.size)*reference_error.sum(dim='forecast_dates').values
    forecast_mse          = (1/forecast_dates.size)*forecast_error.sum(dim='forecast_dates').values
    for i in range(number_shuffle_bootstrap):
        # calc mean square error of forecast       
        forecast_mse_bootstrap = (1/forecast_dates_random.size)*forecast_error.sel(forecast_dates=forecast_dates_random).sum(dim='forecast_dates').values
        # calc fss
        for n in range(0,box_sizes.size,1):
            if box_sizes[n] % 2 != 0: # odd
                fss[n,:]             = 1.0 - forecast_mse[n,:]/reference_mse[n,:]
                fss_bootstrap[n,:,i] = 1.0 - forecast_mse_bootstrap[n,:]/reference_mse[n,:]
            else: # even
                fss_bootstrap[n,:,i] = np.nan
                fss[n,:]             = np.nan
        # shuffle forecasts dates randomly with replacement
        forecast_dates_random = np.random.choice(forecast_dates_index,number_sample_bootstrap,replace='True')    
    return fss,fss_bootstrap



def calc_fss_bootstrap(reference_error, forecast_error, number_shuffle_bootstrap, number_sample_bootstrap, box_sizes):
    """ 
    Calculates fractions skill score and generates bootstrapped estimates by boostrapping 
    subsampling the forecasts/mse_forecasts                                                                           
    """

    number_forecasts = len(reference_error['forecast_dates'])
    
    # Compute the MSE
    reference_mse = reference_error.mean(dim='forecast_dates')
    forecast_mse = forecast_error.mean(dim='forecast_dates')
    
    # Initialize results arrays
    fss           = np.empty((len(box_sizes), forecast_mse.time.size))
    fss_bootstrap = np.empty((len(box_sizes), forecast_mse.time.size, number_shuffle_bootstrap))

    # compute fss without bootstrap
    fss[:,:] = 1.0 - forecast_mse / reference_mse
    
    # compute fss with bootstrap
    for i in range(number_shuffle_bootstrap):
        
        # subsample forecast dates with replacement
        sampled_indices        = np.random.choice(number_forecasts, number_sample_bootstrap, replace=True)
        
        # bootstrap forecast mse
        forecast_mse_bootstrap = forecast_error.isel(forecast_dates=sampled_indices).mean(dim='forecast_dates')
        fss_bootstrap[:,:,i]   = 1.0 - forecast_mse_bootstrap / reference_mse

    return fss, fss_bootstrap


def time_2_timescale(ds,time_flag,datetime64):
    """
    resamples daily time into timescales following
    Wheeler et al. 2016 QJRMS. For exmaple, 1d1d,2d2d etc..
    Not exactly same since hr to lr data occurs on day 15 not 14.
    """
    if time_flag == 'timescale':
        
        if datetime64: # keep time dimension as datetime64
            time = ds.time.values
            if ds.time.size == 15:
                temp1      = ds.isel(time=1).drop_vars('time')
                temp2      = ds.isel(time=slice(2,3)).mean(dim='time')
                temp3      = ds.isel(time=slice(4,7)).mean(dim='time')
                temp4      = ds.isel(time=slice(7,13)).mean(dim='time')
                ds         = xr.concat([temp1,temp2,temp3,temp4],"time")
                ds['time'] = np.array([time[1],time[2],time[4],time[7]],dtype='datetime64[ns]')
            elif ds.time.size == 31:
                temp1      = ds.isel(time=slice(0,12)).mean(dim='time')
                temp2      = ds.isel(time=slice(13,31)).mean(dim='time')
                ds         = xr.concat([temp1,temp2],"time")
                ds['time'] = np.array([time[0],time[13]],dtype='datetime64[ns]')

        else: # convert time dimension to integers starting at 1
            if ds.time.size == 15:
                temp1      = ds.sel(time=2).drop_vars('time')
                temp2      = ds.sel(time=slice(3,4)).mean(dim='time')
                temp3      = ds.sel(time=slice(5,8)).mean(dim='time')
                temp4      = ds.sel(time=slice(8,14)).mean(dim='time')
                ds         = xr.concat([temp1,temp2,temp3,temp4],"time")
                ds['time'] = np.arange(1,5,1) 
            elif ds.time.size == 31:
                temp1      = ds.sel(time=slice(16,28)).mean(dim='time')
                temp2      = ds.sel(time=slice(29,46)).mean(dim='time')
                ds         = xr.concat([temp1,temp2],"time")
                ds['time'] = np.arange(1,3,1)
    return ds


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


def initialize_fss_array(dim,box_sizes,number_shuffle_bootstrap):
    """
    Initializes fss arrays.
    Written here to clean up code. 
    """
    data             = np.zeros((box_sizes.size,dim.ntime),dtype=np.float32)
    data_bootstrap   = np.zeros((box_sizes.size,dim.ntime,number_shuffle_bootstrap),dtype=np.float32)
    dims             = ["box_size","time"]
    dims_bootstrap   = ["box_size","time","number_shuffle_bootstrap"]
    coords           = dict(box_size=box_sizes,time=dim.time)
    coords_bootstrap = dict(box_size=box_sizes,time=dim.time,number_shuffle_bootstrap=np.arange(0,number_shuffle_bootstrap,1))
    attrs            = dict(description='fractions skill score of forecast',units='unitless')
    attrs_bootstrap  = dict(description='fractions skill score of forecast bootstrapped',units='unitless')
    name             = 'fss'
    name_bootstrap   = 'fss_bootstrap'
    fss              = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    fss_bootstrap    = xr.DataArray(data=data_bootstrap,dims=dims_bootstrap,coords=coords_bootstrap,attrs=attrs_bootstrap,name=name_bootstrap)
    return fss,fss_bootstrap


