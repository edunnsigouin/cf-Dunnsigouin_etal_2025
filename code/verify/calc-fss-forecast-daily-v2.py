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
from matplotlib        import pyplot as plt


def init_frac(dim,NH,chunks,nchunks):
    """
    Code to initialize fraction array used below.
    Written here to clean up code.
    """
    frac = xr.DataArray(data=np.zeros((nchunks,dim.ntime,NH.size,dim.nlatitude,dim.nlongitude),dtype=np.float32),
                        dims=["chunks","time","neighborhood","latitude","longitude"],
                        coords=dict(chunks=chunks,time=dim.time,neighborhood=NH,
                                    latitude=dim.latitude,longitude=dim.longitude),
                        name='frac')
    return frac


def init_fss(dim,NH,nshuffle):
    """
    Code to initialize fss array used below.
    Written here to clean up code.
    """
    fss = xr.DataArray(data=np.zeros((dim.ntime,NH.size,nshuffle),dtype=np.float32),
                        dims=["time","neighborhood","number"],
                        coords=dict(time=dim.time,neighborhood=NH,
                                    number=np.arange(0,nshuffle,1)),
                        attrs=dict(description='fractions skill score of forecast',units='unitless'),
                        name='fss')
    return fss


# INPUT -----------------------------------------------
RF_flag           = 'clim'                   # clim or pers
time_flag         = 'timescale'                   # time or timescale
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'europe'                 # europe or norway only?
init_start        = '20210104'               # first initialization date of forecast (either a monday or thursday)
init_n            = 104                      # number of forecasts 
grids             = ['0.25x0.25']            # '0.25x0.25' & '0.5x0.5'
threshold         = 0.01
NH                = np.array([1,9,19,29,39,49])
nshuffle          = 10000                        # number of times to shuffle initialization dates for error bars
nsample           = 50                        # number of sampled forecasts with replacement in each bootstrap member
comp_lev          = 5                        # compression level (0-10) of netcdf putput file
write2file        = True
# -----------------------------------------------------


misc.tic()

# define stuff  
init_dates       = s2s.get_init_dates(init_start,init_n)
init_dates       = init_dates.strftime('%Y-%m-%d').values
chunks           = np.arange(0,init_n,1)
nchunks          = chunks.size
path_in_F        = config.dirs['forecast_daily'] + variable + '/'
path_in_O        = config.dirs['era5_model_daily'] + variable + '/'
path_in_RF       = config.dirs['era5_model_' + RF_flag] + variable + '/'
path_out         = config.dirs['calc_forecast_daily']
filename_hr_out  = 'temp_' + time_flag + '_fss_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
                   'thresh_' + str(threshold) + '_0.25x0.25_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
filename_lr_out  = time_flag + '_fss_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
                   'thresh_' + str(threshold) + '_0.5x0.5_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
filename_out     = time_flag + '_fss_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
                   'thresh_' + str(threshold) + '_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'

