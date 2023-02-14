"""
Calculates the mean-square-error skill score as a function of 
lead time for ecmwf forecasts. Reference forecasts are either 
era5 climatology or era5 persistence. Verification is era5.
"""

import numpy  as np
import xarray as xr
from dask.diagnostics   import ProgressBar
from forsikring import config,misc,s2s
import random

# INPUT -----------------------------------------------
ref_forecast_flag = 'clim'                  # clim or pers
variable          = 'tp24'                 # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
mon_thu_start     = ['20210104','20210107']  # first monday & thursday initialization date of forecast
num_i_weeks       = 52                       # number of weeks withe forecasts
grid              = '0.5x0.5'              # '0.25x0.25' & '0.5x0.5'
comp_lev          = 5
write2file        = False
# -----------------------------------------------------      



# get all dates for monday and thursday forecast initializations
dates_monday_thursday = s2s.get_monday_thursday_dates(mon_thu_start,num_i_weeks)

# convert dates to a list of file names for verification, reference forecast and forecast data
path_in_verification   = config.dirs['era5_model_daily'] + variable + '/'
filenames_verification = path_in_verification + variable + '_' + grid + '_' + dates_monday_thursday.strftime('%Y-%m-%d').values + '.nc'

path_in_ref_forecast   = config.dirs['era5_model_clim'] + variable + '/'
filenames_ref_forecast = path_in_ref_forecast + variable + '_' + grid + '_' + dates_monday_thursday.strftime('%Y-%m-%d').values + '.nc'
                
def preprocess(ds):
    '''change time dim from calendar dates to numbers'''
    ds['time'] = np.arange(0,ds.time.size,1)
    return ds

ds = xr.open_mfdataset(filenames_ref_forecast,preprocess=preprocess,combine='nested',concat_dim='chunks')
print(ds)
ds.close()

#random.shuffle(filenames_verification)





"""
for variable in variables:
    for grid in grids:

        # initialize MSE statistic
        dim              = s2s.get_dim(grid)
        mse_forecast     = np.zeros((dim.ntime,dim.nlatitude,dim.nlongitude))
        mse_ref_forecast = np.zeros((dim.ntime,dim.nlatitude,dim.nlongitude))
        
        for date in dates_monday_thursday:
            
            datestring = date.strftime('%Y-%m-%d')
            print('\nvariable: ' + variable + ', date: ' + datestring,', grid: ',grid)

            # Read data
            path_in_forecast  = config.dirs['forecast_daily'] + variable + '/'
            forcastcycle      = s2s.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
            filename_forecast = variable + '_' + forcastcycle + '_' + grid + '_' + datestring + '.nc'
            # average over ensemble members
            ds_forecast       = xr.open_dataset(path_in_forecast + filename_forecast).mean(dim='number')

            if ref_forecast_flag == 'clim':
                path_in_ref_forecast  = config.dirs['era5_model_clim'] + variable + '/'
                filename_ref_forecast = variable + '_' + grid + '_' + datestring + '.nc'
                ds_ref_forecast       = xr.open_dataset(path_in_ref_forecast + filename_ref_forecast)
            elif ref_forecast_flag == 'pers':
                print('need to code this!')
                
            path_in_verification  = config.dirs['era5_model_daily'] + variable + '/'    
            filename_verification = variable + '_' + grid + '_' + datestring + '.nc'
            ds_verification       = xr.open_dataset(path_in_verification + filename_verification)

            # calc mean square error
            mse_forecast     = (1/dates_monday_thursday.size)*(mse_forecast + (ds_forecast[variable].values - ds_verification[variable].values)**2)
            mse_ref_forecast = (1/dates_monday_thursday.size)*(mse_ref_forecast + (ds_ref_forecast[variable].values - ds_verification[variable].values)**2)
            
            ds_forecast.close()
            ds_ref_forecast.close()
            ds_verification.close()

        # convert numpy array to dataset
        ds_forecast     = misc.convert_xyt_np_to_xr(mse_forecast,'mse','mean square error','',dim)
        ds_ref_forecast = misc.convert_xyt_np_to_xr(mse_ref_forecast,'mse','mean square error','',dim)
        
        # aggregate mse in space (mean)
        ds_forecast     = misc.xy_mean(ds_forecast)
        ds_ref_forecast = misc.xy_mean(ds_ref_forecast)

        # calculate msess
        msess                      = 1 - ds_forecast['mse']/ds_ref_forecast['mse']
        ds                         = msess.to_dataset(name='msess')
        ds['msess']['units']       = 'unitless'
        ds['msess']['description'] = 'mean square error skill score'
        
        if write2file:
            print('writing to file..')
            timestamp    = dates_monday_thursday[0].strftime('%Y-%m-%d') + '_' + dates_monday_thursday[-1].strftime('%Y-%m-%d')
            path_out     = config.dirs['calc_forecast_daily'] + variable + '/'
            filename_out = 't_msses_' + ref_forecast_flag + '_' + grid + '_' + timestamp + '.nc'
            s2s.to_netcdf_pack64bit(ds['msess'],path_out + filename_out)
            print('compress file to reduce space..\n')
            s2s.compress_file(comp_lev,3,filename_out,path_out)

"""





        
