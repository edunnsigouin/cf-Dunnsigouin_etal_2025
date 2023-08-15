"""
Converts era5 model format data into anomaly relative
to climatological mean derived from previous years
e.g., converts era5 model format data (lead time,lat,lon) for year 2021
into anomaly derived from years 2001-2020
in format (dayofyear,lat,lon).
 
NOTE: this is done for both era5 daily data in model format
(files structured per initialization date of forecast)

NOTE2: Currrently, clim mean is simple mean by calendar day
of the past twently years. Should each calendar day mean be calculated
in a way similar to percentile thresholds? i.e. each calendar day +-15 days around
that day? 
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
    attrs      = dict(description='anomalies from climatology',units='unitless')
    name       = variable
    anomaly    = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    return anomaly

# INPUT -----------------------------------------------
time_flag         = 'time'                   # time or timescale
data_flag         = 'daily'                  # daily,clim,pers
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
init_start        = '20210104'               # first initialization date of forecast (either a monday or thursday)
init_n            = 104                      # number of forecasts 
grids             = ['0.5x0.5']  # '0.25x0.25' & '0.5x0.5'
comp_lev          = 5                        # compression level (0-10) of netcdf putput file
write2file        = True
# -----------------------------------------------------

misc.tic()

# define stuff  
years        = np.arange(int(init_start[:4])-20,int(init_start[:4])) # hindcast years for forecasts
init_dates   = s2s.get_init_dates(init_start,init_n)
init_dates   = init_dates.strftime('%Y-%m-%d').values
path_in_O    = config.dirs['era5_forecast_' + data_flag] + variable + '/'
path_in_C    = config.dirs['era5_forecast_clim'] + variable + '/'
path_out     = config.dirs['era5_forecast_anomaly'] + variable + '/'

for grid in grids:
    for date in init_dates:

        print('\nconverting forecast to anomaly ' + variable + ' for ' + grid + ' and initialization ' + date)
        
        # define stuff
        dim           = s2s.get_dim(grid,'daily')
        filename_O    = variable + '_' + grid + '_' + date + '.nc'
        filename_C    = variable + '_' + grid + '_' + date + '.nc'
        filename_out  = variable + '_' + time_flag + '_' + grid + '_' + date + '.nc'
        
        # read forecast and climatology in forecast format
        da_O = xr.open_dataset(path_in_O + filename_O)[variable]
        da_C = xr.open_dataset(path_in_C + filename_C)[variable]

        # resample time into timescales if required
        da_O = s2s.time_2_timescale(da_O,time_flag,datetime64=True)
        da_C = s2s.time_2_timescale(da_C,time_flag,datetime64=True)

        # calculate anomalies from climatology
        anomaly = init_anomaly(variable,dim,da_O.time)
        anomaly = da_O - da_C

        # modify metadata
        if variable == 'tp24':
            anomaly.attrs['units']     = 'm'
            anomaly.attrs['long_name'] = 'daily accumulated precipitation'
        if variable == 'rn24':
            anomaly.attrs['units']     = 'm'
            anomaly.attrs['long_name'] = 'daily accumulated rainfall'
        if variable == 'mx24tpr':
            anomaly.attrs['units']     = 'kg m**-2 s**-1'
            anomaly.attrs['long_name'] = 'daily maximum timestep precipitation rate'
        if variable == 'mx24tp6':
            anomaly.attrs['units']     = 'm'
            anomaly.attrs['long_name'] = 'daily maximum 6 hour accumulated precipitation'
        if variable == 'mx24rn6':
            anomaly.attrs['units']     = 'm'
            anomaly.attrs['long_name'] = 'daily maximum 6 hour accumulated rainfall'
            
        # write output     
        if write2file:
            anomaly.to_netcdf(path_out + filename_out)
            s2s.compress_file(comp_lev,3,filename_out,path_out) 
        
        da_O.close()
        da_C.close()

misc.toc()


