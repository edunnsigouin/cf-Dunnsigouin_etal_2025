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
score_flag               = 'fss'
time_flag                = 'daily'                   # daily or weekly
variable                 = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain                   = 'europe'                 # europe or norway only?
first_forecast_date      = '20200102'               # first initialization date of forecast (either a monday or thursday)
number_forecasts         = 313                      # number of forecasts 
season                   = 'annual'                 # pick forecasts in specific season (djf,mam,jja,son,annual)
grid                     = '0.25x0.25'
box_size                 = 1                       # smoothing box size in grid points per side. Must be odd!
lead_time                = 5
number_shuffle_bootstrap = 10000                   # number of times to shuffle initialization dates for error bars
write2file               = False
# -----------------------------------------------------

misc.tic()

print('\ncalculating fss for variable ' + variable + ' on grid ' + grid)

# define stuff
forecast_dates          = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')
path_in_forecast        = config.dirs['s2s_forecast_' + time_flag + '_anomaly'] + '/' + domain + '/' + variable + '/'
path_in_verification    = config.dirs['era5_forecast_' + time_flag + '_anomaly'] + '/' + domain + '/' + variable + '/'
path_out                = config.dirs['verify_s2s_forecast_daily']
filename_out            = 'fss_xy_' + variable + '_' + time_flag + '_' + domain + '_' + season + '_boxsize_' + str(box_size) + \
                          '_leadtime_' + str(lead_time) + '_' + forecast_dates[0] + '_' + forecast_dates[-1] + '_' + grid + '.nc'
dim                     = verify.get_data_dimensions(grid, time_flag, domain)
box_size_temp           = verify.match_box_sizes_high_to_low_resolution(grid,box_size)

# initialize output arrays
[score,score_bootstrap] = verify.initialize_score_xy_array(score_flag,dim,number_shuffle_bootstrap)
forecast_error          = verify.initialize_error_xy_array(dim,forecast_dates)
reference_error         = verify.initialize_error_xy_array(dim,forecast_dates)

# loop over forecast dates
for  i, date in enumerate(forecast_dates):
    print('forecast date: ' + date)
    filename_verification                           = path_in_verification + variable + '_' + grid + '_' + date + '.nc'
    filename_forecast                               = path_in_forecast + variable + '_' + grid + '_' + date + '.nc'
    forecast_error[i, ...], reference_error[i, ...] = verify.calc_forecast_and_reference_error_xy(score_flag,filename_verification,filename_forecast,variable,box_size_temp,lead_time)

# calc fss with bootstraping over all forecasts  
score[:,:], score_bootstrap[:,:,:] = verify.calc_score_bootstrap_xy(reference_error, forecast_error, number_shuffle_bootstrap)

# calculate signficance based on bootstrapped samples. threshold 95%
sig = s2s.mask_significant_values_from_bootstrap(score_bootstrap,0.05)

# write to fss and errors to file
verify.write_score_to_file_xy(score, sig, write2file, filename_out, path_out)


misc.toc()