for grid in grids:

    # initialize arrays                                                                                                    
    dim     = s2s.get_dim(grid,time_flag)
    fss     = init_fss(dim,NH,nshuffle)
    O_frac  = init_frac(dim,NH,chunks,nchunks)
    F_frac  = init_frac(dim,NH,chunks,nchunks)
    RF_frac = init_frac(dim,NH,chunks,nchunks)

    # define input filenames
    filenames_O  =  path_in_O + variable + '_' + grid + '_' + init_dates + '.nc'
    filenames_F  =  path_in_F + variable + '_' + grid + '_' + init_dates + '.nc'
    filenames_RF =  path_in_RF + variable + '_' + grid + '_' + init_dates + '.nc'

    # read in files
    ds_O  = xr.open_mfdataset(filenames_O,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks')
    ds_F  = xr.open_mfdataset(filenames_F,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks').mean(dim='number') # ensemble mean 
    ds_RF = xr.open_mfdataset(filenames_RF,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks')
    
    # sub-select specific domain
    dim     = misc.get_domain_dim(domain,dim,grid)
    ds_O    = ds_O.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
    ds_F    = ds_F.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
    ds_RF   = ds_RF.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
    O_frac  = O_frac.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
    F_frac  = F_frac.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
    RF_frac = RF_frac.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')

    # resample time into timescales if required 
    ds_O  = s2s.time_2_timescale(ds_O,time_flag)
    ds_F  = s2s.time_2_timescale(ds_F,time_flag)
    ds_RF = s2s.time_2_timescale(ds_RF,time_flag)

    # convert to binary above (1) and below (0) threshold 
    ds_O[variable]  = s2s.convert_2_binary_RL08MWR(ds_O[variable],threshold)
    ds_F[variable]  = s2s.convert_2_binary_RL08MWR(ds_F[variable],threshold)
    ds_RF[variable] = s2s.convert_2_binary_RL08MWR(ds_RF[variable],threshold)
    
    # calculate explicitely
    print('reading & postprocessing input data..')
    with ProgressBar():
        ds_O  = ds_O.compute()
        ds_F  = ds_F.compute()
        ds_RF = ds_RF.compute()

    # calculate fractions
    print('calculation fractions...')
    for t in range(0,dim.ntime,1):
        print(t)
        for c in range(0,nchunks,1):
            O_frac[c,t,:,:,:]  = s2s.calc_frac_RL08MWR_v2(NH,ds_O[variable][c,t,:,:].values)
            F_frac[c,t,:,:,:]  = s2s.calc_frac_RL08MWR_v2(NH,ds_F[variable][c,t,:,:].values)
            RF_frac[c,t,:,:,:] = s2s.calc_frac_RL08MWR_v2(NH,ds_RF[variable][c,t,:,:].values)
    
    ds_RF.close()
    ds_O.close()
    ds_F.close()

    # calc squared error for all forecasts individually 
    error_F  = (F_frac - O_frac)**2
    error_RF = (RF_frac - O_frac)**2

    # weighted spatial mean
    error_F  = misc.xy_mean(error_F)
    error_RF = misc.xy_mean(error_RF)

    # calc fss with bootstraping
    print('calculating fss with bootstrapping..')
    chunks_random = chunks.copy()
    mse_RF        = (1/nchunks)*error_RF.sum(dim='chunks').values
    for i in range(nshuffle):
        # calc mean square error of forecast
        mse_F = (1/chunks_random.size)*error_F.sel(chunks=chunks_random).sum(dim='chunks').values
        # calc fss                                                                                                                                                     
        fss[:,:,i] = 1.0 - mse_F/mse_RF
        # shuffle forecasts (chunks) randomly with replacement
        chunks_random = np.random.choice(chunks,nsample,replace='True')
    
    if write2file:
        print('writing to file..')
        if grid == '0.25x0.25': fss.to_netcdf(path_out+filename_hr_out)
        elif grid == '0.5x0.5': fss.to_netcdf(path_out+filename_lr_out)

        print('compress file to reduce space..') 
        if grid == '0.25x0.25': s2s.compress_file(comp_lev,3,filename_hr_out,path_out) 
        elif grid == '0.5x0.5': s2s.compress_file(comp_lev,3,filename_lr_out,path_out)

"""        
if write2file:
    print('combine high & low resolution files into one file..')
    ds_hr           = xr.open_dataset(path_out + filename_hr_out)
    ds_lr           = xr.open_dataset(path_out + filename_lr_out)
    ds              = xr.concat([ds_hr,ds_lr], 'time')
    ds.to_netcdf(path_out+filename_out)
    os.system('rm ' + path_out + filename_hr_out + ' ' + path_out + filename_lr_out)

#    print('compress file to reduce space..')
#    s2s.compress_file(comp_lev,3,filename_out,path_out)
#    ds.close()
#    ds_lr.close()
#    ds_hr.close()        
"""

misc.toc()


