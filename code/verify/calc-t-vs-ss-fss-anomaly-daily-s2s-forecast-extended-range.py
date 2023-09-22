"""
Calculates the fractional skill score as a function of lead time and box size 
for ecmwf forecasts. Reference forecast is era5 climatology. Verification is era5. 
Code includes bootstrapping of forecast mse to put error bars on fss. 
Input are anomalies in model-format (era5 and forecasts).

NOTE: Here I don't need to read in reference era5 clim forecast
because when using anomalies, the equation fss = 1 - mse_forecast/mse_reference
simplifies to fss = 1 - mse_forecast/variance(obs). 
See chapter 5.4.2 of Joliffe and Stephenson text book  
"""

import numpy     as np
import xarray    as xr
import os
from forsikring  import misc,s2s,verify,config

# INPUT -----------------------------------------------
variable                 = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain                   = 'europe'                 # europe or norway only?
first_forecast_date      = '20200102'               # first initialization date of forecast (either a monday or thursday)
number_forecasts         = 2                      # number of forecasts 
grids                    = ['0.25x0.25']
box_sizes                = np.arange(1,8,2)        # np.array([1,9,19,29,39,49,59])  # neighborhood size in grid points per side
number_shuffle_bootstrap = 2                    # number of times to shuffle initialization dates for error bars
number_sample_bootstrap  = 2                       # number of sampled forecasts with replacement in each bootstrap member
comp_lev                 = 5                        # compression level (0-10) of netcdf putput file
write2file               = False
# -----------------------------------------------------

misc.tic()

# define stuff
forecast_dates       = s2s.get_forecast_dates(first_forecast_date,number_forecasts).strftime('%Y-%m-%d')
path_in_forecast     = config.dirs['s2s_forecast_daily_anomaly'] + variable + '/'
path_in_verification = config.dirs['era5_s2s_forecast_daily_anomaly'] + variable + '/'
path_out             = config.dirs['verify_s2s_forecast_daily']

for grid in grids:

    # define output fss file
    filename_out = 't_vs_ss_fss_anomaly_' + variable + '_' + grid + '_' + domain + \
	           '_' + forecast_dates[0] + '_' + forecast_dates[-1] + '.nc'
    
    # get data dimensions and subselect domain
    dim            = misc.get_dim(grid,'time')
    dim            = misc.subselect_xy_domain_from_dim(dim,domain,grid)
    box_sizes_temp = verify.match_box_sizes_high_to_low_resolution(grid,box_sizes)

    # initialize fss output array                                                                                              
    [fss,fss_bootstrap] = verify.initialize_fss_array(dim,box_sizes,number_shuffle_bootstrap)
    forecast_error      = verify.initialize_error_array(dim,box_sizes,forecast_dates)
    reference_error     = verify.initialize_error_array(dim,box_sizes,forecast_dates)

    # loop over forecasts
    for  i, date in enumerate(forecast_dates):

        print('percent complete: ' + str(i/forecast_dates.size*100) + ', calculating forecast ' + date)
    
        # define input filenames for forecast & observation anomalies
        filename_verification =  path_in_verification + variable + '_' + grid + '_' + date + '.nc'
        filename_forecast     =  path_in_forecast + variable + '_' + grid + '_' + date + '.nc'

        # read in files to dataarray
        verification = xr.open_dataset(filename_verification)[variable]
        forecast     = xr.open_dataset(filename_forecast)[variable] 

        # sub-select specific domain, lead times and percentile threshold
        verification = verification.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
        forecast     = forecast.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
    
        # smooth forecast and observations in xy for each forecast
        # Should there be a cosine weighting when applying filter in y?
        verification_smoothed = verify.boxcar_smoother_xy(box_sizes,verification)
        forecast_smoothed     = verify.boxcar_smoother_xy(box_sizes,forecast)

        # calc squared error for each forecast
        forecast_error_xy  = (forecast_smoothed - verification_smoothed)**2
        reference_error_xy = (verification_smoothed)**2

        # average in space over entire domain and dump into dedicated error array
        forecast_error[i,...]  = misc.xy_mean(forecast_error_xy).values
        reference_error[i,...] = misc.xy_mean(reference_error_xy).values

        verification.close()
        forecast.close()

    
    # calc fss with bootstraping over all forecasts  
    [fss_temp,fss_bootstrap_temp] = verify.calc_fss_bootstrap(reference_error, forecast_error, number_shuffle_bootstrap, number_sample_bootstrap, box_sizes)

    # write to file
    if write2file:
        fss[:,:]           = fss_temp
        fss_bootstrap[:,:] = fss_bootstrap_temp
        ds                 = xr.merge([fss,fss_bootstrap])
        ds.to_netcdf(path_out+filename_out)
        misc.compress_file(comp_lev,3,filename_out,path_out) 

misc.toc()

