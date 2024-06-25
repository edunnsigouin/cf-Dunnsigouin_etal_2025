"""
Calculates the fractional mean square error skill score (fmsess) or the fractional brier skill score (fbss) 
as a function of lead time and box size for ecmwf forecasts. Verification is era5. 

Input data are anomalies from the climatology for the former and ensemble-probabilities and binary values 
of forecasts over a threshold (e.g. 90th percentile) for the later.

Code includes bootstrapping of forecast mse to put error bars on fss. 

Code includes possibility of calculating only high resolution data, low resolution
or both. 
 
For FMSESS,  I don't need to read in reference era5 clim forecast to calulates
the score because when using anomalies, the equation fss = 1 - mse_forecast/mse_reference
simplifies to fss = 1 - mse_forecast/variance(obs). 
See chapter 5.4.2 of Joliffe and Stephenson text book  

Code also outputs the forecast and reference errors for different calculations
downstream. 
"""

import numpy     as np
import xarray    as xr
import os
from forsikring  import misc,s2s,verify,config

# INPUT -----------------------------------------------
score_flag               = 'fbss'
time_flag                = 'weekly'                 # daily or weekly
variable                 = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain                   = 'europe'                 # europe or norway only?
first_forecast_date      = '20200102'               # first initialization date of forecast (either a monday or thursday)
number_forecasts         = 313                      # number of forecasts 
season                   = 'annual'                 # pick forecasts in specific season (djf,mam,jja,son,annual)
grids                    = ['0.25x0.25','0.5x0.5']
box_sizes                = np.arange(1,61,2)        # smoothing box size in grid points per side. Must be odd!
number_bootstrap         = 10000                    # number of times to shuffle initialization dates for error bars
pval                     = 0.9
dt                       = 0.05                     # interpolation for lead time gained & max skill calculation
write2file               = True
# -----------------------------------------------------

misc.tic()

# define stuff
forecast_dates = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')
print(forecast_dates)
if score_flag == 'fmsess':
    path_in_forecast        = config.dirs['s2s_forecast_' + time_flag + '_anomaly'] + '/' + domain + '/' + variable + '/'
    path_in_verification    = config.dirs['era5_forecast_' + time_flag + '_anomaly'] + '/' + domain + '/' + variable + '/'
    prefix                  = score_flag + '_' + variable + '_' + time_flag + '_' + domain + '_' + season + '_' + forecast_dates[0] + '_' + forecast_dates[-1]
elif score_flag == 'fbss':
    path_in_forecast        = config.dirs['s2s_forecast_' + time_flag + '_probability'] + str(pval) + '/' + domain + '/' + variable + '/'
    path_in_verification    = config.dirs['era5_forecast_' + time_flag + '_binary'] + str(pval) + '/' + domain + '/' + variable + '/'
    prefix                  = score_flag + '_' + variable + '_pval' + str(pval) + '_' + time_flag + '_' + domain + '_' + season + '_' + forecast_dates[0] + '_' + forecast_dates[-1]

path_out        = config.dirs['verify_s2s_forecast_daily']
filename_hr_out = prefix + '_0.25x0.25.nc'
filename_lr_out = prefix + '_0.5x0.5.nc'

# loop through forecasts with different grids
for grid in grids:

    print('\ncalculating ' + score_flag + ' for variable ' + variable + ' on grid ' + grid)
    
    # define stuff 
    filename_out        = filename_hr_out if grid == '0.25x0.25' else filename_lr_out
    dim                 = verify.get_data_dimensions(grid, time_flag, domain)
    box_sizes_temp      = verify.match_box_sizes_high_to_low_resolution(grid,box_sizes)
    
    # initialize output arrays
    [score,score_bootstrap,sig] = verify.initialize_misc_arrays(score_flag,dim,box_sizes_temp,number_bootstrap)
    forecast_error              = verify.initialize_error_array(dim,box_sizes_temp,forecast_dates)
    reference_error             = verify.initialize_error_array(dim,box_sizes_temp,forecast_dates)

    # loop over forecast dates
    for  i, date in enumerate(forecast_dates):
        print('forecast date: ' + date)
        filename_verification                           = path_in_verification + variable + '_' + grid + '_' + date + '.nc'
        filename_forecast                               = path_in_forecast + variable + '_' + grid + '_' + date + '.nc'
        forecast_error[i, ...], reference_error[i, ...] = verify.calc_forecast_and_reference_error(score_flag,filename_verification, filename_forecast, variable, box_sizes_temp, pval)
       
    # calc score with bootstraping over all forecasts  
    score[:,:], score_bootstrap[:,:,:] = verify.calc_score_bootstrap(reference_error, forecast_error, number_bootstrap, box_sizes_temp)

    # calculate significance of score (95%)            
    sig[:,:] = s2s.calc_significant_values_using_bootstrap(score_bootstrap,0.05)

    # write to fss and errors to file
    verify.write_score_to_file(score, score_bootstrap, sig, forecast_error, reference_error, write2file, grid, box_sizes, filename_out, path_out)
    
# combine low and high resolution files into one file if both exist
filename_final = verify.combine_high_and_low_res_files(filename_hr_out, filename_lr_out, prefix + '.nc', path_out, write2file)

# calculate lead time gained by increasing spatial scale
# and append file with variables
[lead_time_gained, max_skill_mask]         = verify.initialize_ltg_and_max_skill_arrays(dim,box_sizes,number_bootstrap,dt,grids,time_flag)
lead_time_gained[:,:], max_skill_mask[:,:] = verify.calc_lead_time_gained(filename_final, dt)
verify.append_score_file(lead_time_gained, max_skill_mask, filename_final, write2file) 


misc.toc()



