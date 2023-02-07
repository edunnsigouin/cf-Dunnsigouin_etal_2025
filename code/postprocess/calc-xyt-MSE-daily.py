"""
Calculates the mean-square-error statistic as a function of x,y and 
lead time for ecmwf forecasts, era5 climatology and era5 persistence
"""

import numpy  as np
import xarray as xr
from dask.diagnostics   import ProgressBar
from forsikring import config,misc,s2s

# INPUT -----------------------------------------------
data_flag        = 'clim'                  # ecwmf,clim,pers
variables        = ['tp24']                 # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
mon_thu_start    = ['20210104','20210107']  # first monday & thursday initialization date of forecast
num_i_weeks      = 52                       # number of weeks withe forecasts
grids            = ['0.25x0.25']            # '0.25x0.25' & '0.5x0.5'
comp_lev         = 5
write2file       = True
# -----------------------------------------------------      

# get all dates for monday and thursday forecast initializations
dates_monday_thursday = s2s.get_monday_thursday_dates(mon_thu_start,num_i_weeks)

for variable in variables:
    for grid in grids:

        # initialize MSE statistic
        dim = s2s.get_dim(grid)
        mse = np.zeros((dim.ntime,dim.nlatitude,dim.nlongitude))

        for date in dates_monday_thursday:
            
            datestring = date.strftime('%Y-%m-%d')
            print('\nvariable: ' + variable + ', date: ' + datestring,', grid: ',grid)

            # Read data
            if data_flag == 'ecmwf':
                path_in_forecast  = config.dirs['forecast_daily'] + variable + '/'
                forcastcycle      = s2s.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
                filename_forecast = variable + '_' + forcastcycle + '_' + grid + '_' + datestring + '.nc'
                # average over ensemble members
                ds_forecast       = xr.open_dataset(path_in_forecast + filename_forecast).mean(dim='number')
            elif data_flag == 'clim':
                path_in_forecast  = config.dirs['era5_model_clim'] + variable + '/'
                filename_forecast = variable + '_' + grid + '_' + datestring + '.nc'
                ds_forecast       = xr.open_dataset(path_in_forecast + filename_forecast)
                
            path_in_verification  = config.dirs['era5_model_daily'] + variable + '/'    
            filename_verification = variable + '_' + grid + '_' + datestring + '.nc'
            ds_verification       = xr.open_dataset(path_in_verification + filename_verification)

            # calc mean square error
            mse = (1/dates_monday_thursday.size)*(mse + (ds_forecast[variable].values - ds_verification[variable].values)**2)
            
            ds_forecast.close()
            ds_verification.close()

        if write2file:
            # turn numpy array into dataset
            output = xr.DataArray(
                data=mse,
                dims=["time","latitude", "longitude"],
                coords=dict(longitude=(["longitude"], dim.longitude),
                        latitude=(["latitude"], dim.latitude),
                        time=dim.time),
                attrs=dict(description="mean square error",
                           units="test"))
            ds = output.to_dataset(name='mse')

            print('writing to file..')
            timestamp    = dates_monday_thursday[0].strftime('%Y-%m-%d') + '_' + dates_monday_thursday[-1].strftime('%Y-%m-%d')
            path_out     = config.dirs['calc_forecast_daily'] + variable + '/'
            filename_out = 'xyt_mse_' + data_flag + '_' + grid + '_' + timestamp + '.nc'
            s2s.to_netcdf_pack64bit(ds['mse'],path_out + filename_out)
            print('compress file to reduce space..\n')
            s2s.compress_file(comp_lev,3,filename_out,path_out)







        
