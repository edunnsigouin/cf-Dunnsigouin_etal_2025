"""
Calculates the difference in fss for two different sets of variables, domains, seasons etc..
The difference of the fss is also boostrapped. 

This code reads in the forecast and reference errors calculated previously so you need to 
run that code first.

NOTE: Forecast sets that differ in season will have different total number of forecasts.
For bootstrapping of the difference between the fss of each set to work, the number of 
forecasts need to be the samein each set. So here I shorten the number of forecasts of the
season with the most to match the one that has the least. 
"""

import numpy     as np
import xarray    as xr
import os
from forsikring  import misc,s2s,verify,config

# INPUT -----------------------------------------------
time_flag                = 'time'                   # timescale or time?
first_forecast_date      = '20210104'
number_forecasts         = 104
grid                     = '0.25x0.25'      	    # grid resolution
box_sizes                = np.arange(1,61,2)        # smoothing box size in grid points per side. Must be odd!
number_shuffle_bootstrap = 10000                    # number of times to shuffle initialization dates for error bars
comp_lev                 = 5                        # compression level (0-10) of netcdf putput file 
write2file               = False
# fss number 1:
variable1                = 't2m24'                   
domain1                  = 'europe'                 
season1                  = 'annual'                 
# fss number 2:
variable2                = 'tp24'
domain2                  = 'europe'
season2                  = 'annual'
# -----------------------------------------------------

misc.tic()

# define stuff
forecast_dates1         = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season1).strftime('%Y-%m-%d')
forecast_dates2         = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season2).strftime('%Y-%m-%d')
if len(forecast_dates1) > len(forecast_dates2): # make sure the number of forecast_dates are the same size 
    forecast_dates1 = forecast_dates1[:len(forecast_dates2)]
else:
    forecast_dates2 = forecast_dates2[:len(forecast_dates1)]

# define more stuff    
number_sample_bootstrap = forecast_dates1.size 
path_in                 = config.dirs['verify_s2s_forecast_daily']
path_out                = config.dirs['verify_s2s_forecast_daily']
prefix_out              = time_flag + '_vs_ss_difference_' + variable1 + '_' + domain1 + '_' + season1 + '_' + forecast_dates1[0] + '_' + forecast_dates1[-1] + \
                          '_' + variable2 + '_' + domain2 + '_' + season2 + '_' + forecast_dates2[0] + '_' + forecast_dates2[-1] 
prefix_in_1             = time_flag + '_vs_ss_error_anomaly_' + variable1 + '_' + domain1 + '_' + season1 + '_' + forecast_dates1[0] + '_' + forecast_dates1[-1]
prefix_in_2             = time_flag + '_vs_ss_error_anomaly_' + variable2 + '_' + domain2 + '_' + season2 + '_' + forecast_dates2[0] + '_' + forecast_dates2[-1]
if (grid == '0.25x0.25') or (grid == '0.5x0.5'):
    filename_in_1  = prefix_in_1 + '_' + grid + '.nc'
    filename_in_2  = prefix_in_2 + '_' + grid + '.nc'
    filename_out   = prefix_out + '_' + grid + '.nc'
else:    
    filename_in_1  = prefix_in_1 + '.nc'
    filename_in_2  = prefix_in_2 + '.nc'
    filename_out   = prefix_out + '.nc'

# read in error data
forecast_error1  = xr.open_dataset(path_in + filename_in_1)['forecast_error']
reference_error1 = xr.open_dataset(path_in + filename_in_1)['reference_error']
forecast_error2  = xr.open_dataset(path_in + filename_in_2)['forecast_error']
reference_error2 = xr.open_dataset(path_in + filename_in_2)['reference_error']

# initialize fss arrays for output
dim                                       = verify.get_data_dimensions(grid, time_flag, domain1) # doesn't matter which domain we input here
[fss_difference,fss_bootstrap_difference] = verify.initialize_fss_array(dim,box_sizes,number_shuffle_bootstrap)

# calc fss with bootstraping over all forecasts  
fss_difference[:,:], fss_bootstrap_difference[:,:,:] = verify.calc_fss_bootstrap_difference(reference_error1, reference_error2, forecast_error1, forecast_error2, number_shuffle_bootstrap, number_sample_bootstrap, box_sizes)

# write to fss and errors to file
verify.write_fss_to_file(fss_difference, fss_bootstrap_difference, write2file, grid, box_sizes, time_flag, filename_out, path_out, comp_lev)

misc.toc()


