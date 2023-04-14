"""
Converts era5 model format data into binary if over/under
a climatological percentile threshold derived from previous years
e.g., converts era5 model format data (lead time,lat,lon) for year 2021
into binary if above/below percentile thresholds derived from years 2001-2020
in format (dayofyear,lat,lon).
 
NOTE: this is done for both era5 daily, climatology and persistence data in model format
(files structured per initialization date of forecast)

NOTE2: the climatological mean precip can be BIGGER than for example percentiles > 75. 
This occurs because the distribution can have a long tail, skewing the mean towards the
extremes. Thus, the output of this script is not just zero everywhere.
"""

import numpy  as np
import xarray as xr
import os
from dask.diagnostics  import ProgressBar
from forsikring        import misc,s2s,config
from matplotlib        import pyplot as plt

def init_binary(variable,dim,time,pvals):
    """ 
    Initializes output array used below. 
    Written here to clean up code.                                                                                                                      
    """
    data       = np.zeros((pvals.size,dim.ntime,dim.nlatitude,dim.nlongitude),dtype=np.int16)
    dims       = ["pval","time","latitude","longitude"]
    coords     = dict(pval=pvals,time=time,latitude=dim.latitude,longitude=dim.longitude)
    attrs      = dict(description='binary values over percentile threshold',units='unitless')
    name       = variable
    binary     = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    return binary

# INPUT -----------------------------------------------
data_flag         = 'clim'                   # daily,clim,pers
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
years             = np.arange(2001,2021)    # percentile thrshold derived years
init_start        = '20210104'               # first initialization date of forecast (either a monday or thursday)
init_n            = 104                      # number of forecasts 
grids             = ['0.25x0.25','0.5x0.5']            # '0.25x0.25' & '0.5x0.5'
pvals             = np.array([0.75,0.8,0.85,0.9,0.95,0.99]) # percentile thresholds
comp_lev          = 5                        # compression level (0-10) of netcdf putput file
write2file        = True
# -----------------------------------------------------

misc.tic()

# define stuff  
init_dates   = s2s.get_init_dates(init_start,init_n)
init_dates   = init_dates.strftime('%Y-%m-%d').values
path_in_O    = config.dirs['era5_forecast_' + data_flag] + variable + '/'
path_in_pval = config.dirs['era5_percentile'] + variable + '/'
path_out     = config.dirs['era5_forecast_' + data_flag + '_binary'] + variable + '/'

for grid in grids:

    # read in thresholds 
    filename_pval = 'xyt_percentile_' + variable + '_' + grid + '_' + str(years[0]) + '-' + str(years[-1]) + '.nc'
    da_pval       = xr.open_dataset(path_in_pval + filename_pval)['percentile']

    for date in init_dates:

        print('\nconverting to binary ' + variable + ' for ' + grid + ' and initialization ' + date)
        
        # define stuff
        dim           = s2s.get_dim(grid,'daily')
        filename_O    = variable + '_' + grid + '_' + date + '.nc'
        filename_out  = filename_O
        
        # read data
        da_O = xr.open_dataset(path_in_O + filename_O)[variable]

        # convert to binary
        binary = init_binary(variable,dim,da_O.time,pvals)
        for pval in range(0,pvals.size):
            for t in range(0,dim.ntime):
                doy                = da_O['time.dayofyear'][t].values - 1 # potential problem here with leap year days (e.g. 2020) !!!!!!!!!!!!!!!!!!!!!!!!!!
                threshold          = da_pval[:,doy,:,:].sel(pval=pvals[pval],method='nearest').values
                binary[pval,t,:,:] = (da_O[t,:,:].values >= threshold[:,:]).astype(np.int16)
            
        # write output     
        if write2file:
            binary.to_netcdf(path_out + filename_out)
            s2s.compress_file(comp_lev,3,filename_out,path_out) 

        da_O.close()
    da_pval.close()
misc.toc()


