"""
1) interpolates high-res (0.25x0.25) forecasts/hindcasts from day 1-15 to low res (0.5x0.5)
2) combines the interpolated low res forecasts/hindcasts from day 1-15 with low res forecasts/hindcasts from day 16-46.
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
import xesmf    as xe
from forsikring import misc,s2s,config,verify

# INPUT -----------------------------------------------
variable            = 'tp24'                 # tp24 or t2m24
product             = 'hindcast'              # hindcast or forecast ? 
first_forecast_date = '20200102'             # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 313                      # number of forecasts 
season              = 'annual'
path_in             = config.dirs[f's2s_{product}_daily'] + variable + '/'
path_out            = config.dirs[f's2s_{product}_daily'] + variable + '/'
write2file          = True
# -----------------------------------------------------

def load_hr_and_lr_data(date,path_in,path_out,variable):
    
    # define stuff
    filename_in_hr    = path_in + variable + '_0.25x0.25_' + date + '.nc'
    filename_in_lr    = path_in + variable + '_0.5x0.5_' + date + '.nc'
    filename_out      = path_out + variable + '_day1to46_0.5x0.5_' + date + '.nc'
    
    # load data
    forecast_hr = xr.open_dataset(filename_in_hr)[variable]
    forecast_lr = xr.open_dataset(filename_in_lr)[variable]

    return forecast_hr, forecast_lr, filename_out


def regrid_hr_to_lr(forecast_hr, forecast_lr, variable):

    # define your target grid
    lat_out = forecast_lr['latitude'].values 
    lon_out = forecast_lr['longitude'].values 
    ds_out  = xr.Dataset({"lat": (["lat"], lat_out),"lon": (["lon"], lon_out),})

    # regrid
    forecast_hr        = forecast_hr.rename({'latitude': 'lat','longitude': 'lon'}) # xe needs lat/lon names variables
    regridder          = xe.Regridder(forecast_hr, ds_out, method="bilinear", periodic=False)
    forecast_hr_regrid = regridder(forecast_hr)

    # fix metadata
    forecast_hr_regrid = forecast_hr_regrid.rename({'lat': 'latitude','lon': 'longitude'})
    if variable == 'tp24':
        forecast_hr_regrid = forecast_hr_regrid.assign_attrs(units="m",long_name="daily accumulated precipitation").rename(variable)

    return forecast_hr_regrid


def concatenate_hr_regrid_to_lr_in_time(forecast_hr_regrid, forecast_lr):
    return xr.concat([forecast_hr_regrid, forecast_lr], dim="time").sortby("time")


def save_to_file(da,filename_out,write2file):
    if write2file:
        da.astype('float32').to_netcdf(filename_out)


    
if __name__ == "__main__":

    forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')

    for date in forecast_dates:

        print(date)
        
        forecast_hr, forecast_lr, filename_out = load_hr_and_lr_data(date,path_in,path_out,variable)
        forecast_hr_regrid                     = regrid_hr_to_lr(forecast_hr, forecast_lr, variable)
        forecast_combined                      = concatenate_hr_regrid_to_lr_in_time(forecast_hr_regrid, forecast_lr)
        save_to_file(forecast_combined,filename_out,write2file)
        

