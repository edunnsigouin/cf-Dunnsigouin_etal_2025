"""
Calculates the mean-square-error skill score as a function of 
lead time for ecmwf forecasts. Reference forecasts are either 
era5 climatology or era5 persistence. Verification is era5.
Code includes bootstrapping of forecast mse to put error bars
on msess
"""

import numpy  as np
import xarray as xr
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

def resample_2_timescale(ds):
    """
    resamples daily time into timescales following 
    Wheeler et al. 2016 QJRMS. For exmaple, 1d1d,2d2d etc..
    Not exactly same since hr to lr data occurs on day 15 not 14.
    """
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
    return ds
    

# INPUT -----------------------------------------------
ref_forecast_flag = 'clim'                   # clim or pers
variable          = 'tp24'                # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'vestland'                 # europe or norway only?
mon_thu_start     = ['20210104','20210107']  # first monday & thursday initialization date of forecast
num_i_weeks       = 52                      # number of weeks withe forecasts
grid              = '0.5x0.5'              # '0.25x0.25' & '0.5x0.5'
nshuffle          = 10000                    # number of times to shuffle initialization dates for error bars
nsample           = 50
comp_lev          = 5
write2file        = True
# -----------------------------------------------------      

misc.tic()

# initialize msess array
dim                    = s2s.get_dim(grid)
msess                  = np.zeros((dim.ntimescale,nshuffle))
mse_forecast           = np.zeros((dim.ntimescale,nshuffle))

# get all initialization dates and convert to list
init_dates             = s2s.get_monday_thursday_dates(mon_thu_start,num_i_weeks)
init_dates             = init_dates.strftime('%Y-%m-%d').values

# define paths and output filename
path_in_forecast       = config.dirs['forecast_daily'] + variable + '/'
path_in_verification   = config.dirs['era5_model_daily'] + variable + '/'
path_in_ref_forecast   = config.dirs['era5_model_clim'] + variable + '/'
path_out               = config.dirs['calc_forecast_daily'] 
filename_out           = 'timescale_msess_' + variable + '_' + 'forecast-' + ref_forecast_flag + '_' + grid + '_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'

# define input filenames
filenames_verification =  path_in_verification + variable + '_' + grid + '_' + init_dates + '.nc'
filenames_forecast     =  path_in_forecast + variable + '_' + grid + '_' + init_dates + '.nc'
filenames_ref_forecast =  path_in_ref_forecast + variable + '_' + grid + '_' + init_dates + '.nc'

# read in files     
ds_ref_forecast = xr.open_mfdataset(filenames_ref_forecast,preprocess=preprocess,combine='nested',concat_dim='chunks')
ds_verification = xr.open_mfdataset(filenames_verification,preprocess=preprocess,combine='nested',concat_dim='chunks')
ds_forecast     = xr.open_mfdataset(filenames_forecast,preprocess=preprocess,combine='nested',concat_dim='chunks').mean(dim='number') # ensemble mean

# sub-select specific domain     
dim             = misc.get_domain_dim(domain,dim,grid)
ds_ref_forecast = ds_ref_forecast.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
ds_forecast     = ds_forecast.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
ds_verification = ds_verification.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')

# calculate explicitely
with ProgressBar():
    ds_forecast     = ds_forecast.compute()
    ds_ref_forecast = ds_ref_forecast.compute()
    ds_verification = ds_verification.compute()

# resample into timescales
ds_ref_forecast = resample_2_timescale(ds_ref_forecast) 
ds_forecast     = resample_2_timescale(ds_forecast)
ds_verification = resample_2_timescale(ds_verification)


# calc squared error for all forecasts individually
error_forecast     = (ds_forecast[variable] - ds_verification[variable])**2
error_ref_forecast = (ds_ref_forecast[variable] - ds_verification[variable])**2

ds_ref_forecast.close()
ds_verification.close()
ds_forecast.close()

# weighted spatial mean
error_forecast     = misc.xy_mean(error_forecast)
error_ref_forecast = misc.xy_mean(error_ref_forecast)

# bootstrap
chunks           = np.arange(0,init_dates.size,1)
chunks_random    = chunks.copy()
mse_ref_forecast = (1/chunks.size)*error_ref_forecast.sum(dim='chunks').values
for i in range(nshuffle):

    # calc mean square error    
    mse_forecast[:,i] = (1/chunks_random.size)*error_forecast.sel(chunks=chunks_random).sum(dim='chunks').values 
    
    # calc msess
    msess[:,i] = 1 - mse_forecast[:,i]/mse_ref_forecast[:]
    
    # shuffle forecasts (chunks) randomly with replacement
    chunks_random = np.random.choice(chunks,nsample,replace='True')
       

if write2file:    
    print('writing to file..')
    msess             = xr.DataArray(data=msess,dims=["timescale","number"],
                                     coords=dict(number=np.arange(0,nshuffle,1),timescale=dim.timescale),
                                     attrs=dict(description='mean square error skill score',units='unitless'),
                                     name='msess')
    mse_forecast      = xr.DataArray(data=mse_forecast,dims=["timescale","number"],
                                     coords=dict(number=np.arange(0,nshuffle,1),timescale=dim.timescale),
                                     attrs=dict(description='mean square error of forecast',units='?'),
                                     name='mse_forecast')
    mse_ref_forecast  = xr.DataArray(data=mse_ref_forecast,dims=["timescale"],
                                     coords=dict(timescale=dim.timescale),
                                     attrs=dict(description='mean square error of reference forecast',units='?'),
                                     name='mse_ref_forecast')
    ds                = xr.merge([msess,mse_forecast,mse_ref_forecast])
    ds.to_netcdf(path_out+filename_out)
    print('compress file to reduce space..')
    s2s.compress_file(comp_lev,3,filename_out,path_out)

misc.toc()

