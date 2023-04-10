"""
Converts era5 model format data into binary if over/under
a climatological percentile threshold derived from previous years
e.g., converts era5 model format data (lead time,lat,lon) for year 2021
into binary if above/below percentile thresholds derived from years 2001-2020
in format (dayofyear,lat,lon). 
"""

import numpy  as np
import xarray as xr
import os
from dask.diagnostics  import ProgressBar
from forsikring        import misc,s2s,config
from matplotlib        import pyplot as plt


def init_binary(variable,dim,time):
    """ 
    Initializes output array used below. 
    Written here to clean up code.                                                                                                                      
    """
    data       = np.zeros((dim.ntime,dim.nlatitude,dim.nlongitude),dtype=np.int16)
    dims       = ["time","latitude","longitude"]
    coords     = dict(time=time,latitude=dim.latitude,longitude=dim.longitude)
    attrs      = dict(description='binary values over percentile threshold',units='unitless')
    name       = variable
    binary     = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    return binary


# INPUT -----------------------------------------------
time_flag         = 'time'                   # time or timescale
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
years             = np.arange(2001,2021)    # percentile thrshold derived years
init_start        = '20210104'               # first initialization date of forecast (either a monday or thursday)
init_n            = 104                        # number of forecasts 
grids             = ['0.25x0.25']            # '0.25x0.25' & '0.5x0.5'
pval              = 0.9
comp_lev          = 5                        # compression level (0-10) of netcdf putput file
write2file        = True
# -----------------------------------------------------

misc.tic()

# define stuff  
init_dates   = s2s.get_init_dates(init_start,init_n)
init_dates   = init_dates.strftime('%Y-%m-%d').values
path_in_O    = config.dirs['era5_model_daily'] + variable + '/'
path_in_pval = config.dirs['era5_percentile'] + variable + '/'
path_out     = config.dirs['era5_binary'] + variable + '/' + str(pval) + '/'

for grid in grids:
    for date in init_dates:
        
        print('\nconverting to binary for ' + grid + ' and initialization ' + date + ' ...')
    
        # define stuff
        dim           = s2s.get_dim(grid,time_flag)
        filename_O    = variable + '_' + grid + '_' + date + '.nc'
        filename_pval = 'xyt_percentile_' + variable + '_' + grid + '_' + str(years[0]) + '-' + str(years[-1]) + '.nc'
        filename_out  = filename_O

        print(path_out + filename_out)
        
        # read data
        da_O    = xr.open_dataset(path_in_O + filename_O)[variable]
        da_pval = xr.open_dataset(path_in_pval + filename_pval).sel(pval=pval)['percentile']

        # convert to binary
        binary = init_binary(variable,dim,da_O.time)
        for t in dim.time-1:
            doy         = da_O['time.dayofyear'][t].values
            binary[t,:,:] = (da_O[t,:,:].values >= da_pval[doy,:,:].values).astype(np.int16)

        # write output     
        if write2file:
            binary.to_netcdf(path_out + filename_out)
            s2s.compress_file(comp_lev,3,filename_out,path_out) 

        da_O.close()
        da_pval.close()
                
misc.toc()


