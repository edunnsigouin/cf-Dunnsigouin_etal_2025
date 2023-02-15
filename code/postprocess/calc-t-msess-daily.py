"""
Calculates the mean-square-error skill score as a function of 
lead time for ecmwf forecasts. Reference forecasts are either 
era5 climatology or era5 persistence. Verification is era5.
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

# INPUT -----------------------------------------------
ref_forecast_flag = 'clim'                   # clim or pers
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
mon_thu_start     = ['20210104','20210107']  # first monday & thursday initialization date of forecast
num_i_weeks       = 52                       # number of weeks withe forecasts
grid              = '0.5x0.5'              # '0.25x0.25' & '0.5x0.5'
nshuffle          = 100                      # number of times to shuffle initialization dates for error bars
comp_lev          = 5
write2file        = True
# -----------------------------------------------------      

# initialize msess array
dim   = s2s.get_dim(grid)
msess = np.zeros((dim.ntime,nshuffle))

# get all initialization dates and convert to list
init_dates        = s2s.get_monday_thursday_dates(mon_thu_start,num_i_weeks)
init_dates        = init_dates.strftime('%Y-%m-%d').values.tolist()
init_dates_random = init_dates.copy() # shuffled dates for errorbar calculation

for i in range(nshuffle):
    
    misc.tic()
    print('\niteration #:',str(i+1) ,', variable: ' + variable + ', grid: ',grid)

    # get list of filenames
    filenames_verification = []
    filenames_forecast     = []
    filenames_ref_forecast = []
    for j in init_dates_random:        
        path_in_verification = config.dirs['era5_model_daily'] + variable + '/'
        filename1            = path_in_verification + variable + '_' + grid + '_' + j + '.nc'
        filenames_verification.append(filename1)
        
        path_in_forecast = config.dirs['forecast_daily'] + variable + '/'
        filename2        = path_in_forecast + variable + '_' + grid + '_' + j + '.nc'
        filenames_forecast.append(filename2)
        
        if ref_forecast_flag == 'clim':
            path_in_ref_forecast = config.dirs['era5_model_clim'] + variable + '/'
            filename3            = path_in_ref_forecast + variable + '_' + grid + '_' + j + '.nc'
        elif ref_forecast_flag == 'pers':
            print('need to code this!')
        filenames_ref_forecast.append(filename3)
            
    # Read in files
    ds_ref_forecast = xr.open_mfdataset(filenames_ref_forecast,preprocess=preprocess,combine='nested',concat_dim='chunks')
    ds_verification = xr.open_mfdataset(filenames_verification,preprocess=preprocess,combine='nested',concat_dim='chunks')
    ds_forecast     = xr.open_mfdataset(filenames_forecast,preprocess=preprocess,combine='nested',concat_dim='chunks').mean(dim='number') # ensemble mean
    
    # calc mean square error                                                                                                                                            
    mse_forecast     = (1/len(init_dates_random))*((ds_forecast[variable] - ds_verification[variable])**2).sum(dim='chunks')
    mse_ref_forecast = (1/len(init_dates_random))*((ds_ref_forecast[variable] - ds_verification[variable])**2).sum(dim='chunks')

    ds_ref_forecast.close()
    ds_verification.close()
    ds_forecast.close()

    # calculate explicitely                                                                                                                                             
    with ProgressBar():
        mse_forecast     = mse_forecast.compute().to_dataset()
        mse_ref_forecast = mse_ref_forecast.compute().to_dataset()

    # weighted spatial mean of mse                                                                                                                 
    mse_forecast     = misc.xy_mean(mse_forecast)
    mse_ref_forecast = misc.xy_mean(mse_ref_forecast)

    # calculate msess                                                                                                                                                       
    msess[:,i] = 1 - mse_forecast[variable].values/mse_ref_forecast[variable].values
    
    # shuffle init dates for error bar calculation
    init_dates_random = random.sample(init_dates,33)
    misc.toc()
    
    
if write2file:    
    print('writing to file..')
    da           = xr.DataArray(data=msess,dims=["time","number"],
                                coords=dict(number=np.arange(0,nshuffle,1),time=dim.time),
                                attrs=dict(description='mean square error skill score',units='unitless'))
    ds           = da.to_dataset(name='msess')
    path_out     = config.dirs['calc_forecast_daily'] + variable + '/'
    filename_out = 't_msess_' + ref_forecast_flag + '_' + grid + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
    s2s.to_netcdf_pack64bit(ds['msess'],path_out + filename_out)

    print('compress file to reduce space..\n')
    s2s.compress_file(comp_lev,3,filename_out,path_out)



