"""
Downloads seas5.1 monthly seasonal hindcast data produced 
by ecmwf from the copernicus data store 

NOTE: When downloading total precipitation, the units are m/s. You need to 
multiply the values by the number of seconds in a month to get m units as
shown here:
https://confluence.ecmwf.int/pages/viewpage.action?pageId=197702790

NOTE2: Data is downloaded automatically on the 1x1 degree resolution.
This is the highest resolution offered on the c3s database.
"""

import numpy  as np
import xarray as xr
from dask.diagnostics import ProgressBar
import cdsapi
import pandas as pd
import os
from calendar import monthrange
from datetime import datetime, timedelta
from forsikring import config,s2s,misc


def seconds_in_month(date_string,leadtime_months):
    try:
        # Parse the date string 
        date_object = datetime.strptime(date_string, '%Y-%m-%d')

        # Create a dictionary to store the results
        seconds_per_month = np.zeros(leadtime_months.size)

        # Calculate seconds for the next 7 months (including the input month)
        for i in range(leadtime_months.size):
            _, days_in_month = monthrange(date_object.year, date_object.month)
            seconds_in_month = days_in_month * 24 * 60 * 60

            # Store the result in the dictionary
            seconds_per_month[i] = seconds_in_month

            # Increment the month
            date_object += timedelta(days=days_in_month)
            date_object = date_object.replace(day=1)

        return seconds_per_month

    except Exception as e:
        print("An error occurred:", e)
        return None


# INPUT -----------------------------------------------
area            = '74/-27/33/45' # or 'E' for europe
variables       = ['tp','t2m'] # 'tp' and 't2m'
data_type       = 'hindcast' # forecast or hindcast
system          = '5' # model version (4,5 or 51)
years           = np.arange(1993,2017,1)
months          = np.arange(1,13,1)
leadtime_months = np.arange(1,7,1)
comp_lev        = 5 # file compression level
write2file      = True
# -----------------------------------------------------

# loop through variables        
for variable in variables:
    for year in years:

        # define stuff
        filename_grib = variable + '_' + str(year) + '.grib'
        filename_nc   = variable + '_' + str(year) + '.nc'
        path          = config.dirs['seasonal_' + data_type + '_monthly'] + variable + '/'

        # populate dictionary
        months_string          = [str(month) for month in months]
        leadtime_months_string = [str(leadtime_month) for leadtime_month in leadtime_months]
        dic = {
                'format':'grib',
                'originating_centre':'ecmwf',
                'system':system,
                'product_type':'monthly_mean',
                'year':[str(year)],
                'month':months_string,
                'leadtime_month':leadtime_months_string,
                'area':area,
        }
        if variable == 'tp': dic['variable'] = 'total_precipitation'
        if variable == 't2m': dic['variable'] = '2m_temperature'

        if write2file:
                
                print('')
                print('downloading file: ' + filename_grib)
                print('')

                # download
                c = cdsapi.Client()
                c.retrieve('seasonal-monthly-single-levels', dic, path + filename_grib)

                # read in data 
                ds = xr.open_dataset(path+filename_grib, engine='cfgrib', backend_kwargs=dict(time_dims=('forecastMonth', 'time')))
                ds = ds.rename({'forecastMonth':'lead_time_month'})
                
                # modify metadata
                if variable == 'tp':
                        # rename stuff
                        ds                              = ds.rename({'tprate':variable})
                        ds[variable].attrs['long_name'] = 'total accumulated monthly precipitation'
                        ds[variable].attrs['units']     = 'm'
                        ds                              = ds.drop('surface')
                        del ds[variable].attrs['GRIB_name']
                        del ds[variable].attrs['GRIB_shortName']
                        del ds[variable].attrs['GRIB_units']
                        
                        # units => m/s to m
                        for t in range(0,ds['time'].size): # initialization dates
                                date_string = str(ds['time'][t].values)[:10]
                                seconds     = seconds_in_month(date_string,leadtime_months)
                                for lt in range(0,leadtime_months.size): # lead times
                                        ds[variable][:,lt,t,:,:] = ds[variable][:,lt,t,:,:]*seconds[lt]
                                        
                if variable == 't2m':
                        ds[variable].attrs['long_name'] = '2m temperature'
                        ds[variable].attrs['units']     = 'K'
                        ds                              = ds.drop('surface')
                        
                # write to file
                ds.to_netcdf(path+filename_nc)
                os.system('rm ' + path + filename_grib)
                os.system('rm ' + path + '*.idx')
                
                # compress netcdf
                s2s.compress_file(comp_lev,3,filename_nc,path)     


                
