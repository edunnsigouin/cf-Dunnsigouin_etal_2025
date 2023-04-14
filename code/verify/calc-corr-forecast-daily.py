"""
Calculates the correlation as a function of lead time or timescale 
for ecmwf forecasts. Reference forecasts are either 
era5 climatology or era5 persistence. Verification is era5.
Code includes bootstrapping of forecast covariances to put error bars 
on correlation.
"""

import numpy  as np
import xarray as xr
import os
from dask.diagnostics   import ProgressBar
from forsikring import config,misc,s2s
import random


def preprocess(ds):
    '''change time dim from calendar dates to numbers'''
    if ds.time.size == 15:
        ds['time'] = np.arange(1,ds.time.size+1,1) # high resolution lead times
    elif ds.time.size == 31:
        ds['time'] = np.arange(16,47,1) # low resolution lead times
    return ds

def time_2_timescale(ds,time_flag):
    """ 
    resamples daily time into timescales following
    Wheeler et al. 2016 QJRMS. For exmaple, 1d1d,2d2d etc..
    Not exactly same since hr to lr data occurs on day 15 not 14. 
    """
    if time_flag == 'timescale':
        if ds.time.size == 15:
            temp1 = ds.sel(time=2).drop_vars('time')
            temp2 = ds.sel(time=slice(3,4)).mean(dim='time')
            temp3 = ds.sel(time=slice(5,8)).mean(dim='time')
            temp4 = ds.sel(time=slice(8,15)).mean(dim='time')
            ds    = xr.concat([temp1,temp2,temp3,temp4], "timescale")
            ds    = ds.assign(timescale=np.arange(1,5,1))
        elif ds.time.size == 31:
            temp1 = ds.sel(time=slice(16,28)).mean(dim='time')
            temp2 = ds.sel(time=slice(29,46)).mean(dim='time')
            ds    = xr.concat([temp1,temp2], "timescale")
            ds    = ds.assign(timescale=np.arange(5,7,1))
    elif time_flag == 'time':
        ds = ds
            
    return ds


# INPUT -----------------------------------------------
ref_forecast_flag = 'clim'                   # clim or pers
time_flag         = 'time'                   # time or timescale
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'europe'               # europe or norway only?
mon_thu_start     = ['20210104','20210107']  # first monday & thursday initialization date of forecast
num_i_weeks       = 5                       # number of weeks withe forecasts
grids             = ['0.25x0.25','0.5x0.5']  # '0.25x0.25' & '0.5x0.5'
nshuffle          = 10000                    # number of times to shuffle initialization dates for error bars
nsample           = 50
comp_lev          = 5
write2file        = True
# -----------------------------------------------------      

misc.tic()

# define stuff
init_dates             = s2s.get_monday_thursday_dates(mon_thu_start,num_i_weeks)
init_dates             = init_dates.strftime('%Y-%m-%d').values
path_in_forecast       = config.dirs['forecast_daily'] + variable + '/'
path_in_verification   = config.dirs['era5_forecast_daily'] + variable + '/'
path_out               = config.dirs['verify_forecast_daily']
if time_flag == 'time':
    filename_hr_out = 't_corr_' + variable + '_' + 'forecast-' + ref_forecast_flag + '_' + \
                      '0.25x0.25_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
    filename_lr_out = 't_corr_' + variable + '_' + 'forecast-' + ref_forecast_flag + '_' + \
                      '0.5x0.5_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
    filename_out    = 't_corr_' + variable + '_' + 'forecast-' + ref_forecast_flag + '_' + \
                      domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
elif time_flag == 'timescale':
    filename_hr_out = 'timescale_corr_' + variable + '_' + 'forecast-' + ref_forecast_flag + '_' + \
                      '0.25x0.25_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
    filename_lr_out = 'timescale_corr_' + variable + '_' + 'forecast-' + ref_forecast_flag + '_' + \
                      '0.5x0.5_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
    filename_out    = 'timescale_corr_' + variable + '_' + 'forecast-' + ref_forecast_flag + '_' + \
                      domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'

    
