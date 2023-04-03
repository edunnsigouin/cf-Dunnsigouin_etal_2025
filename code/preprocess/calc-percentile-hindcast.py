"""
calculates climatological percentiles per xy grid point from ecmwf hindcast data
NOTE: here I calculate the statistics over all of the hindcasts in one year (104) 
"""

import numpy           as np
import xarray          as xr
from dask.diagnostics  import ProgressBar
from forsikring        import misc,s2s,config


def init_percentile(variable,units,dim,pval):
    """ 
    Initializes output array used below.  
    Written here to clean up code.    
    """
    data       = np.zeros((pval.size,dim.time.size,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims       = ["pval","time","latitude","longitude"]
    coords     = dict(pval=pval,time=dim.time,latitude=dim.latitude,longitude=dim.longitude)
    attrs      = dict(description='climatological percentile',units=units)
    name       = 'percentile'
    percentile = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    return percentile


# input ----------------------------------------------
variable      = 'tp24'                # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
product       = 'hindcast'              # hindcast or forecast
init_start    = '20210104'              # first initialization date of forecast (either a monday or thursday)   
init_n        = 1                     # number of forecast initializations 
grids         = ['0.25x0.25']           # '0.25x0.25' or '0.5x0.5'
pval          = np.array([0.5,0.75,0.90,0.95,0.99]) # percentile values  
comp_lev      = 5                       # level of compression with nccopy (1-10)
write2file    = False
# ----------------------------------------------------

# get all dates for monday and thursday forecast initializations                                                                                                                                    
init_dates = s2s.get_init_dates(init_start,init_n)
    
for grid in grids:
    for date in init_dates:

        misc.tic()
        
        dim           = s2s.get_dim(grid,'time')
        datestring    = date.strftime('%Y-%m-%d')
        filename_in   = variable + '_' + grid + '_' + datestring + '.nc'
        filename_out  = 'xy_percentile_' + variable + '_' + grid + '_' + + '.nc'
        path_in       = config.dirs[product + '_daily'] + variable + '/'
        ds            = xr.open_dataset(path_in + filename_in)

        # calculate percentiles
        units               = ds[variable].attrs['units']
        ds                  = ds.stack(temp_index=("number", "hdate")) # form sample out of number and hdate
        percentile          = init_percentile(variable,units,dim,pval)
        percentile[:,:,:,:] = ds[variable].quantile(pval,dim='temp_index').values

        if write2file:
            percentile.to_netcdf(path_out + filename_out)
            s2s.compress_file(comp_lev,3,filename_out,path_out)

        misc.toc()
