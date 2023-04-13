"""
Calculates the fractional skill score as a function of                                                                                                        
lead time and neighborhood size for ecmwf forecasts. 

Reference forecasts are either era5 climatology or era5 persistence. 
Verification is era5. Code includes bootstrapping of 
forecast mse to put error bars on fss. 

Input is pre-processed
data in model-format converted to binary.
"""

import numpy  as np
import xarray as xr
import os
from dask.diagnostics  import ProgressBar
from forsikring        import misc,s2s,config
import random
from matplotlib        import pyplot as plt


def init_frac(dim,NH,chunks):
    """
    Initializes fraction array used below.
    Written here to clean up code.
    """
    data   = np.zeros((NH.size,chunks.size,dim.ntime,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims   = ["neighborhood","chunks","time","latitude","longitude"]
    coords = dict(neighborhood=NH,chunks=chunks,time=dim.time,latitude=dim.latitude,longitude=dim.longitude)
    name   = 'frac'
    frac   = xr.DataArray(data=data,dims=dims,coords=coords,name=name)
    return frac

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

def subselect_dim(dim,domain,ltime,grid,NH,time_flag):
    """ 
    kitchen sink function to sub-select appropriate data  
    """
    # subselect lat-lon grid given domain and grid resolution
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

    # specify selected lead times if lead times are daily (not timescale)
    # also subselect lead times corresponding to grid resolution
    if time_flag == 'time':
        dim.time = ltime
        if grid == '0.5x0.5':
            dim.time = dim.time[dim.time > 15]
        elif grid == '0.25x0.25':
            dim.time = dim.time[dim.time <= 15]
        dim.ntime = dim.time.size

    # match neighborhood sizes between high and low resolution data
    # i.e. grid neighborhood size 5 in hr data is equivalent to 3 in lr data.
    if grid == '0.5x0.5':
        NH_grid = np.copy(np.ceil(NH/2)).astype(int)
    elif grid == '0.25x0.25':
        NH_grid = np.copy(NH).astype(int)

    return dim,NH_grid



# INPUT -----------------------------------------------
RF_flag           = 'clim'                   # clim or pers
time_flag         = 'time'                   # time or timescale
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'europe'                 # europe or norway only?
init_start        = '20210104'               # first initialization date of forecast (either a monday or thursday)
init_n            = 104                        # number of forecasts 
grids             = ['0.25x0.25','0.5x0.5']            # '0.25x0.25' & '0.5x0.5'
pval              = 0.9                      # percentile threshold
NH                = np.array([1,9,19,29,39,49,59,69,79,89,99])  # neighborhood size in grid points per side
ltime             = np.arange(1,16,1)  # forecast lead times to calculate
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
path_in_F        = config.dirs['forecast_binary_daily'] + variable + '/'
path_in_O        = config.dirs['era5_binary_daily'] + variable + '/'
path_in_RF       = config.dirs['era5_binary_' + RF_flag] + variable + '/'
path_out         = config.dirs['verify_forecast_daily']
filename_hr_out  = time_flag + '_fss_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
                   'pval_' + str(pval) + '_0.25x0.25_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
filename_lr_out  = time_flag + '_fss_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
                   'pval_' + str(pval) + '_0.5x0.5_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'
filename_out     = time_flag + '_fss_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
                   'pval_' + str(pval) + '_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'

for grid in grids:

    print('\ncalculating fss for ' + grid + '...')
    
    # get data dimensions
    dim = s2s.get_dim(grid,time_flag)

    # kitchen sink function to sub-select appropriate data dimensions
    # given input options above
    [dim,NH_grid] = subselect_dim(dim,domain,ltime,grid,NH,time_flag)

    if dim.time.size > 0: # only calc stuff if lead time is in lr or hr data

        # initialize arrays                                                                                                    
        [fss,fss_bs] = init_fss(dim,NH_grid,nshuffle)
        O_frac       = init_frac(dim,NH_grid,chunks)
        F_frac       = init_frac(dim,NH_grid,chunks)
        RF_frac      = init_frac(dim,NH_grid,chunks)

        # define input filenames
        filenames_O  =  path_in_O + variable + '_' + grid + '_' + init_dates + '.nc'
        filenames_F  =  path_in_F + variable + '_' + grid + '_' + init_dates + '.nc'
        filenames_RF =  path_in_RF + variable + '_' + grid + '_' + init_dates + '.nc'

        # read in files to dataarray
        O  = xr.open_mfdataset(filenames_O,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks')[variable]
        F  = xr.open_mfdataset(filenames_F,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks')[variable] # ensemble mean 
        RF = xr.open_mfdataset(filenames_RF,preprocess=s2s.preprocess,combine='nested',concat_dim='chunks')[variable]

        # sub-select specific domain, lead times and percentile threshold
        O  = O.sel(latitude=dim.latitude,longitude=dim.longitude,time=dim.time,pval=pval,method='nearest')
        F  = F.sel(latitude=dim.latitude,longitude=dim.longitude,time=dim.time,pval=pval,method='nearest')
        RF = RF.sel(latitude=dim.latitude,longitude=dim.longitude,time=dim.time,pval=pval,method='nearest')

        # resample time into timescales if required 
        O  = s2s.time_2_timescale(O,time_flag)
        F  = s2s.time_2_timescale(F,time_flag)
        RF = s2s.time_2_timescale(RF,time_flag)

        # calculate dask arrays explicitely
        print('reading & postprocessing input data..')
        with ProgressBar():
            O  = O.compute()
            F  = F.compute()
            RF = RF.compute()

        # calculate fractions
        # Should there be a cosine weighting when applying filter in y?
        print('calculating observation fractions...')
        O_frac[:,:,:,:,:]  = s2s.calc_frac_RL08MWR(NH_grid,O)
        print('calculating forecast fractions...')
        F_frac[:,:,:,:,:]  = s2s.calc_frac_RL08MWR(NH_grid,F)
        print('calculating reference forecast fractions...')
        RF_frac[:,:,:,:,:] = s2s.calc_frac_RL08MWR(NH_grid,RF)
    
        O.close()
        F.close()
        RF.close()

        print('calculating errors..')
        # calc squared error for all forecasts individually 
        F_error  = (F_frac - O_frac)**2
        RF_error = (RF_frac - O_frac)**2

        # weighted spatial (x,y) mean
        F_error  = misc.xy_mean(F_error)
        RF_error = misc.xy_mean(RF_error)

        # calc fss with bootstraping
        print('calculating fss with bootstrapping..')
        [fss,fss_bs] = s2s.calc_fss_bootstrap(fss,fss_bs,RF_error,F_error,nshuffle,nsample,chunks,NH_grid)

        # postprocessing
        ds = xr.merge([fss,fss_bs])
        if grid == '0.5x0.5': ds['neighborhood'] = NH
        
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


