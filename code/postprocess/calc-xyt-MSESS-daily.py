"""
Calculates the mean-square-error skill score as a function of x,y and 
lead time for ecmwf forecasts relative to era5 climatology or era5 persistence
"""

import numpy  as np
import xarray as xr
from dask.diagnostics   import ProgressBar
from forsikring import config,misc,s2s
from matplotlib         import pyplot as plt

# INPUT -----------------------------------------------
verification_flag = 'clim' 
variables         = ['tp24']                    # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
dates             = ['2021-01-04','2021-12-30'] # first monday & thursday initialization date of forecast
grids             = ['0.25x0.25']               # '0.25x0.25' & '0.5x0.5'
comp_lev          = 5
write2file        = False
# -----------------------------------------------------      

for variable in variables:
    for grid in grids:

        # read mse files
        path_in               = config.dirs['calc_forecast_daily'] + variable + '/'
        filename_verification = 'xyt_mse_' + verification_flag + '_' + grid + '_' + dates[0] + '_' + dates[-1] + '.nc'
        filename_forecast     = 'xyt_mse_ecmwf_' + grid + '_' + dates[0] + '_' + dates[-1] + '.nc'
        ds_verification       = xr.open_dataset(path_in + filename_verification)
        ds_forecast           = xr.open_dataset(path_in + filename_forecast)

        # calculate msess
        dim   = s2s.get_dim(grid)
        msess = np.zeros((dim.ntime,dim.nlatitude,dim.nlongitude))
        msess = 1 - ds_forecast['mse'].values/ds_verification['mse'].values

        ds_verification.close()
        ds_forecast.close()

        levels = np.linspace(-1.5, 1.5, 20+1)
        p = plt.contourf(dim.longitude,dim.latitude,msess[14,:,:],levels=levels,cmap='coolwarm')
        plt.colorbar(p)
        plt.show()
        
        if write2file:
            # turn numpy array into dataset
            output = xr.DataArray(
                data=msess,
                dims=["time","latitude", "longitude"],
                coords=dict(longitude=(["longitude"], dim.longitude),
                        latitude=(["latitude"], dim.latitude),
                        time=dim.time),
                attrs=dict(description="mean square error skill score",
                           units="test"))
            ds = output.to_dataset(name='msess')

            print('writing to file..')
            timestamp    = dates[0] + '_' + dates[-1]
            path_out     = config.dirs['calc_forecast_daily'] + variable + '/'
            filename_out = 'xyt_msess_ecmwf_vs_' + verification_flag + '_' + grid + '_' + timestamp + '.nc'
            s2s.to_netcdf_pack64bit(ds['msess'],path_out + filename_out)
            print('compress file to reduce space..\n')
            s2s.compress_file(comp_lev,3,filename_out,path_out)







        
