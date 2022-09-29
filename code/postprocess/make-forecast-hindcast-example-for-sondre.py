"""
Makes example forecast and hindcast files for Sondre at NHH. I just modified the already available
files from ecmwf at low resolution and converted from grib to netcdf for simplicity.
"""

import numpy as nc
import xarray as xr

# INPUT ------------------------------------
write2file = True
# ------------------------------------------

hc_dir   = '/nird/projects/NS9853K/DATA/S2S/hindcast/ECMWF/sfc/tp/'
fc_dir   = '/nird/projects/NS9853K/DATA/S2S/forecast/ECMWF/sfc/tp/'
filename = 'tp_CY46R1_2020-06-25_pf.grb'

ds_hc = xr.open_dataset(hc_dir + filename,engine='cfgrib').sel(latitude=60,longitude=6)
ds_fc = xr.open_dataset(fc_dir + filename,engine='cfgrib').sel(latitude=60,longitude=6)

if write2file:
    out_dir         = '/nird/projects/NS9853K/www/nhh/example.forecast.ecwmf/'
    out_filename_hc = 'hc_tp_CY46R1_2020-06-25_pf.nc'
    out_filename_fc = 'fc_tp_CY46R1_2020-06-25_pf.nc'
    ds_hc.to_netcdf(out_dir + out_filename_hc)
    ds_fc.to_netcdf(out_dir + out_filename_fc)
