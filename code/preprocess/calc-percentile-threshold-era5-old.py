"""
calculates climatological percentiles per xy grid point from era5 data
given a 20 year time interval (e.g. 2001-2022).
"""

import numpy           as np
import xarray          as xr
from dask.diagnostics  import ProgressBar
from forsikring        import misc,s2s,config
from scipy             import ndimage


def init_percentile(variable,units,dim,pval):
    """ 
    Initializes output array used below.  
    Written here to clean up code.    
    """
    time       = xr.cftime_range(start="2021-01-01", periods=365, freq="D", calendar="noleap")
    data       = np.zeros((pval.size,365,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims       = ["pval","time","latitude","longitude"]
    coords     = dict(pval=pval,time=time,latitude=dim.latitude,longitude=dim.longitude)
    attrs      = dict(description='climatological percentile',units=units)
    name       = 'percentile'
    percentile = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)
    return percentile


def get_sample_dates(time,window):
    """
    creates array of sample dates to get percentile thresholds
    for each 365 day of the year. For example, if day of year = 30,
    then function makes a sample of day 30 +- window for each year, 
    giving a sample of window*years days for each day of the year.
    Sample is used to calculate climatological percentiles.
    """
    window_half = int(np.floor(window/2))
    start       = time - np.timedelta64(window_half,'D')
    
    if (start.dt.month == 2) & (start.dt.day == 29): # skip leap year day
        start  = start - np.timedelta64(1,'D')
        
    start = np.datetime_as_string(start, unit='D') 
    dates = xr.cftime_range(start=start, periods=window, freq="D", calendar="noleap").strftime('%Y-%m-%d')

    return dates


def calc_percentile(da,pval,window):
    """
    Calculates climatological percentiles for a given grid point
    for each day of year (365)
    """

    half_window = int(np.floor(window/2))
    # SHOULD THIS BE ZEROS OR NANS? THEN MODIFY QUANTILE TO NAN.QUANTILE?
    temp        = np.zeros((da.time.size,window),dtype='float32')
    
    for t in range(half_window,da.time.size-half_window):
        dates     = get_sample_dates(da.time[t],window)
        temp[t,:] = da.sel(time=dates).values
        
    temp       = np.reshape(temp,(years.size,365,window))
    temp       = np.transpose(temp, (1, 0, 2))
    temp       = np.reshape(temp,(365,years.size*window))
    percentile = np.quantile(temp,pval,axis=1)

    #percentile = np.zeros((pval.size,365))
    
    return percentile


# input ----------------------------------------------
variables        = ['tp24']                 # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
years            = np.arange(2001,2002,1)   # years for climatology calculation
grids            = ['0.25x0.25']            # '0.25x0.25' or '0.5x0.5'
pval             = np.array([0.75,0.9,0.95,0.99]) # percentile values
comp_lev         = 5
window           = 11
write2file       = False
# ----------------------------------------------------

for variable in variables:
    for grid in grids:

        misc.tic()
        
        # define stuff
        dim          = s2s.get_dim(grid,'time')
        path_in      = config.dirs['era5_cont_daily'] + variable + '/'
        path_out     = config.dirs['era5_percentile'] + variable + '/'
        filename_out = 'xy_percentile_' + variable + '_' + grid + '_' + str(years[0]) + '-' + str(years[-1]) + '.nc'
        
        # read files and remove leap year days
        filenames_in = [path_in + variable + '_' + grid + '_' + str(years[0]) + '.nc']
        for year in years[1:]: filenames_in = filenames_in + [path_in + variable + '_' + grid + '_' + str(year) + '.nc']
        da = xr.open_mfdataset(filenames_in)[variable]
        da = misc.rm_lpyr_days(da)
        
        # calculate dask array explicitely
        with ProgressBar():
            da = da.compute()

        # calculate percentiles for each grid point
        percentile = init_percentile(variable,da.attrs['units'],dim,pval)
        for i in range(0,dim.nlongitude):
            for j in range(0,dim.nlatitude):
                misc.tic()
                da_temp             = da.sel(latitude=dim.latitude[j],longitude=dim.longitude[i],method='nearest')
                percentile[:,:,j,i] = calc_percentile(da_temp,pval,window)
                misc.toc()
                
        if write2file:
            percentile.to_netcdf(path_out + filename_out)
            s2s.compress_file(comp_lev,3,filename_out,path_out)

        misc.toc()


