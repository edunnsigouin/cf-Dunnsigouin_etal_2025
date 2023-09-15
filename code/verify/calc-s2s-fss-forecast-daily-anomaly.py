"""
Calculates the fractional skill score as a function of                                                                                                        
lead time and neighborhood size for ecmwf forecasts. Reference 
forecast is era5 climatology. Verification is era5. Code 
includes bootstrapping of forecast mse to put error bars on fss. 
Input is pre-processed data in model-format converted to anomalies 
from era5 or hindcast climatology.

NOTE: Here I don't need to read in reference era5 clim forecast
because when using anomalies, the equation fss = 1 - mse_forecast/mse_reference
simplifies to fss = 1 - mse_forecast/variance(obs). See chapter 5.4.2 of 
Joliffe and Stephenson text book  
"""

import numpy     as np
import xarray    as xr
import os
from forsikring  import misc,s2s,verify,config

# INPUT -----------------------------------------------
RF_flag           = 'clim'                   # clim or pers
variable          = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain            = 'europe'                 # europe or norway only?
init_start        = '20200102'               # first initialization date of forecast (either a monday or thursday)
init_n            = 313                      # number of forecasts 
NH                = np.arange(1,61,2)        # np.array([1,9,19,29,39,49,59])  # neighborhood size in grid points per side
nshuffle          = 10000                    # number of times to shuffle initialization dates for error bars
nsample           = 150                       # number of sampled forecasts with replacement in each bootstrap member
comp_lev          = 5                        # compression level (0-10) of netcdf putput file
write2file        = True
# -----------------------------------------------------

misc.tic()

# define stuff
grid             = '0.25x0.25'       # grid resolution
time_flag        = 'time'            # time or timescale
init_dates       = s2s.get_init_dates(init_start,init_n).strftime('%Y-%m-%d').values
path_in_F        = config.dirs['forecast_daily_anomaly'] + variable + '/'
path_in_O        = config.dirs['era5_forecast_anomaly'] + variable + '/'
path_out         = config.dirs['verify_forecast_daily']
filename_out     = 'time_fss_' + variable + '_' + 'forecast_' + RF_flag + '_' + \
                   'anomaly_0.25x0.25_' + domain + '_' + init_dates[0] + '_' + init_dates[-1] + '.nc'

# Get data dimensions and make sure they are consistent with those
# given the input options NH and ltime above
dim      = s2s.get_dim(grid,time_flag)
dim      = misc.subselect_xy_domain_from_dim(dim,domain,grid)

# initialize fss output array                                                                                              
[fss,fss_bs] = verify.init_fss(dim,NH,nshuffle)
F_error      = verify.init_error(dim,NH,init_dates)
RF_error     = verify.init_error(dim,NH,init_dates)

# loop over forecasts
for  i, date in enumerate(init_dates):

    print('percent complete: ' + str(i/init_dates.size*100) + ', calculating forecast ' + date)
    
    # define input filenames for forecast & observation anomalies
    filename_O  =  path_in_O + variable + '_' + time_flag + '_' + grid + '_' + date + '.nc'
    filename_F  =  path_in_F + variable + '_' + time_flag + '_' + grid + '_' + date + '.nc'

    # read in files to dataarray
    O = xr.open_dataset(filename_O)[variable]
    F = xr.open_dataset(filename_F)[variable] 

    # sub-select specific domain, lead times and percentile threshold
    O  = O.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
    F  = F.sel(latitude=dim.latitude,longitude=dim.longitude,method='nearest')
    
    # smooth forecast and observations in xy for each forecast
    # Should there be a cosine weighting when applying filter in y?
    O_smooth = verify.boxcar_smoother_xy(NH,O)
    F_smooth = verify.boxcar_smoother_xy(NH,F)

    O.close()
    F.close()

    # calc squared error for each forecast
    F_error_xy  = (F_smooth - O_smooth)**2
    RF_error_xy = (O_smooth)**2
            
    # average in space over entire domain and dump into dedicated error array
    F_error[i,...]  = misc.xy_mean(F_error_xy).values
    RF_error[i,...] = misc.xy_mean(RF_error_xy).values


# calc fss with bootstraping over all forecasts
[fss,fss_bs] = verify.calc_fss_bootstrap(fss,fss_bs,RF_error,F_error,nshuffle,nsample,init_dates,NH)

# write to file
if write2file:
    ds = xr.merge([fss,fss_bs])
    ds.to_netcdf(path_out+filename_out)
    s2s.compress_file(comp_lev,3,filename_out,path_out) 

misc.toc()

