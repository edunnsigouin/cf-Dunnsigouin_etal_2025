"""
Calculates the fractional skill score as a function of                                                                                                        
lead time and neighborhood size for ecmwf seasonal forecats. 
Reference forecast is era5 climatology and verification is era5. 
Code includes bootstrapping of forecast mse to put error bars on fss. 
Input is pre-processed data in model-format converted to anomalies 
from era5 and hindcast climatology.

NOTE: Here I don't need to read in reference era5 clim forecast
because when using anomalies, the equation fss = 1 - mse_forecast/mse_reference
simplifies to fss = 1 - (forecast - obs)**2/(obs)**2. See chapter 5.4.2 of 
Joliffe and Stephenson text book.  
"""

import numpy     as np
import xarray    as xr
import pandas    as pd
import os
from forsikring  import misc,s2s,verify,config

# INPUT -----------------------------------------------
time_flag                = 'time'                   # time or timescale as time dimension?
variable                 = 't2m'                     # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain                   = 'europe'                 # flag for geographical domain for analysis, e.g, europe, nordic.
first_forecast_date      = '2022-01'
number_forecasts         = 12      
box_sizes                = np.arange(1,61,2)        # np.array([1,9,19,29,39,49,59])  # neighborhood size in grid points per side
number_shuffle_bootstrap = 10000                    # number of times to shuffle initialization dates for error bars
number_sample_bootstrap  = 12                       # number of sampled forecasts with replacement in each bootstrap member
comp_lev                 = 5                        # compression level (0-10) of netcdf putput file
write2file               = True
# -----------------------------------------------------


misc.tic()

# define stuff
forecast_dates       = pd.date_range(first_forecast_date,periods=number_forecasts,freq="M").strftime('%Y-%m').values
path_in_forecast     = config.dirs['seasonal_forecast_monthly_anomaly'] + variable + '/'
path_in_verification = config.dirs['era5_seasonal_forecast_monthly_anomaly'] + variable + '/'
path_out             = config.dirs['verify_seasonal_forecast_monthly']
filename_out         = 'time_vs_ss_fss_anomaly_' + variable + '_' + domain + '_' + forecast_dates[0] + '_' + forecast_dates[-1] + '.nc'

# initialize fss output array
dim                 = misc.get_dim('1.0x1.0','time')
[fss,fss_bootstrap] = verify.initialize_fss_array(dim,box_sizes,number_shuffle_bootstrap)
forecast_error      = verify.initialize_error_array(dim,box_sizes,forecast_dates)
reference_error     = verify.initialize_error_array(dim,box_sizes,forecast_dates)

# loop over forecasts
for  i, date in enumerate(forecast_dates):

    print('percent complete: ' + str(i/forecast_dates.size*100) + ', calculating forecast ' + date)
    
    # define input filenames for forecast & observation anomalies
    filename_verification = path_in_verification + variable + '_' + date + '.nc'
    filename_forecast     = path_in_forecast + variable + '_' + date + '.nc'

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

