"""
Calculates the fractional skill score as a function of                                                                                                        
lead time for ecmwf forecasts. Reference forecasts are either
era5 climatology or era5 persistence. Verification is era5.
Code includes bootstrapping of forecast mse to put error bars 
on fss.
"""

import numpy  as np
import xarray as xr
import os
from dask.diagnostics  import ProgressBar
from forsikring        import misc,s2s,config
import random

# INPUT -----------------------------------------------
ref_forecast_flag = 'clim'                   # clim or pers
time_flag         = 'time'                   # time or timescale
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'europe'                 # europe or norway only?
mon_thu_start     = ['20210104','20210107']  # first monday & thursday initialization date of forecast
num_i_weeks       = 1                        # number of weeks withe forecasts
grids             = ['0.25x0.25']            # '0.25x0.25' & '0.5x0.5'
nshuffle          = 10000                    # number of times to shuffle initialization dates for error bars
nsample           = 50                       # number of sampled forecasts with replacement in each bootstrap member
comp_lev          = 5                        # compression level (0-10) of netcdf putput file
write2file        = False
# -----------------------------------------------------         

misc.tic()

# define stuff  
init_dates           = s2s.get_monday_thursday_dates(mon_thu_start,num_i_weeks)
init_dates           = init_dates.strftime('%Y-%m-%d').values
path_in_forecast     = config.dirs['forecast_daily'] + variable + '/'
path_in_verification = config.dirs['era5_model_daily'] + variable + '/'
path_in_ref_forecast = config.dirs['era5_model_' + ref_forecast_flag] + variable + '/'
path_out             = config.dirs['calc_forecast_daily']
filename_hr_out      = time_flag + '_msess_' + variable + '_' + 'forecast-' + ref_forecast_flag + '_' + \
                        '0.25x0.25_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
filename_lr_out      = time_flag + '_msess_' + variable + '_' + 'forecast-' + ref_forecast_flag + '_' + \
                        '0.5x0.5_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
filename_out         = time_flag + '_msess_' + variable + '_' + 'forecast-' + ref_forecast_flag + '_' + \
                        domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'

for grid in grids:

    # initialize msess array                                                                                                    
    dim = s2s.get_dim(grid)
    if time_flag == 'time':
        msess        = np.zeros((dim.ntime,nshuffle))
        mse_forecast = np.zeros((dim.ntime,nshuffle))
    elif time_flag == 'timescale':
        msess        = np.zeros((dim.ntimescale,nshuffle))
        mse_forecast = np.zeros((dim.ntimescale,nshuffle))

    # define input filenames
    filenames_verification =  path_in_verification + variable + '_' + grid + '_' + init_dates + '.nc'
    filenames_forecast     =  path_in_forecast + variable + '_' + grid + '_' + init_dates + '.nc'
    filenames_ref_forecast =  path_in_ref_forecast + variable + '_' + grid + '_' + init_dates + '.nc'

    # read in files
    ds_ref_forecast = xr.open_mfdataset(filenames_ref_forecast,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks')
    ds_verification = xr.open_mfdataset(filenames_verification,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks')
    ds_forecast     = xr.open_mfdataset(filenames_forecast,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks').mean(dim='number') # ensemble mean 

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

    # resample time into timescales if required
    ds_ref_forecast = s2s.time_2_timescale(ds_ref_forecast,time_flag)
    ds_forecast     = s2s.time_2_timescale(ds_forecast,time_flag)
    ds_verification = s2s.time_2_timescale(ds_verification,time_flag)    

    # calculate fractions
    #calc_frac_RL08MWR(N,data)

    ds_ref_forecast.close()
    ds_verification.close()
    ds_forecast.close()
