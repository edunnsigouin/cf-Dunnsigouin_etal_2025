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

# dictionary of model versions with (start,end)     
model_version_specs = dict(
    ECMWF = dict(
        CY43R1 = ('2016-11-22','2017-07-10'),
        CY43R3 = ('2017-07-11','2018-06-05'),
        CY45R1 = ('2018-06-06','2019-06-10'),
        CY46R1 = ('2019-06-11','2020-06-29'),
        CY47R1 = ('2020-06-30','2021-05-10'),
        CY47R2 = ('2021-05-11','2021-10-11'),
        CY47R3 = ('2021-10-12',datetime.strftime(datetime.today(),"%Y-%m-%d"))
    )
)


def which_mv_for_init(fc_init_date,model='ECMWF',fmt='%Y-%m-%d'):
    """    
    return model version for a specified initialization date and model 
    INPUT:  
            fc_init_date:   date string YYYY-mm-dd, datetime.datetime    
                            or pandas.Timestamp
            model:          string for the modeling center (currently just
                            'ECMWF' is valid)
                            default: 'ECMWF'
            fmt:            string specifying the date format,  
                            default: '%Y-%m-%d'  
    OUTPUT:                                                                                                                                                
            model version as string
    """
    if isinstance(fc_init_date,str):
        # convert date string to datetime object: 
        fc_init_datetime = pd.Timestamp(fc_init_date)

    elif isinstance(fc_init_date,pd.Timestamp):
        fc_init_datetime = fc_init_date

    elif isinstance(fc_init_date,datetime.datetime):
        fc_init_datetime = pd.Timestamp(fc_init_date)

    else:
        raise TypeError(
            'Input of invalid type was given to date_to_model.which_mv_for_init'
            )
        return None

    # got through the model versions from the above dictionary:
    for MV,mv_dates in model_version_specs[model].items():
        # convert first and last dates to datetime:

        mv_first = pd.Timestamp(mv_dates[0])
        mv_last  = pd.Timestamp(mv_dates[-1])

        # check if the given date is within the current model version's 
        # start and end dates:
        if  mv_first <= fc_init_datetime <= mv_last:
            valid_version = MV
    try:
        return valid_version
    except:
        
        raise ValueError(
            'No matching model version found...'
            )
        return None



def get_monday_thursday_dates(mon_thu_start,num_i_weeks):
    """
    generate set of continuous monday and thursday dates starting on mon_thu_start[0] and mon_thu_start[1] respectively
    """
    dates_monday          = pd.date_range(mon_thu_start[0], periods=num_i_weeks, freq="7D") # forecasts that start monday
    dates_thursday        = pd.date_range(mon_thu_start[1], periods=num_i_weeks, freq="7D") # forecasts that start thursday
    dates_monday_thursday = dates_monday.union(dates_thursday)
    return dates_monday_thursday


def get_init_dates(init_start,init_n):
    """
    generate set of continuous dates on mondays and thursdays starting on init_start
    with length init_n
    """
    dates_monday          = pd.date_range(init_start, periods=init_n, freq="W-MON") # forecasts that start monday
    dates_thursday        = pd.date_range(init_start, periods=init_n, freq="W-THU")
    dates_monday_thursday = dates_monday.union(dates_thursday)
    dates_monday_thursday = dates_monday_thursday[:init_n] 
    return dates_monday_thursday



def grib_to_netcdf(path,filename_grb,filename_nc):
    """
    wrapper for eccode's grib_to_netcdf function
    """
    os.system('grib_to_netcdf ' + path + filename_grb + ' -I step -o ' + path + filename_nc)
    os.system('rm ' +  path + filename_grb)
    return


def compress_file(comp_lev,ncfiletype,filename,path_out):
    """
    wrapper for compressing file using nccopy
    """
    cmd           = 'nccopy -k ' + str(ncfiletype) + ' -s -d ' + str(comp_lev) + ' '
    filename_comp = 'temp_' + filename 
    os.system(cmd + path_out + filename + ' ' + path_out + filename_comp)
    os.system('mv ' + path_out + filename_comp + ' ' + path_out + filename)
    return


def to_netcdf_pack64bit(da,filename_out):
    """
    A wraper on xrray's to_netcdf with 64-bit
    encoding to pack the data.
    Modified from: https://stackoverflow.com/questions/57179990/compression-of-arrays-in-netcdf-file
    """
    n    = 16
    vmin = np.min(da).item()
    vmax = np.max(da).item()

    # stretch/compress data to the available packed range                                                                                                                                                    
    scale_factor = (vmax - vmin) / (2 ** n - 1)

    # translate the range to be symmetric about zero
    add_offset = vmin + 2 ** (n - 1) * scale_factor

    # write2file
    encoding = {da.name:{
                "dtype": 'int16',
                "scale_factor": scale_factor,
                "add_offset": add_offset,
                "_FillValue": -9999,
                "missing_value":-9999}}

    da.to_netcdf(filename_out,encoding=encoding,format='NETCDF3_64BIT')
    
    return


def get_dim(grid,time_flag):
    """
    imports data dimensions given a grid
    """
    if grid == '0.25x0.25':
        from forsikring import dim_hr as dim
    elif grid == '0.5x0.5':
        from forsikring import dim_lr as dim

    if time_flag == 'timescale':
        dim.time  = dim.timescale
        dim.ntime = dim.ntimescale
        
    return dim



