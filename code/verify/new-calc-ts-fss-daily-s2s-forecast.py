"""
Calculates the fractional skill score as a function of lead time and box size 
for ecmwf forecasts. Verification is era5. Data are anomalies from the climatology. 

Code includes bootstrapping of forecast mse to put error bars on fss. 
Input are anomalies in model-format (era5 and forecasts).

Code includes possibility of output as a function of lead timescale.
Lead timescale refers to those defined by Wheeler et al. 2016 QJRMS. For example,
1-day leadtime/1-day average. 2-day lead time/2-day average, etc..

Code includes possibility of calculating only high resolution data, low resolution
or both. 
 
NOTE: Here I don't need to read in reference era5 clim forecast to calulates fss
because when using anomalies, the equation fss = 1 - mse_forecast/mse_reference
simplifies to fss = 1 - mse_forecast/variance(obs). 
See chapter 5.4.2 of Joliffe and Stephenson text book  

NOTE2: outputs the forecast and reference errors for different calculations
downstream. Need them for boostrapping of the difference in fss
"""

import numpy     as np
import xarray    as xr
import os
from forsikring  import misc,s2s,verify,config

# INPUT -----------------------------------------------
time_flag                = 'timescale'                   # timescale or time?
variable                 = 't2m24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain                   = 'europe'                 # europe or norway only?
first_forecast_date      = '20210104'               # first initialization date of forecast (either a monday or thursday)
number_forecasts         = 104                      # number of forecasts 
season                   = 'annual'                 # pick forecasts in specific season (djf,mam,jja,son,annual)
grids                    = ['0.25x0.25','0.5x0.5']
box_sizes                = np.arange(1,61,2)        # smoothing box size in grid points per side. Must be odd!
number_shuffle_bootstrap = 10000                    # number of times to shuffle initialization dates for error bars
write2file               = True
# -----------------------------------------------------

misc.tic()

# define stuff
forecast_dates          = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')
path_in_forecast        = config.dirs['s2s_forecast_daily_anomaly'] + variable + '/'
path_in_verification    = config.dirs['era5_s2s_forecast_daily_anomaly'] + variable + '/'
path_out                = config.dirs['verify_s2s_forecast_daily']
prefix_fss              = 'fss_' + variable + '_' + time_flag + '_' + domain + '_' + season + '_' + forecast_dates[0] + '_' + forecast_dates[-1] 
filename_fss_hr_out     = prefix_fss + '_0.25x0.25.nc'
filename_fss_lr_out     = prefix_fss + '_0.5x0.5.nc'
prefix_error            = 'error_' + variable + '_' + time_flag + '_' + domain + '_' + season + '_' + forecast_dates[0] + '_' + forecast_dates[-1]
filename_error_hr_out   = prefix_error + '_0.25x0.25.nc'
filename_error_lr_out   = prefix_error + '_0.5x0.5.nc'

# loop through forecasts with different grids
for grid in grids:

    print('\ncalculating fss for variable ' + variable + ' on grid ' + grid)
    
    # define stuff 
    filename_fss_out    = filename_fss_hr_out if grid == '0.25x0.25' else filename_fss_lr_out
    filename_error_out  = filename_error_hr_out if grid == '0.25x0.25' else filename_error_lr_out
    dim                 = verify.get_data_dimensions(grid, time_flag, domain)
    box_sizes_temp      = verify.match_box_sizes_high_to_low_resolution(grid,box_sizes)

    # initialize output arrays
    [fss,fss_bootstrap] = verify.initialize_fss_array(dim,box_sizes_temp,number_shuffle_bootstrap)
    forecast_error      = verify.initialize_error_array(dim,box_sizes_temp,forecast_dates)
    reference_error     = verify.initialize_error_array(dim,box_sizes_temp,forecast_dates)

     # loop over forecast dates
    for  i, date in enumerate(forecast_dates):
        print('forecast date: ' + date)
        filename_verification                           = path_in_verification + 'anomaly_' + variable + '_' + time_flag + '_' + grid + '_' + date + '.nc'
        filename_forecast                               = path_in_forecast + 'anomaly_' + variable + '_' + time_flag + '_' + grid + '_' + date + '.nc'
        forecast_error[i, ...], reference_error[i, ...] = verify.calc_forecast_and_reference_error_new(filename_verification, filename_forecast, variable, box_sizes_temp, dim)
 
    # calc fss with bootstraping over all forecasts  
    fss[:,:], fss_bootstrap[:,:,:] = verify.calc_fss_bootstrap(reference_error, forecast_error, number_shuffle_bootstrap, box_sizes_temp)
     
    # write to fss and errors to file
    verify.write_error_to_file(forecast_error, reference_error, write2file, grid, box_sizes, time_flag, filename_error_out, path_out)
    verify.write_fss_to_file(fss, fss_bootstrap, write2file, grid, box_sizes, time_flag, filename_fss_out, path_out)

# combine low and high resolution files into one file if both exist
verify.combine_high_and_low_res_files(filename_error_hr_out, filename_error_lr_out, prefix_error + '.nc', path_out, time_flag, write2file)
verify.combine_high_and_low_res_files(filename_fss_hr_out, filename_fss_lr_out, prefix_fss + '.nc', path_out, time_flag, write2file)

misc.toc()


