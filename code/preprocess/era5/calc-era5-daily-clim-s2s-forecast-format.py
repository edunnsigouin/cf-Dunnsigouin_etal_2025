"""
Creates era5 climatology files with same format as ecmwf forecast file
for use as a reference forecast for verification.
example: tp24_CY47R1_0.25x0.25_2021-01-04.nc is the forecast file
and the new era5 clim file associated with this forecast is 
tp24_clim_0.25x0.25_2021-01-04.nc with dates corresponding
to climatological jan 04 to jan 04 + 46 days.

NOTE1: climatology is calculated over an equivalent hindcast period. E.g.,
if forecast date is 2021-01-04, then climatology calculated from past twenty 
years 2001-2020. Climatology is simple calendar day mean from continuous yearly data.
"""

import numpy  as np
import xarray as xr
import pandas as pd
from dask.diagnostics import ProgressBar
from forsikring       import config,misc,s2s

# INPUT -----------------------------------------------
variables           = ['t2m24']             # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
first_forecast_date = '20210104' # first initialization date of forecast (either a monday or thursday)  
number_forecasts    = 104        # number of forecast initializations 
grids               = ['0.5x0.5']          # '0.25x0.25' or '0.5x0.5'
comp_lev            = 5
write2file          = True
# -----------------------------------------------------         

# get all dates for monday and thursday forecast initializations
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts)
print(forecast_dates)

for variable in variables:
    for grid in grids:
        for forecast_date in forecast_dates:

            print('\nvariable: ' + variable + ', date: ' + forecast_date.strftime('%Y-%m-%d'),', grid: ' + grid)
            
            # define stuff
            path_in  = config.dirs['era5_daily'] + variable + '/'
            path_out = config.dirs['era5_s2s_forecast_daily_clim'] + variable + '/'

            # get corresponding hindcast climatology for given forecast
            forecast_year = int(forecast_date.strftime('%Y'))
            clim_years    = np.arange(forecast_year-20, forecast_year)
            filenames     = [path_in + variable + '_' + grid + '_' + str(year) + '.nc' for year in clim_years]
            with ProgressBar(): ds_clim = xr.open_mfdataset(filenames).groupby('time.dayofyear').mean(dim='time').compute()
            ds_clim       = ds_clim.rename({'dayofyear':'time'})

            # only include extra calendar day in climatology if forecast_year is a leap year
            # Best way of doing this?
            if misc.is_leap_year(forecast_year) == False: ds_clim = ds_clim.drop_sel(time=366) 

            
            # Extract climatology dates corresponding to forecast dates.
            # Make dates in resulting array correspond to forecast dates
            # for convenience later on.
            if grid == '0.25x0.25':
                clim_dates = pd.date_range(forecast_date,periods=15,freq="D").dayofyear.values
                ds         = ds_clim.sel(time=clim_dates)
                ds['time'] = pd.date_range(forecast_date,periods=15,freq="D") 
            elif grid == '0.5x0.5':
                clim_dates = (pd.date_range(forecast_date,periods=31,freq="D") + np.timedelta64(15,'D')).dayofyear.values
                ds         = ds_clim.sel(time=clim_dates)
                ds['time'] = pd.date_range(forecast_date,periods=31,freq="D") + np.timedelta64(15,'D') 

            # modify metadata
            if variable == 'tp24':
                ds[variable].attrs['units']     = 'm'
                ds[variable].attrs['long_name'] = 'climatological mean daily accumulated precipitation'
            if variable == 'rn24':
                ds[variable].attrs['units']     = 'm'
                ds[variable].attrs['long_name'] = 'climatological mean daily accumulated rainfall'
            if variable == 'mx24tpr':
                ds[variable].attrs['units']     = 'kg m**-2 s**-1'
                ds[variable].attrs['long_name'] = 'climatological mean daily maximum timestep precipitation rate'
            if variable == 'mx24tp6':
                ds[variable].attrs['units']     = 'm'
                ds[variable].attrs['long_name'] = 'climatological mean daily maximum 6 hour accumulated precipitation'
            if variable == 'mx24rn6':
                ds[variable].attrs['units']     = 'm'
                ds[variable].attrs['long_name'] = 'climatological mean daily maximum 6 hour accumulated rainfall'
            
            if write2file:
                filename_out = '%s_%s_%s.nc'%(variable,grid,forecast_date.strftime('%Y-%m-%d'))
                misc.to_netcdf_pack64bit(ds[variable],path_out + filename_out)
                misc.compress_file(comp_lev,3,filename_out,path_out)

            ds.close()
            ds_clim.close()

