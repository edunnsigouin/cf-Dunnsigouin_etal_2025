"""
Converts s2s forecast format data into anomaly relative
to smoothed climatological mean from hindcast data for Fig. 6 of paper.
Anomalies are normalized. 
If daily forecast date does not correspond to bi-weekly hindcast date,
the we use the most recent hindcast as the climatology for a given forecast. 
"""

import numpy      as np
import xarray     as xr
import pandas     as pd
import os
from   datetime   import datetime
from   forsikring import misc,s2s,config,verify
from   scipy      import stats
import matplotlib.pyplot as plt

def find_most_recent_hindcast(forecast_file, hindcast_dir):
    # Extract date from the forecast filename
    forecast_date_str = os.path.basename(forecast_file).split('_')[-1].split('.')[0]
    forecast_date = datetime.strptime(forecast_date_str, '%Y-%m-%d')
    
    # List all hindcast files in the directory
    hindcast_files = [f for f in os.listdir(hindcast_dir) if f.endswith('.nc')]
    
    # Find the most recent hindcast file
    most_recent_hindcast = None
    most_recent_date = None
    
    for file in hindcast_files:
        hindcast_date_str = file.split('_')[-1].split('.')[0]
        hindcast_date = datetime.strptime(hindcast_date_str, '%Y-%m-%d')
        
        if hindcast_date <= forecast_date:
            if most_recent_date is None or hindcast_date > most_recent_date:
                most_recent_hindcast = file
                most_recent_date = hindcast_date
    
    return os.path.join(hindcast_dir, most_recent_hindcast) if most_recent_hindcast else None


def init_EFI(forecast):

    box_size  = forecast['box_size']
    time      = forecast['time']
    latitude  = forecast['latitude']
    longitude = forecast['longitude']

    data       = np.zeros((box_sizes.size,time.size,dim.nlatitude,dim.nlongitude),dtype=np.float32)
    dims       = ["box_size","time","latitude","longitude"]
    coords     = dict(box_size=box_sizes,time=time,latitude=latitude,longitude=longitude)

    units       = 'none: 0-1'
    description = 'ecmwf extreme forecast index'

    attrs      = dict(description=description,units=units)
    name       = 'EFI'
    
    return xr.DataArray(data=data,dims=dims,coords=coords,attrs=attrs,name=name)


def calculate_EFI(forecast,hindcast,dq):

    # re-order forecast and hindcast dimensions for convenience
    hindcast = hindcast.transpose('box_size','hdate','number','time','latitude','longitude')
    forecast = forecast.transpose('box_size','number','time','latitude','longitude')

    # define stuff
    box_size = forecast['box_size'].size
    number   = forecast['number'].size
    EFI      = init_EFI(forecast)

    # calculate EFI for each smoothing box_size
    for bs in range(box_size):

        print(bs)
        
        # work with number arrays for speed
        hindcast_temp = hindcast[bs,:].values
        forecast_temp = forecast[bs,:].values
        
        # Reshape the hindcast array to combine the 'hdate' and 'number' dimensions
        dim_sizes      = hindcast_temp.shape
        hindcast_temp  = hindcast_temp.reshape(dim_sizes[0] * dim_sizes[1], *dim_sizes[2:])

        # Calculate quantiles for the hindcast along the combined dimension
        q   = np.arange(dq,1.0,dq)
        qx  = np.quantile(hindcast_temp,q,axis=0)

        # Calculate the fraction of forecast members below each hindcast quantile
        fq = np.zeros((qx.shape))
        for i in range(q.size):
            fq[i,:] = (forecast_temp < qx[i,:]).sum(axis=0)/number

        # Vectorized calculation of EFI
        EFI[bs,:] = (2 / np.pi) * np.sum((q[:, np.newaxis, np.newaxis, np.newaxis] - fq) / \
                        np.sqrt(q[:, np.newaxis, np.newaxis, np.newaxis] * (1 - q[:, np.newaxis, np.newaxis, np.newaxis]))*dq, axis=0)
    
    return EFI


def initialize_score_array(time,box_sizes,name):
    """
    Initializes score array.
    Written here to clean up code.     
    """
    data   = np.zeros((box_sizes.size,time.size),dtype=np.float32)
    dims   = ["box_size","time"]
    coords = dict(box_size=box_sizes,time=time)
    name   = name
    score  = xr.DataArray(data=data,dims=dims,coords=coords,name=name)
    return score



# INPUT -----------------------------------------------
time_flag           = 'daily'                 # daily or weekly
variable            = 'tp24'              # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
first_forecast_date = '20230731'             # first initialization date of forecast (either a monday or thursday)
number_forecasts    = 1                      # number of forecasts 
season              = 'annual'
grid                = '0.25x0.25'          # '0.25x0.25' & '0.5x0.5'
domain              = 'scandinavia'
box_sizes           = np.arange(1,61,2)        # smoothing box size in grid points per side. Must be odd!  
write2file          = True
# -----------------------------------------------------

