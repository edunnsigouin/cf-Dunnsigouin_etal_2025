"""
Converts era5 yearly files into the same format as ecmwf hindcasts
corresponding to foreacsts initialized on mondays and thursdays for a given year.
e.g., for a forecast initialized on 2021-01-04, we collect all data for years 2001-2020
starting on 01-04 + 15 days (for high-resolution). Analogous files are created for low-resolution
data corresponfing to low-reoslution forecasts.  
"""

import numpy  as np
import xarray as xr
import pandas as pd
from dask.diagnostics   import ProgressBar
import os
from forsikring import config,misc,s2s

def init_hindcast(dim,date,hindcast_years,time,variable,long_name,units):
    """ 
    Initializes output array used below. 
    Written here to clean up code.
    """
    hdate = np.zeros(hindcast_years.size,dtype=int)
    for i in range(0,hindcast_years.size):
        hdate[i] = int(hindcast_years[i].astype(str) + date.strftime('%m%d'))
    
    data   = np.zeros((time.size,hdate.size,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims   = ["time","hdate","latitude","longitude"]
    coords = dict(time=time,hdate=hdate,latitude=dim.latitude,longitude=dim.longitude)
    attrs  = dict(long_name=long_name,units=units)
    output = xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=variable)
    return output

def init_time(date,grid):
    """
    initialized time array for use in code below
    """
    if grid == '0.25x0.25': time = pd.date_range(date,periods=15,freq="D")
    elif grid == '0.5x0.5': time = pd.date_range(date,periods=31,freq="D") + np.timedelta64(15,'D')
    return time

# INPUT -----------------------------------------------
variables        = ['tp24']             # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
init_start       = '20210104'              # first initialization date of forecast (either a monday or thursday)
init_n           = 104                     # number of forecasts   
grids            = ['0.25x0.25']           # '0.25x0.25' or '0.5x0.5'
comp_lev         = 5
write2file       = True
# -----------------------------------------------------         

# get all dates for monday and thursday forecast initializations 
init_dates = s2s.get_init_dates(init_start,init_n)

for variable in variables:
    for grid in grids:
        for date in init_dates:

            misc.tic()
            
            # define stuff
            dim            = s2s.get_dim(grid,'time')
            datestring     = date.strftime('%Y-%m-%d')
            forecast_year  = int(date.strftime('%Y'))
            hindcast_years = np.arange(forecast_year-20,forecast_year,1)
            path_in        = config.dirs['era5_cont_daily'] + variable + '/'
            path_out       = config.dirs['era5_hindcast_daily'] + variable + '/'
            filename_out   = variable + '_' + grid + '_' + datestring + '.nc'
            
            # read in data
            filenames_in = [path_in + variable + '_' + grid + '_' + str(hindcast_years[0]) + '.nc']
            for year in hindcast_years[1:]: filenames_in = filenames_in + [path_in + variable + '_' + grid + '_' + str(year) + '.nc']
            da = xr.open_mfdataset(filenames_in)[variable]

            # calculate explicitely
            with ProgressBar():
                da = da.compute()

            # extract data from specific hindcast dates    
            time     = init_time(date,grid)
            hindcast = init_hindcast(dim,date,hindcast_years,time,variable,da.attrs['long_name'],da.attrs['units'])            
            for i in range(0,hindcast_years.size):
                time              = init_time(date.replace(year=hindcast_years[i]),grid)
                hindcast[:,i,:,:] = da.sel(time=time,method='nearest').values
            da.close()

            if write2file:
                print('writing to file..')
                s2s.to_netcdf_pack64bit(hindcast,path_out + filename_out)
                print('compress file to reduce space..')
                s2s.compress_file(comp_lev,3,filename_out,path_out)
                print('')
            misc.toc()
