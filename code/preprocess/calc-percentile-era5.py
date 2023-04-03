"""
calculates climatological percentiles per xy grid point from era5 data
given a 20 year time interval (e.g. 2001-2022).
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
    data       = np.zeros((pval.size,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims       = ["pval","latitude","longitude"]
    coords     = dict(pval=pval,latitude=dim.latitude,longitude=dim.longitude)
    attrs      = dict(description='climatological percentile',units=units)
    name       = 'percentile'
    percentile = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    return percentile


# input ----------------------------------------------
variables        = ['rn24']                 # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
years            = np.arange(2001,2021,1)   # years for climatology calculation
grids            = ['0.25x0.25']            # '0.25x0.25' or '0.5x0.5'
pval             = np.array([0.5,0.75,0.90,0.95,0.99]) # percentile values
comp_lev         = 5
write2file       = True
# ----------------------------------------------------

for variable in variables:
    for grid in grids:

        misc.tic()
        
        # define stuff
        dim          = s2s.get_dim(grid,'time')
        path_in      = config.dirs['era5_cont_daily'] + variable + '/'
        path_out     = config.dirs['era5_percentile'] + variable + '/'
        filename_out = 'xy_percentile_' + variable + '_' + grid + '_' + str(years[0]) + '-' + str(years[-1]) + '.nc'
        
        # read files
        filenames_in = [path_in + variable + '_' + grid + '_' + str(years[0]) + '.nc']
        for year in years[1:]: filenames_in = filenames_in + [path_in + variable + '_' + grid + '_' + str(year) + '.nc']
        with ProgressBar(): ds = xr.open_mfdataset(filenames_in).compute()
            
        # calculate percentiles
        units      = ds[variable].attrs['units']
        percentile = init_percentile(variable,units,dim,pval)
        for i in range(0,pval.size):
            print(pval[i])
            percentile[i,:,:] = ds[variable].quantile(pval[i],dim='time').values

        if write2file:
            percentile.to_netcdf(path_out + filename_out)
            s2s.compress_file(comp_lev,3,filename_out,path_out)
            
        misc.toc()
