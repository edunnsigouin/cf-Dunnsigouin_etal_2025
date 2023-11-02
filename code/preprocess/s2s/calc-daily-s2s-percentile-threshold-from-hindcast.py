"""
Calculates climatological percentiles per xy grid point from ecmwf 
smoothed hindcast data
"""

import numpy           as np
import xarray          as xr
from dask.diagnostics  import ProgressBar
from forsikring        import misc,s2s,config,verify
import os

def init_percentile(variable,time,units,dim,pval):
    """ 
    Initializes output array used below.  
    Written here to clean up code.    
    """
    data       = np.zeros((pval.size,time.size,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims       = ["pval","time","latitude","longitude"]
    coords     = dict(pval=pval,time=time,latitude=dim.latitude,longitude=dim.longitude)
    attrs      = dict(description='climatological percentile',units=units)
    name       = 'percentile'
    percentile = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    return percentile

# input ----------------------------------------------
time_flag           = 'timescale'                # time or timescale
variable            = 't2m24'                # tp24, rn24, mx24tp6, mx24rn6, mx24tpr
first_forecast_date = '20210104'              # first initialization date of forecast (either a monday or thursday)   
number_forecasts    = 1                    # number of forecast initializations 
season              = 'annual'
grids               = ['0.25x0.25']           # '0.25x0.25' or '0.5x0.5'
pval                = np.array([0.75,0.8,0.85,0.9,0.95,0.99]) # percentile values  
comp_lev            = 5                       # level of compression with nccopy (1-10)
write2file          = False
# ----------------------------------------------------

# get all dates for monday and thursday forecast initializations
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d').values
print(forecast_dates)

for grid in grids:
    for date in forecast_dates:
        
        misc.tic()
        print('\ncalculating percentiles for smoothed hindcast ' + date + ' and grid: ' + grid)
        
        # define stuff
        path_in           = config.dirs['s2s_hindcast_daily_smooth'] + variable + '/'
        path_out          = config.dirs['s2s_hindcast_daily_percentile'] + variable + '/'
        filename_in       = variable + '_' + grid + '_' + date + '.nc'
        filename_out      = variable + '_' + grid + '_' + date + '.nc'
        
        # read data                                                                                                                                               
        da = xr.open_dataset(path_in + filename_in)[variable]

        print(da)
        # convert time to timescale if applicable
        da = verify.resample_time_to_timescale(da, time_flag)

        print(da)
        """
        # calculate percentiles
        time                = da.time
        da                  = da.stack(temp_index=("number", "hdate")) # form sample out of number and hdate dims
        percentile          = init_percentile(variable,time,units,dim,pval)
        percentile[:,:,:,:] = da.quantile(pval,dim='temp_index').values
                    
        if write2file:
            s2s.to_netcdf_pack64bit(percentile,path_out + filename_out)
            s2s.compress_file(comp_lev,3,filename_out,path_out)
        """
        
        misc.toc()
