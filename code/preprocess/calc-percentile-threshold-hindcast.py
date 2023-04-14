"""
Calculates climatological percentiles per xy grid point from ecmwf hindcast data
"""

import numpy           as np
import xarray          as xr
from dask.diagnostics  import ProgressBar
from forsikring        import misc,s2s,config
import os

def init_percentile(variable,time,units,dim,pval,nshuffle):
    """ 
    Initializes output array used below.  
    Written here to clean up code.    
    """
    number     = np.arange(0,nshuffle)
    data       = np.zeros((nshuffle,pval.size,time.size,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims       = ["number","pval","time","latitude","longitude"]
    coords     = dict(number=number,pval=pval,time=time,latitude=dim.latitude,longitude=dim.longitude)
    attrs      = dict(description='climatological percentile',units=units)
    name       = 'percentile'
    percentile = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    return percentile

# input ----------------------------------------------
variable      = 'tp24'                # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
init_start    = '20210104'              # first initialization date of forecast (either a monday or thursday)   
init_n        = 1                     # number of forecast initializations 
grids         = ['0.25x0.25']           # '0.25x0.25' or '0.5x0.5'
pval          = np.array([0.9]) # percentile values  
nsample       = 100
nshuffle      = 10
comp_lev      = 5                       # level of compression with nccopy (1-10)
write2file    = False
# ----------------------------------------------------

# get all dates for monday and thursday forecast initializations
init_dates = s2s.get_init_dates(init_start,init_n)

for date in init_dates:
    
    misc.tic()

    for grid in grids:

        print('\ncalculating percentiles for hindcast ' + date.strftime('%Y-%m-%d') + ' and grid: ' + grid)
        
        # define stuff
        dim             = s2s.get_dim(grid,'time')
        datestring      = date.strftime('%Y-%m-%d')
        filename_in     = variable + '_' + grid + '_' + datestring + '.nc'
        filename_out    = 'xyt_percentile_' + variable + '_' + grid + '_' + datestring + '.nc'
        path_in         = config.dirs['hindcast_daily'] + variable + '/'
        path_out        = config.dirs['hindcast_percentile'] + variable + '/'
        ds              = xr.open_dataset(path_in + filename_in)

        # ONE WAY TO SPEED THE BOOTSTRAPPING IS TO DO IN IN NUMPY NOT XARRAY
        # calculate percentiles
        units               = ds[variable].attrs['units']
        time                = ds.time
        ds                  = ds.stack(temp_index=("number", "hdate")) # form sample out of number and hdate dims
        percentile          = init_percentile(variable,time,units,dim,pval,nshuffle)
        chunks              = ds['temp_index'].values
        chunks_random       = chunks.copy()
        for i in range(nshuffle):
            print(i)
            percentile[i,:,:,:,:] = ds[variable].sel(temp_index=chunks_random).quantile(pval,dim='temp_index').values
            chunks_random         = np.random.choice(chunks,nsample,replace='True')
        
        # mean over boot-strapped samples
        percentile = percentile.mean(dim='number')
        
        if write2file:
            s2s.to_netcdf_pack64bit(percentile,path_out + filename_out)
            s2s.compress_file(comp_lev,3,filename_out,path_out)
            
    misc.toc()
