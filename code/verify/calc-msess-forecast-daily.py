"""
Calculates the mean-square-error skill score as a function of 
lead time for ecmwf forecasts. Reference forecasts are either 
era5 climatology or era5 persistence. Verification is era5.
Code includes bootstrapping of forecast mse to put error bars
on msess.
"""

import numpy            as np
import xarray           as xr
import os
from dask.diagnostics   import ProgressBar
from forsikring         import config,misc,s2s
import random

def init_msess(dim,nshuffle):
    """
    Initializes msess arrays used below.
    Written here to clean up code. 
    """
    data      = np.zeros((dim.ntime),dtype=np.float32)
    data_bs   = np.zeros((dim.ntime,nshuffle),dtype=np.float32)
    dims      = ["time"]
    dims_bs   = ["time","number"]
    coords    = dict(time=dim.time)
    coords_bs = dict(time=dim.time,number=np.arange(0,nshuffle,1))
    attrs     = dict(description='mean square error skill score of forecast',units='unitless')
    attrs_bs  = dict(description='mean square error skill score of forecast bootstrapped',units='unitless')
    name      = 'msess'
    name_bs   = 'msess_bs'
    msess     = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    msess_bs  = xr.DataArray(data=data_bs,dims=dims_bs,coords=coords_bs,attrs=attrs_bs,name=name_bs)
    return msess,msess_bs


def subselect_dim(dim,domain,grid):
    """ 
    kitchen sink function to sub-select appropriate data
    """
    # subselect lat-lon grid given domain and grid resololution
    if grid == '0.25x0.25':
        if domain == 'nordic':
            dim.latitude   = np.flip(np.arange(53,73.75,0.25))
            dim.longitude  = np.arange(0,35.25,0.25)
        elif domain == 'vestland':
            dim.latitude   = np.flip(np.arange(59,62.75,0.25))
            dim.longitude  = np.arange(4,8.75,0.25)
    elif grid == '0.5x0.5':
        if domain == 'nordic':
            dim.latitude   = np.flip(np.arange(53,74,0.5))
            dim.longitude  = np.arange(0,35.5,0.5)
        elif domain == 'vestland':
            dim.latitude   = np.flip(np.arange(59,63,0.5))
            dim.longitude  = np.arange(4,9,0.5)
    dim.nlatitude  = dim.latitude.size
    dim.nlongitude = dim.longitude.size

    return dim

# INPUT -----------------------------------------------
RF_flag           = 'clim'                   # clim or pers
time_flag         = 'time'                   # time or timescale
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'nordic'               # europe or norway only?
init_start        = '20210104'               # first initialization date of forecast (either a monday or thursday)
init_n            = 104                        # number of forecasts
grids             = ['0.25x0.25','0.5x0.5']  # '0.25x0.25' & '0.5x0.5'
nshuffle          = 10000                    # number of times to shuffle initialization dates for error bars
nsample           = 50
comp_lev          = 5
write2file        = True
# -----------------------------------------------------      

misc.tic()

# define stuff
init_dates       = s2s.get_init_dates(init_start,init_n)
init_dates       = init_dates.strftime('%Y-%m-%d').values
chunks           = np.arange(0,init_n,1)
path_in_F        = config.dirs['forecast_daily'] + variable + '/'
path_in_O        = config.dirs['era5_model_daily'] + variable + '/'
path_in_RF       = config.dirs['era5_model_' + RF_flag] + variable + '/'
path_out         = config.dirs['calc_forecast_daily']
filename_hr_out  = time_flag + '_msess_' + variable + '_' + 'forecast_' + RF_flag + \
                   '_0.25x0.25_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
filename_lr_out  = time_flag + '_msess_' + variable + '_' + 'forecast_' + RF_flag + \
	           '_0.5x0.5_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
filename_out     = time_flag + '_msess_' + variable + '_' + 'forecast_' + RF_flag + \
	           '_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'

for grid in grids:

    print('\ncalculating msess for ' + grid + '...')
    
    # get data dimensions
    dim = s2s.get_dim(grid,time_flag)
    dim = subselect_dim(dim,domain,grid)

    # initialize msess
    [msess,msess_bs] = init_msess(dim,nshuffle)
    
    # define input filenames
    filenames_O  =  path_in_O + variable + '_' + grid + '_' + init_dates + '.nc'
    filenames_F  =  path_in_F + variable + '_' + grid + '_' + init_dates + '.nc'
    filenames_RF =  path_in_RF + variable + '_' + grid + '_' + init_dates + '.nc'

    # read in files     
    O  = xr.open_mfdataset(filenames_O,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks')[variable]
    F  = xr.open_mfdataset(filenames_F,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks').mean(dim='number')[variable] # ensemble mean
    RF = xr.open_mfdataset(filenames_RF,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks')[variable]
    
    # sub-select specific domain
    O  = O.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
    F  = F.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
    RF = RF.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')

    # resample time into timescales if required 
    O  = s2s.time_2_timescale(O,time_flag)
    F  = s2s.time_2_timescale(F,time_flag)
    RF = s2s.time_2_timescale(RF,time_flag)
    
    # calculate explicitely 
    with ProgressBar():
        O  = O.compute()
        F  = F.compute()
        RF = RF.compute()
        
    # calc squared error for all Fs individually
    F_error  = (F - O)**2
    RF_error = (RF - O)**2

    RF.close()
    O.close()
    F.close()

    # weighted spatial mean
    F_error  = misc.xy_mean(F_error)
    RF_error = misc.xy_mean(RF_error)

    # calc fss with bootstraping   
    print('calculating msess with bootstrapping..')
    [msess,msess_bs] = s2s.calc_msess_bootstrap(msess,msess_bs,RF_error,F_error,nshuffle,nsample,chunks)

    # postprocessing 
    ds = xr.merge([msess,msess_bs])

    if write2file:
        print('writing to file..')
        if grid == '0.25x0.25': ds.to_netcdf(path_out+filename_hr_out)
        elif grid == '0.5x0.5': ds.to_netcdf(path_out+filename_lr_out)

        print('compress file to reduce space..')
        if grid == '0.25x0.25': s2s.compress_file(comp_lev,3,filename_hr_out,path_out)
        elif grid == '0.5x0.5': s2s.compress_file(comp_lev,3,filename_lr_out,path_out)
            

# combine low and high resolution files into one file if both exist 
if (os.path.exists(path_out + filename_hr_out)) and (os.path.exists(path_out + filename_lr_out)):
    if write2file:
        print('combine high & low resolution files into one file..')
        ds_hr           = xr.open_dataset(path_out + filename_hr_out)
        ds_lr           = xr.open_dataset(path_out + filename_lr_out)
        ds              = xr.concat([ds_hr,ds_lr], 'time')
        ds.to_netcdf(path_out+filename_out)
        os.system('rm ' + path_out + filename_hr_out + ' ' + path_out + filename_lr_out)

        print('compress file to reduce space..')
        s2s.compress_file(comp_lev,3,filename_out,path_out)
        ds.close()
        ds_lr.close()
        ds_hr.close()

    
misc.toc()


