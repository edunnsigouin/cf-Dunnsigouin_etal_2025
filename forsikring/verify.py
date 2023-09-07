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


def boxcar_smoother_xy(NH, da):
    """
    Smooths an array in xy using a boxcar smoother where the last two 
    dimensions are latitude & longitude.
    Note: only performs calculation on odd sized neighborhood smoothings (e.g., 1, 9, 19, ..)
    """
    # Ensure that the input is an xarray DataArray
    if not isinstance(da, xr.DataArray):
        raise ValueError("Input 'da' must be an xarray DataArray")

    # Check if the last two dimensions are latitude and longitude
    if (da.dims[-2], da.dims[-1]) != ('latitude', 'longitude'):
        raise ValueError("The last two dimensions of 'da' must be 'latitude' and 'longitude'")

    # initialize output array
    #smooth = np.zeros((NH.size,) + da.shape)

    smooth_values = np.zeros((NH.size,) + da.shape)
    coords = {'NH': NH, **da.coords}
    dims = ['NH'] + list(da.dims)
    smooth = xr.DataArray(smooth_values, coords=coords, dims=dims)
    
    for i, n in enumerate(NH):
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



def calc_fss_bootstrap(fss,fss_bs,RF_error,F_error,nshuffle,nsample,init_dates,NH):
    """
    calculates fractions skill score and generates bootstrapped estimates by boostrapping
    subsampling the forecasts/mse_forecasts
    """

    init_dates_index  = np.arange(0,init_dates.size)
    init_dates_random = init_dates_index.copy()
    RF_mse            = (1/init_dates.size)*RF_error.sum(dim='init_dates').values
    F_mse             = (1/init_dates.size)*F_error.sum(dim='init_dates').values
    for i in range(nshuffle):
        # calc mean square error of forecast       
        F_mse_bs = (1/init_dates_random.size)*F_error.sel(init_dates=init_dates_random).sum(dim='init_dates').values
        # calc fss
        for n in range(0,NH.size,1):
            if NH[n] % 2 != 0: # odd
                fss[n,:]      = 1.0 - F_mse[n,:]/RF_mse[n,:]
                fss_bs[n,:,i] = 1.0 - F_mse_bs[n,:]/RF_mse[n,:]
            else: # even
                fss_bs[n,:,i] = np.nan
                fss[n,:]      = np.nan
        # shuffle forecasts (init_dates) randomly with replacement
        init_dates_random = np.random.choice(init_dates_index,nsample,replace='True')    
    return fss,fss_bs


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



def init_error(dim,NH,init_dates):
    """
    Initializes error array used below.
    Written here to clean up code.
    """
    data   = np.zeros((init_dates.size,NH.size,dim.ntime),dtype=np.float32)
    dims   = ["init_dates","neighborhood","time"]
    coords = dict(init_dates=np.arange(0,init_dates.size),neighborhood=NH,time=dim.time)
    name   = 'error'
    error  = xr.DataArray(data=data,dims=dims,coords=coords,name=name)
    return error



def init_fss(dim,NH,nshuffle):
    """
    Initializes fss arrays used below.
    Written here to clean up code. 
    """
    data      = np.zeros((NH.size,dim.ntime),dtype=np.float32)
    data_bs   = np.zeros((NH.size,dim.ntime,nshuffle),dtype=np.float32)
    dims      = ["neighborhood","time"]
    dims_bs   = ["neighborhood","time","number"]
    coords    = dict(neighborhood=NH,time=dim.time)
    coords_bs = dict(neighborhood=NH,time=dim.time,number=np.arange(0,nshuffle,1))
    attrs     = dict(description='fractions skill score of forecast',units='unitless')
    attrs_bs  = dict(description='fractions skill score of forecast bootstrapped',units='unitless')
    name      = 'fss'
    name_bs   = 'fss_bs'
    fss       = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    fss_bs    = xr.DataArray(data=data_bs,dims=dims_bs,coords=coords_bs,attrs=attrs_bs,name=name_bs)
    return fss,fss_bs


