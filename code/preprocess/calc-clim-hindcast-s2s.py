"""
Calculates climatology per xy grid point from ecmwf hindcast data
"""

import numpy           as np
import xarray          as xr
from dask.diagnostics  import ProgressBar
from forsikring        import misc,s2s,config
import os

def init_clim(variable,time,units,dim):
    """ 
    Initializes output array used below.  
    Written here to clean up code.    
    """
    data       = np.zeros((time.size,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims       = ["time","latitude","longitude"]
    coords     = dict(time=time,latitude=dim.latitude,longitude=dim.longitude)
    attrs      = dict(description='climatological mean',units=units)
    name       = 'clim'
    percentile = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    return percentile

# input ----------------------------------------------
time_flag     = 'time'                # time or timescale
variable      = 'tp24'                # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
init_start    = '20210104'            # first initialization date of forecast (either a monday or thursday)   
init_n        = 104                     # number of forecast initializations 
grids         = ['0.25x0.25','0.5x0.5']           # '0.25x0.25' or '0.5x0.5'
comp_lev      = 5                       # level of compression with nccopy (1-10)
write2file    = True
# ----------------------------------------------------

# get all dates for monday and thursday forecast initializations
init_dates = s2s.get_init_dates(init_start,init_n)

for grid in grids:
    for date in init_dates:
        
        misc.tic()
        print('\ncalculating climatology for hindcast ' + date.strftime('%Y-%m-%d') + ' and grid: ' + grid)
        
        # define stuff
        dim             = s2s.get_dim(grid,'time')
        datestring      = date.strftime('%Y-%m-%d')
        filename_in     = variable + '_' + grid + '_' + datestring + '.nc'
        filename_out    = 'xy_' + time_flag + '_clim_' + variable + '_' + grid + '_' + datestring + '.nc'
        path_in         = config.dirs['hindcast_daily'] + variable + '/'
        path_out        = config.dirs['hindcast_clim'] + variable + '/'
        da              = xr.open_dataset(path_in + filename_in)[variable]
        units           = da.attrs['units']

        # convert time to timescale if applicable
        da = s2s.time_2_timescale(da,time_flag,datetime64=True)
        
        # calculate percentiles
        time                = da.time
        da                  = da.stack(temp_index=("number", "hdate")) # form sample out of number and hdate dims
        clim                = init_clim(variable,time,units,dim)
        clim[:,:,:]         = da.mean(dim='temp_index').values
                    
        if write2file:
            s2s.to_netcdf_pack64bit(clim,path_out + filename_out)
            s2s.compress_file(comp_lev,3,filename_out,path_out)

        misc.toc()

