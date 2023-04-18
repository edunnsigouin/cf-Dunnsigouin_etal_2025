"""
calculates climatological percentiles per xy grid point from era5 data
given a 20 year time interval (e.g. 2001-2022).
"""

import numpy           as np
import xarray          as xr
from dask.diagnostics  import ProgressBar
from forsikring        import misc,s2s,config
from scipy             import ndimage


def init_percentile(variable,units,dim,pval,year):
    """ 
    Initializes output array used below.  
    Written here to clean up code.    
    """
    time       = xr.cftime_range(start=str(year) + "-01-01", periods=365, freq="D", calendar="noleap")
    data       = np.zeros((pval.size,365,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims       = ["pval","time","latitude","longitude"]
    coords     = dict(pval=pval,time=time,latitude=dim.latitude,longitude=dim.longitude)
    attrs      = dict(description='climatological percentile',units=units)
    name       = 'percentile'
    percentile = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    return percentile

def moving_average(x, w):
    """
    simple moving average to aggregate data corresponding to 'timescale' lengths
    e.g. takes the average of data[day:day+w.size,lat,lon]. Last time values are
    calculated with data padded with zeros.
    """
    x = np.pad(x,pad_width=w-1,mode='constant',constant_values=(0.0, 0.0))[w-1:]
    return np.convolve(x, np.ones(w), 'valid') / w

def calc_percentile(data,pval,window,years):
    """
    Calculates climatological percentiles for a given grid point
    for each day of year (365) using a window of days around
    each calendar day to increase the sample.
    """
    ntime       = data.shape[0]
    half_window = int(np.floor(window/2))
    temp        = np.zeros((ntime,window),dtype='float32') # should be nans? also np.nanquantile?

    for t in range(half_window,ntime-half_window):
        temp[t,:] = data[t-half_window:t+half_window+1]
        
    temp       = np.reshape(temp,(years.size,365,window))
    temp       = np.transpose(temp, (1, 0, 2))
    temp       = np.reshape(temp,(365,years.size*window))
    return np.quantile(temp,pval,axis=1)

# input ----------------------------------------------
variables        = ['tp24']                 # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
years            = np.arange(2001,2021,1)   # years for climatology calculation
grids            = ['0.25x0.25']            # '0.25x0.25' or '0.5x0.5'
pval             = np.array([0.75,0.8,0.85,0.9,0.95,0.99]) # percentile values
comp_lev         = 5                        # compression level for output file
aggregation      = 2
window           = 11                       # sample window in days around calendar day
write2file       = True
# ----------------------------------------------------

for variable in variables:
    for grid in grids:

        misc.tic()
        
        # define stuff
        dim          = s2s.get_dim(grid,'time')
        path_in      = config.dirs['era5_cont_daily'] + variable + '/'
        path_out     = config.dirs['era5_cont_percentile'] + variable + '/'
        filename_out = 'xyt_percentile_' + variable + '_' + grid + '_' + 'agg_' + str(aggregation) + '_' + str(years[0]) + '-' + str(years[-1]) + '.nc'
        
        # read files and remove leap year days
        filenames_in = [path_in + variable + '_' + grid + '_' + str(years[0]) + '.nc']
        for year in years[1:]: filenames_in = filenames_in + [path_in + variable + '_' + grid + '_' + str(year) + '.nc']
        da    = xr.open_mfdataset(filenames_in)[variable]
        da    = misc.rm_lpyr_days(da)
        units = da.attrs['units']

        # calculate dask array explicitely
        with ProgressBar():
            data = da.compute().values
        da.close()
            
        # aggregation step. Basically a running mean smoother of data[day:day+aggregation,lat,lon].
        # output dims are same as input
        data = np.apply_along_axis(moving_average,0,data,aggregation)

        # calculate percentiles for each grid point
        percentile = init_percentile(variable,units,dim,pval,years[-1])
        for i in range(0,dim.nlongitude):
            print('\n percent complete: ' + str(i/dim.nlongitude*100))
            for j in range(0,dim.nlatitude):
                percentile[:,:,j,i] = calc_percentile(data[:,j,i],pval,window,years)
                
        if write2file:
            percentile.to_netcdf(path_out + filename_out)
            s2s.compress_file(comp_lev,3,filename_out,path_out)

        misc.toc()

