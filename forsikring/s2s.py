"""
Collection of miscellaneous functions for ecmwf s2s model data 
"""
import numpy    as np
import xarray   as xr
import pandas   as pd
import os


def get_monday_thursday_dates(mon_thu_start,num_i_weeks):
    """
    generate set of continuous monday and thursday dates starting on mon_thu_start[0] and mon_thu_start[1] respectively
    """
    dates_monday          = pd.date_range(mon_thu_start[0], periods=num_i_weeks, freq="7D") # forecasts that start monday
    dates_thursday        = pd.date_range(mon_thu_start[1], periods=num_i_weeks, freq="7D") # forecasts that start thursday
    dates_monday_thursday = dates_monday.union(dates_thursday)
    return dates_monday_thursday


def compress_file(comp_lev,ncfiletype,filename,path_out):
    """
    wrapper for compressing file using nccopy
    """
    cmd           = 'nccopy -k ' + str(ncfiletype) + ' -s -d ' + str(comp_lev) + ' '
    filename_comp = path_out + 'temp.nc'
    os.system(cmd + filename + ' ' + filename_comp)
    os.system('mv ' + filename_comp + ' ' + filename)
    return


def to_netcdf_pack64bit(da,filename_out):
    """
    A wraper on xrray's to_netcdf with 64-bit
    encoding to pack the data.
    Modified from: https://stackoverflow.com/questions/57179990/compression-of-arrays-in-netcdf-file
    """
    n    = 16
    vmin = np.min(da).item()
    vmax = np.max(da).item()

    # stretch/compress data to the available packed range                                                                                                                                                    
    scale_factor = (vmax - vmin) / (2 ** n - 1)

    # translate the range to be symmetric about zero
    add_offset = vmin + 2 ** (n - 1) * scale_factor

    # write2file
    encoding = {da.name:{
                "dtype": 'int16',
                "scale_factor": scale_factor,
                "add_offset": add_offset,
                "_FillValue": -9999,
                "missing_value":-9999}}

    da.to_netcdf(filename_out,encoding=encoding,format='NETCDF3_64BIT')
    
    return