# get forecast dates
forecast_dates = pd.date_range(first_forecast_date, periods=number_forecasts).strftime('%Y-%m-%d')
print(forecast_dates)

for date in forecast_dates:

    misc.tic()
    print('\n ' + variable + ', ' + grid + ', ' + date)

    # 1) calculate EFI 
    # define stuff
    path_in_forecast1  = config.dirs['s2s_forecast_daily'] + variable + '/'
    path_in_hindcast1  = config.dirs['s2s_hindcast_daily'] + variable + '/'
    path_out           = config.dirs['s2s_forecast_' + time_flag + '_EFI'] + '/' + domain + '/' + variable + '/'
    filename_forecast1 = path_in_forecast1 + variable + '_' + grid + '_' + date + '.nc'
    filename_hindcast1 = find_most_recent_hindcast(filename_forecast1, path_in_hindcast1) # find most recent bi-weekly hindcast! 
    filename_out       = path_out + variable + '_' + grid + '_' + date + '_EFI.nc'
    
    # read forecast and hindcast format data from specific domain
    dim       = verify.get_data_dimensions(grid, time_flag, domain)
    forecast1 = xr.open_dataset(filename_forecast1).sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')[variable]
    hindcast1 = xr.open_dataset(filename_hindcast1).sel(latitude=dim.latitude, longitude=dim.longitude, method='nearest')[variable]

    # apply spatial smoothing. Note here that in order to standardize correctly,
    # you need to smooth the forecast & hindcast before standardizing since                                                                              
    # its not a linear operation.  
    forecast1 = verify.boxcar_smoother_xy_optimized(box_sizes, forecast1, 'xarray')
    hindcast1 = verify.boxcar_smoother_xy_optimized(box_sizes, hindcast1, 'xarray')

    # calculate extreme forecast index
    EFI = calculate_EFI(forecast1,hindcast1,dq=0.01)
    
    # 2) Calculate FMSESS 
    path_in_forecast2        = config.dirs['s2s_forecast_' + time_flag + '_anomaly'] + '/' + domain + '/' + variable + '/'
    path_in_verification2    = config.dirs['era5_forecast_' + time_flag + '_anomaly'] + '/' + domain + '/' + variable + '/'
    filename_verification2   = path_in_verification2 + variable + '_' + grid + '_' + date + '.nc'
    filename_forecast2       = path_in_forecast2 + variable + '_' + grid + '_' + date + '.nc'

    fmsess                        = initialize_score_array(forecast1.time,box_sizes,'fmsess')
    forecast_mse2, reference_mse2 = verify.calc_forecast_and_reference_error('fmsess', filename_verification2, filename_forecast2, variable, box_sizes,grid)
    fmsess[:,:]                   = 1.0 - forecast_mse2 / reference_mse2

    
    # Calculate FBSS
    pval                    = 0.9
    path_in_forecast3       = config.dirs['s2s_forecast_' + time_flag + '_probability'] + str(pval) + '/' + domain + '/' + variable + '/'
    path_in_verification3   = config.dirs['era5_forecast_' + time_flag + '_binary'] + str(pval) + '/' + domain + '/' + variable + '/'
    filename_verification3  = path_in_verification3 + variable + '_' + grid + '_' + date + '.nc'
    filename_forecast3      = path_in_forecast3 + variable + '_' + grid + '_' + date + '.nc'

    fbss                          = initialize_score_array(forecast1.time,box_sizes,'fbss')
    forecast_mse3, reference_mse3 = verify.calc_forecast_and_reference_error('fbss', filename_verification3, filename_forecast3, variable, box_sizes, grid, pval)
    fbss[:,:]                     = 1.0 - forecast_mse3 / reference_mse3

    # modify metadata 
    forecast1                            = forecast1.rename(variable)
    forecast1                            = forecast1.mean(dim='number') # ensemble mean
    output                               = xr.merge([forecast1,EFI,fmsess,fbss])    
    output[variable]                     = output[variable]*1000 # convert from m to mm/day 
    output[variable].attrs['units']      = 'mm/day'                                                                                                                              
    output[variable].attrs['long_name']  = 'daily accumulated precipitation'  
    output['fmsess'].attrs['units']      = 'none: -infty to +1'
    output['fmsess'].attrs['long_name']  = 'fractions mean-square error skill score'
    output['fbss'].attrs['units']        = 'none: -infty to +1'
    output['fbss'].attrs['long_name']    = 'fractions brier skill score'
    
    # write output
    if write2file: misc.to_netcdf_with_packing_and_compression(output, filename_out)

    forecast1.close()
    hindcast1.close()
    
    misc.toc()



