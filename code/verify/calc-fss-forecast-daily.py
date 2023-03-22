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


def init_fraction_datarray(dim,chunks,nchunks):
    """
    Code to initialize fraction array used below.
    Written here to clean up code.
    """
    frac = xr.DataArray(data=np.zeros((nchunks,dim.ntime,NHsize,dim.nlatitude,dim.nlongitude)),
                        dims=["chunks","time","NHsize","latitude","longitude"],
                        coords=dict(chunks=chunks,time=dim.time,NHsize=np.arange(0,NHsize),
                                    latitude=dim.latitude,longitude=dim.longitude),
                        name='frac')
    return frac

def init_fss_datarray(dim,NHsize,nshuffle):
    """
    Code to initialize fss array used below.
    Written here to clean up code.
    """
    fss = xr.DataArray(data=np.zeros((dim.ntime,NHsize,nshuffle)),
                        dims=["time","NHsize","number"],
                        coords=dict(time=dim.time,NHsize=np.arange(0,NHsize),
                                    number=np.arange(0,nshuffle,1)),
                        attrs=dict(description='fractions skill score of forecast',units='unitless'),
                        name='fss')
    return fss

# INPUT -----------------------------------------------
RF_flag           = 'clim'                   # clim or pers
time_flag         = 'time'                   # time or timescale
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'europe'                 # europe or norway only?
mon_thu_start     = ['20210104','20210107']  # first monday & thursday initialization date of forecast
num_i_weeks       = 5                        # number of weeks withe forecasts
grids             = ['0.25x0.25']            # '0.25x0.25' & '0.5x0.5'
NHsize            = 5                        # size of neighborhoods for fss calculation
nshuffle          = 2                    # number of times to shuffle initialization dates for error bars
nsample           = 2                       # number of sampled forecasts with replacement in each bootstrap member
comp_lev          = 5                        # compression level (0-10) of netcdf putput file
write2file        = False
# -----------------------------------------------------         

misc.tic()

# define stuff  
init_dates       = s2s.get_monday_thursday_dates(mon_thu_start,num_i_weeks)
init_dates       = init_dates.strftime('%Y-%m-%d').values
chunks           = np.arange(0,init_dates.size,1)
nchunks          = chunks.size
path_in_F        = config.dirs['forecast_daily'] + variable + '/'
path_in_O        = config.dirs['era5_model_daily'] + variable + '/'
path_in_RF       = config.dirs['era5_model_' + RF_flag] + variable + '/'
path_out         = config.dirs['calc_forecast_daily']
filename_hr_out  = time_flag + '_fss_' + variable + '_' + 'forecast-' + RF_flag + '_' + \
                   '0.25x0.25_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
filename_lr_out  = time_flag + '_fss_' + variable + '_' + 'forecast-' + RF_flag + '_' + \
                   '0.5x0.5_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
filename_out     = time_flag + '_fss_' + variable + '_' + 'forecast-' + RF_flag + '_' + \
                   domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'

for grid in grids:

    # initialize arrays                                                                                                    
    dim     = s2s.get_dim(grid,time_flag)
    fss     = init_fss_datarray(dim,NHsize,nshuffle)
    O_frac  = init_fraction_datarray(dim,chunks,nchunks)
    F_frac  = init_fraction_datarray(dim,chunks,nchunks)
    RF_frac = init_fraction_datarray(dim,chunks,nchunks)

    # define input filenames
    filenames_O  =  path_in_O + variable + '_' + grid + '_' + init_dates + '.nc'
    filenames_F  =  path_in_F + variable + '_' + grid + '_' + init_dates + '.nc'
    filenames_RF =  path_in_RF + variable + '_' + grid + '_' + init_dates + '.nc'

    # read in files
    ds_O  = xr.open_mfdataset(filenames_O,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks')
    ds_F  = xr.open_mfdataset(filenames_F,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks').mean(dim='number') # ensemble mean 
    ds_RF = xr.open_mfdataset(filenames_RF,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks')
    
    # sub-select specific domain
    dim   = misc.get_domain_dim(domain,dim,grid)
    ds_O  = ds_O.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
    ds_F  = ds_F.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
    ds_RF = ds_RF.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')

    # calculate explicitely
    with ProgressBar():
        ds_O  = ds_O.compute()
        ds_F  = ds_F.compute()
        ds_RF = ds_RF.compute()

    # resample time into timescales if required
    ds_O  = s2s.time_2_timescale(ds_O,time_flag)
    ds_F  = s2s.time_2_timescale(ds_F,time_flag)
    ds_RF = s2s.time_2_timescale(ds_RF,time_flag)

    # calculate fractions
    for t in range(0,dim.ntime,1):
        print(t)
        for c in range(0,nchunks,1):
            O_frac[c,t,:,:,:]  = s2s.calc_frac_RL08MWR(NHsize,ds_O[variable][c,t,:,:].values)
            F_frac[c,t,:,:,:]  = s2s.calc_frac_RL08MWR(NHsize,ds_F[variable][c,t,:,:].values)
            RF_frac[c,t,:,:,:] = s2s.calc_frac_RL08MWR(NHsize,ds_RF[variable][c,t,:,:].values)

    ds_RF.close()
    ds_O.close()
    ds_F.close()

    # calc squared error for all forecasts individually 
    error_F  = (F_frac - O_frac)**2
    error_RF = (RF_frac - O_frac)**2

    # weighted spatial mean
    error_F  = misc.xy_mean(error_F)
    error_RF = misc.xy_mean(error_RF)

    # bootstraped fss
    chunks_random = chunks.copy()
    mse_RF        = (1/nchunks)*error_RF.sum(dim='chunks').values
    for i in range(nshuffle):
        # calc mean square error of forecast
        mse_F = (1/chunks_random.size)*error_F.sel(chunks=chunks_random).sum(dim='chunks').values
        # calc fss                                                                                                                                                     
        fss[:,:,i] = 1.0 - mse_F/mse_RF
        # shuffle forecasts (chunks) randomly with replacement
        chunks_random = np.random.choice(chunks,nsample,replace='True')


print(fss[:,2,0].values)

misc.toc()