def convert_2_binary_RL08MWR(data,threshold):
    """
    Converts forecast data into binary. 1 above a given 
    threshold and zero below
    """
    # converts to true/false then 1's and 0's
    binary_data = (data >= threshold).astype(np.int32)
    
    return binary_data



def calc_frac_RL08MWR(NH,da):
    """
    Generates fractions following equations 2 and 3 from 
    Roberts and Lean 2008 MWR given binary input data.
    Specifically, smooths 2D x,y fields using a boxcar smoother. 
    Here, last two dimensions of 'da' are latitude and longitude.
    Note: only performs calculation on odd sized neighborhoods
    """
    frac = np.zeros((NH.size,) + da.shape)    
    for n in range(0,NH.size,1):
        if NH[n] % 2 != 0: # odd
            kernel          = np.ones((NH[n],NH[n]))
            kernel          = kernel[None,None,:,:]
            frac[n,:,:,:,:] = ndimage.convolve(da.values, kernel, mode='constant', cval=0.0, origin=0)/NH[n]**2
        else: # even
            frac[n,:,:,:,:] = np.nan
    return frac


def calc_fss_bootstrap(fss,fss_bs,RF_error,F_error,nshuffle,nsample,chunks,NH):
    """
    calculates fractions skill score and generates bootstrapped estimates by boostrapping
    subsampling the forecasts/mse_forecasts
    """
    chunks_random = chunks.copy()
    RF_mse        = (1/chunks.size)*RF_error.sum(dim='chunks').values
    F_mse         = (1/chunks.size)*F_error.sum(dim='chunks').values
    for i in range(nshuffle):
        # calc mean square error of forecast       
        F_mse_bs = (1/chunks_random.size)*F_error.sel(chunks=chunks_random).sum(dim='chunks').values
        # calc fss
        for n in range(0,NH.size,1):
            if NH[n] % 2 != 0: # odd
                fss[n,:]      = 1.0 - F_mse[n,:]/RF_mse[n,:]
                fss_bs[n,:,i] = 1.0 - F_mse_bs[n,:]/RF_mse[n,:]
            else: # even
                fss_bs[n,:,i] = np.nan
                fss[n,:]      = np.nan
        # shuffle forecasts (chunks) randomly with replacement
        chunks_random = np.random.choice(chunks,nsample,replace='True')    
    return fss,fss_bs


def calc_msess_bootstrap(msess,msess_bs,RF_error,F_error,nshuffle,nsample,chunks):
    """
    calculates mean square error skill score and generates bootstrapped estimates by boostrapping
    subsampling the forecasts/mse_forecasts
    """
    chunks_random  = chunks.copy()
    RF_mse         = (1/chunks.size)*RF_error.sum(dim='chunks').values
    F_mse          = (1/chunks.size)*F_error.sum(dim='chunks').values
    msess[:]       =  1 - F_mse/RF_mse
    for i in range(nshuffle):
        # calc mean square error                          
        F_mse_bs = (1/chunks_random.size)*F_error.sel(chunks=chunks_random).sum(dim='chunks').values
        # calc msess
        msess_bs[:,i] =  1 - F_mse_bs/RF_mse
        # shuffle forecasts (chunks) randomly with replacement 
        chunks_random = np.random.choice(chunks,nsample,replace='True')
    return msess,msess_bs




def calc_fss_RL08MWR(O,F,RF,method):
    """
    Calculates the fractions skill score following equations 5,6,7
    from Roberts and Lean 2008 MWR given input fractions for observations,
    forecast, and reference forecast.
    INPUT: O, F and RF have shape [N,Nx,Ny], where N = neighborhood size, 
    Nx and Ny are spatial dimensions. O,F and RF must have same dimension 
    sizes.
    If method = 'classic', then mse of reference forecast is calculated
    as in equation 7 from RL08MWR. Else if method = 'default', mse of reference forecast defaults 
    to regular mse for input reference forecast (like climatology or persistence)
    """
    Nx = O.shape[1]
    Ny = O.shape[2]
    
    # calc MSE 
    error_forecast     = (O - F)**2
    error_ref_forecast = (O - RF)**2
    mse_forecast       = error_forecast.sum(axis=2).sum(axis=1)/Nx/Ny

    if method == 'classic':
        mse_ref_forecast = (1/Nx/Ny)*(np.sum(np.sum(O**2,axis=2),axis=1) + np.sum(np.sum(F**2,axis=2),axis=1))
    elif method == 'default':
        mse_ref_forecast = error_ref_forecast.sum(axis=2).sum(axis=1)/Nx/Ny
        
    # fractions skill score                                 
    fss = 1.0 - mse_forecast/mse_ref_forecast
    
    return fss



def preprocess(ds,grid,time_flag):
    '''change time dim from calendar dates to numbers'''
    if time_flag == 'time':
        if grid == '0.25x0.25':
            ds['time'] = np.arange(1,16,1) 
        elif grid == '0.5x0.5':
            ds['time'] = np.arange(16,47,1) 
    elif time_flag == 'timescale':
        if grid == '0.25x0.25':
            ds['time'] = np.arange(1,5,1)
        elif grid == '0.5x0.5':
            ds['time'] = np.arange(1,3,1)
    return ds


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

