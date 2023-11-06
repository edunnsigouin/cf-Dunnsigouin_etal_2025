"""
Calculates climatological percentiles per xy grid point from ecmwf 
smoothed hindcast data. Estimate is taken from sample of 20 years x 
11 ensemble members for each grid point, calendar day, and spatial smoothing.
"""

import numpy           as np
import xarray          as xr
from dask.diagnostics  import ProgressBar
from forsikring        import misc,s2s,config,verify
import os


def initialize_quantile_array(variable,box_sizes,time_flag,dim,pval):
    """ 
    Initializes output array used below.  
    Written here to clean up code.    
    """

    if time_flag == 'time':
        time = dim.time
    elif time_flag == 'timescale':
        time = dim.timescale
        
    data       = np.zeros((box_sizes.size,pval.size,time.size,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims       = ["box_size","pval","time","latitude","longitude"]
    coords     = dict(box_size=box_sizes,pval=pval,time=time,latitude=dim.latitude,longitude=dim.longitude)
    
    if variable == 't2m24':
        units       = 'K'
        description = 'climatological quantiles of 2-meter temperature'
    elif variable == 'tp24':
        units       = 'm'
        description = 'climatological quantiles of daily accumulated precipitation'
        
    attrs      = dict(description=description,units=units)
    name       = 'quantile'
    return xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)


# input ----------------------------------------------
time_flag           = 'time'                # time or timescale
variable            = 't2m24'                # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
first_forecast_date = '20210104'              # first initialization date of forecast (either a monday or thursday)   
number_forecasts    = 104                    # number of forecast initializations 
season              = 'annual'
grid                = '0.5x0.5'              # '0.25x0.25' or '0.5x0.5'
box_sizes           = np.arange(1,61,2)        # smoothing box size in grid points per side. Must be odd!
pval                = np.array([0.9]) # percentile values  
comp_lev            = 5                        # level of compression with nccopy (1-10)
write2file          = True
# ----------------------------------------------------

# get all dates for monday and thursday forecast initializations
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d').values
dim            = misc.get_dim(grid,time_flag)
print(forecast_dates)

for date in forecast_dates:

    misc.tic()
    print('\ncalculating percentiles for smoothed hindcast ' + date + ' and grid: ' + grid)
    quantile = initialize_quantile_array(variable,box_sizes,time_flag,dim,pval)
    
    for bs, box_size in enumerate(box_sizes):

        print('smoothing box size = ' + str(box_size))

        # define stuff
        path_in      = config.dirs['s2s_hindcast_daily_smooth'] + variable + '/'
        path_out     = config.dirs['s2s_hindcast_daily_percentile'] + variable + '/'
        filename_in  = variable + '_' + grid + '_' + date + '.nc'
        filename_out = 'quantile_' + variable + '_' + time_flag + '_' + grid + '_' + date + '.nc'
    
        # read data                                                                                                                                               
        da = xr.open_dataset(path_in + filename_in)[variable].isel(box_size=bs).drop('box_size')

        # convert time to timescale if applicable
        da = verify.resample_time_to_timescale(da, time_flag)

        # calculate percentiles
        quantile['time']     = da['time'] # match time dimensions
        quantile[bs,:,:,:,:] = np.quantile(da.stack(temp_index=("number", "hdate")).values,pval,axis=3) # using numpy function for speed  
        
        da.close()
        
    if write2file: misc.to_netcdf_with_compression(quantile,comp_lev,path_out,filename_out)

    misc.toc()
    
