
import numpy    as np
import xarray   as xr
from forsikring import s2s, verify, misc, config
from matplotlib  import pyplot as plt

# Input -----------------------------------
variables           = ['t2m24']                  # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
first_forecast_date = '20210104'               # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 1                      # number of forecasts
season              = 'annual'
grids               = ['0.25x0.25']            # '0.25x0.25' & '0.5x0.5'
box_sizes           = np.arange(1,7,2)        # smoothing box size in grid points per side. Must be odd! 
comp_lev            = 5                        # compression level (0-10) of netcdf putput file 
write2file          = False
# -----------------------------------------

misc.tic()

# define stuff 
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d').values
print(forecast_dates)

for variable in variables:
    for grid in grids:
        for date in forecast_dates:
            
            print('\nsmoothing ' + variable + ' in forecast initialized on ' + date + ' with resolution ' + grid)

            path_in_forecast  = config.dirs['s2s_forecast_daily'] + variable + '/'
            path_out          = config.dirs['s2s_forecast_daily_smooth'] + variable + '/'
            filename_forecast = variable + '_' + grid + '_' + date + '.nc'
            filename_out      = variable + '_' + grid + '_' + date + '.nc'

            # read data
            da_forecast = xr.open_dataset(path_in_forecast + filename_forecast)[variable].mean(dim='number').isel(time=1)


            da_forecast_smooth = verify.boxcar_smoother_xy_optimized(box_sizes, da_forecast)


            """
            # smooth
            #da_forecast_smooth = verify.initialize_smooth_forecast(box_sizes,variable,da_forecast)
            #da_forecast_smooth[:,:,:,:,:] = verify.boxcar_smoother_xy(box_sizes, da_forecast)
            

            

misc.toc()
