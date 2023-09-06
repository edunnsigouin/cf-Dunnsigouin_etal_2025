"""
Converts ecmwf forecast data into anomalies relative to 
corresponding hindcast climatology.
"""

import numpy  as np
import xarray as xr
import os
from dask.diagnostics  import ProgressBar
from forsikring        import misc,s2s,config
from matplotlib        import pyplot as plt

def init_anomaly(variable,dim,time):
    """ 
    Initializes output array used below. 
    Written here to clean up code.                                                                                                                      
    """
    data       = np.zeros((time.size,dim.nlatitude,dim.nlongitude),dtype=np.int16)
    dims       = ["time","latitude","longitude"]
    coords     = dict(time=time,latitude=dim.latitude,longitude=dim.longitude)
    attrs      = dict(description='forecast anomalies relative to hindcast climatology',units='unitless')
    name       = variable
    anomaly     = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    return anomaly

# INPUT -----------------------------------------------
time_flag         = 'time'                   # time or timescale
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
init_start        = '20200102'               # first initialization date of forecast (either a monday or thursday)
init_n            = 105                      # number of forecasts 
grids             = ['0.25x0.25']  # '0.25x0.25' & '0.5x0.5'
comp_lev          = 5                        # compression level (0-10) of netcdf putput file
write2file        = True
# -----------------------------------------------------

misc.tic()

# define stuff  
init_dates   = s2s.get_init_dates(init_start,init_n)
init_dates   = init_dates.strftime('%Y-%m-%d').values
path_in_F    = config.dirs['forecast_daily'] + variable + '/'
path_in_HC   = config.dirs['hindcast_clim'] + variable + '/'
path_out     = config.dirs['forecast_daily_anomaly'] + variable + '/'

for grid in grids:
    for date in init_dates:

        print('\nconverting forecast to anomaly for ' + grid + ' and initialization ' + date)
        
        # define stuff
        dim           = s2s.get_dim(grid,'time')
        filename_F    = variable + '_' + grid + '_' + date + '.nc'
        filename_HC   = variable + '_' + grid + '_' + date + '.nc'
        filename_out  = variable + '_' + time_flag + '_' + grid + '_' + date + '.nc'
        
        # read data
        da_F    = xr.open_dataset(path_in_F + filename_F)[variable].mean(dim='number') # ensemble mean
        da_HC   = xr.open_dataset(path_in_HC + filename_HC)[variable]

        # resample time into timescales if required
        da_F  = s2s.time_2_timescale(da_F,time_flag,datetime64=True)
        da_HC = s2s.time_2_timescale(da_HC,time_flag,datetime64=True)
        
	# calculate anomalies from climatology
        anomaly = init_anomaly(variable,dim,da_F.time)
        anomaly = da_F - da_HC

        # modify metadata
        if variable == 'tp24':
            anomaly.attrs['units']     = 'm'
            anomaly.attrs['long_name'] = 'anomalies of daily accumulated precipitation'
        if variable == 'rn24':
            anomaly.attrs['units']     = 'm'
            anomaly.attrs['long_name'] = 'anomalies of daily accumulated rainfall'
        if variable == 'mx24tpr':
            anomaly.attrs['units']     = 'kg m**-2 s**-1'
            anomaly.attrs['long_name'] = 'anomalies of daily maximum timestep precipitation rate'
        if variable == 'mx24tp6':
            anomaly.attrs['units']     = 'm'
            anomaly.attrs['long_name'] = 'anomalies of daily maximum 6 hour accumulated precipitation'
        if variable == 'mx24rn6':
            anomaly.attrs['units']     = 'm'
            anomaly.attrs['long_name'] = 'anomalies of daily maximum 6 hour accumulated rainfall'
            
        # write output     
        if write2file:
            anomaly.to_netcdf(path_out + filename_out)
            s2s.compress_file(comp_lev,3,filename_out,path_out) 

        da_F.close()
        da_HC.close()

misc.toc()


