"""
Converts ecmwf forecast data into binary if over/under
a climatological percentile threshold derived from corresponding hindcast
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
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
init_start        = '20210104'               # first initialization date of forecast (either a monday or thursday)
init_n            = 104                        # number of forecasts 
grids             = ['0.25x0.25','0.5x0.5']            # '0.25x0.25' & '0.5x0.5'
pvals             = np.array([0.75,0.8,0.85,0.9,0.95,0.99]) # percentile thresholds
comp_lev          = 5                        # compression level (0-10) of netcdf putput file
write2file        = True
# -----------------------------------------------------

misc.tic()

# define stuff  
init_dates   = s2s.get_init_dates(init_start,init_n)
init_dates   = init_dates.strftime('%Y-%m-%d').values
path_in_F    = config.dirs['forecast_model_daily'] + variable + '/'
path_in_pval = config.dirs['hindcast_percentile'] + variable + '/'
path_out     = config.dirs['forecast_binary_daily'] + variable + '/'

for grid in grids:
    for date in init_dates:

        print('\nconverting to binary for ' + grid + ' and initialization ' + date)
        
        # define stuff
        dim           = s2s.get_dim(grid,'daily')
        filename_F    = variable + '_' + grid + '_' + date + '.nc'
        filename_pval = 'xyt_percentile_' + variable + '_' + grid + '_' + date + '.nc'
        filename_out  = filename_F
        
        # read data
        da_F          = xr.open_dataset(path_in_F + filename_F)[variable].mean(dim='number') # ensemble mean
        da_pval       = xr.open_dataset(path_in_pval + filename_pval)['percentile']
        
        # convert to binary
        binary = init_binary(variable,dim,da_F.time,pvals)
        for pval in range(0,pvals.size):
            threshold          = da_pval.sel(pval=pvals[pval],method='nearest').values
            binary[pval,:,:,:] = (da_F.values >= threshold).astype(np.int16)

        # write output     
        if write2file:
            binary.to_netcdf(path_out + filename_out)
            s2s.compress_file(comp_lev,3,filename_out,path_out) 

        da_F.close()
        da_pval.close()

misc.toc()


