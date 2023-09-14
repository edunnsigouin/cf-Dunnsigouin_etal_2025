"""
Fills out the last two months of the system 5 seasonal forecast for year
2022 with data from system 5.1. The missing data for system 5 is due to 
the transition from system 5 to 5.1 where they stoppe dusing the latter.
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
from forsikring import misc,s2s,config

# Input -------------------------------
variables  = ['tp','t2m'] # 'tp' and 't2m'   
write2file = False
# -------------------------------------

for variable in variables:

    # define stuff  
    filename_system5  = variable + '_2022-system5.nc'
    filename_system51 = variable + '_2022-system51.nc'
    filename_dummy    = variable + '_2021.nc' # use as empty array with correct metadata
    filename_output   = variable + '_2022.nc'
    path              = config.dirs['seasonal_forecast_monthly'] + variable + '/'

    ds_system5  = xr.open_dataset(path + filename_system5).sel(time=slice('2022-01-01','2022-10-01'))[variable]
    ds_system51 = xr.open_dataset(path + filename_system51).sel(time=slice('2022-11-01','2022-12-01'))[variable]
    ds_output   = xr.open_dataset(path + filename_dummy)[variable]

    # dump into dummy dataset
    ds_output[:,:,10:12,:,:] = ds_system51[:,:,:,:,:].values
    ds_output[:,:,:10,:,:] = ds_system5[:,:,:,:,:].values

    # assign correct time dimension
    dates             = pd.date_range('2022-01-01',periods=12,freq="MS")
    ds_output['time'] = dates

    if write2file:
        ds_output.to_netcdf(path + filename_output)