for grid in grids:
    
    # initialize corr array
    dim = s2s.get_dim(grid)
    if time_flag == 'time':
        corr = np.zeros((dim.ntime,nshuffle))
    elif time_flag == 'timescale':
        corr = np.zeros((dim.ntimescale,nshuffle))
        
    # define input filenames
    filenames_verification =  path_in_verification + variable + '_' + grid + '_' + init_dates + '.nc'
    filenames_forecast     =  path_in_forecast + variable + '_' + grid + '_' + init_dates + '.nc'

    # read in files     
    ds_verification = xr.open_mfdataset(filenames_verification,preprocess=preprocess,combine='nested',concat_dim='chunks')
    ds_forecast     = xr.open_mfdataset(filenames_forecast,preprocess=preprocess,combine='nested',concat_dim='chunks').mean(dim='number') # ensemble mean

    # sub-select specific domain
    dim             = misc.get_domain_dim(domain,dim,grid)
    ds_forecast     = ds_forecast.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
    ds_verification = ds_verification.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')

    # calculate explicitely 
    with ProgressBar():
        ds_forecast     = ds_forecast.compute()
        ds_verification = ds_verification.compute()

    # resample time into timescales if required         
    ds_forecast     = time_2_timescale(ds_forecast,time_flag)
    ds_verification = time_2_timescale(ds_verification,time_flag)

    # calculate means
    
    # calc squared error for all forecasts individually
    temp_forecast_verification = ds_forecast[variable]*ds_verification[variable]
    temp_forecast              = ds_forecast[variable]**2
    temp_verification          = ds_verification[variable]**2
    
    ds_verification.close()
    ds_forecast.close()

    # weighted spatial mean
    cov_forecast_verification = misc.xy_mean(cov_forecast_verification)
    cov_forecast              = misc.xy_mean(cov_forecast)
    cov_verification          = misc.xy_mean(cov_verification)
    
    # bootstrap temp of forecasts, then take forecast-mean to calculate correlation of forecasts 
    chunks           = np.arange(0,init_dates.size,1)
    chunks_random    = chunks.copy()
    cov_verification = (1/chunks.size)*temp_verification.sum(dim='chunks').values # over all initializations
    for i in range(nshuffle):

        # calc covariances
        cov_forecast              = (1/chunks_random.size)*temp_forecast.sel(chunks=chunks_random).sum(dim='chunks').values 
        cov_forecast_verification = (1/chunks_random.size)*temp_forecast_verification.sel(chunks=chunks_random).sum(dim='chunks').values
        
        # calc correlation
        corr[:,i] = cov_forecast_verification/(cov_forecast*cov_verification)**0.5
    
        # shuffle forecasts (chunks) randomly with replacement
        chunks_random = np.random.choice(chunks,nsample,replace='True')
    
    if write2file:    
        print('writing to file..')
        if time_flag == 'time':
            ds = xr.DataArray(data=corr,dims=["time","number"],
                                coords=dict(number=np.arange(0,nshuffle,1),time=dim.time),
                                attrs=dict(description='correlation',units='unitless'),
                                name='corr')
        elif time_flag == 'timescale':
            ds = xr.DataArray(data=corr,dims=["timescale","number"],
                                 coords=dict(number=np.arange(0,nshuffle,1),timescale=dim.timescale),
                                 attrs=dict(description='correlation',units='unitless'),
                                 name='corr')

        if grid == '0.25x0.25': ds.to_netcdf(path_out+filename_hr_out)
        elif grid == '0.5x0.5': ds.to_netcdf(path_out+filename_lr_out)
        ds.close()


if write2file:
    print('combine high & low resolution files into one file..')
    ds_hr           = xr.open_dataset(path_out + filename_hr_out)
    ds_lr           = xr.open_dataset(path_out + filename_lr_out)
    ds              = xr.concat([ds_hr,ds_lr], time_flag)
    ds.to_netcdf(path_out+filename_out)
    os.system('rm ' + path_out + filename_hr_out + ' ' + path_out + filename_lr_out)

    print('compress file to reduce space..')
    s2s.compress_file(comp_lev,3,filename_out,path_out)
    ds.close()
    ds_lr.close()
    ds_hr.close()
    
misc.toc()

