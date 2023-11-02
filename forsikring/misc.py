"""
Collection of useful miscellaneous functions
"""

import time
import numpy  as np
import xarray as xr
from scipy    import signal
import os

def tic():
    """
    matlab style tic function
    """
    global startTime_for_tictoc
    startTime_for_tictoc = time.time()
    return

def toc():
    """
    matlab style toc function
    """                        
    if 'startTime_for_tictoc' in globals():
        print("Elapsed time is " + str(time.time() - startTime_for_tictoc) + " seconds.")
    else:
        print("Toc: start time not set")
    return


def get_dim(grid,time_flag):
    """   
    imports data dimensions given a grid 
    """
    if grid == '0.25x0.25':
        from forsikring import dim_025x025 as dim
    elif grid == '0.5x0.5':
        from forsikring import dim_05x05 as dim
    elif grid == '1.0x1.0':
        from forsikring import dim_1x1 as dim
    else:
        from forsikring import dim_1x1 as dim
        
    if time_flag == 'timescale':
        dim.time  = dim.timescale
        dim.ntime = dim.ntimescale

    return dim


def xy_mean(ds):
    """ 
    calculates xy mean over dims lat and lon
    with cosine weighting in lat. Input is xarray
    dataarray or dataset
    """
    weights = np.cos(np.deg2rad(ds.latitude))
    ds      = ds.weighted(weights).mean(dim=('latitude','longitude'))
    return ds        

def rm_lpyr_days(data):
    """ 
    removes leap-year days from daily xrray dataset
    """
    return data.sel(time=~((data.time.dt.month == 2) & (data.time.dt.day == 29)))

def is_leap_year(year):
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return True
    else:
        return False

def get_season(ds,season):
    """
    Extracts times belonging to a given season
    input = xarray dataset or dataarray
    """
    months = ds['time.month']
    if season == 'ndjfm': index = (months >= 11) | (months <= 3)
    elif season == 'mjjas': index = (months >= 5) & (months <= 9)
    elif season == 'annual': index = (months >= 1) & (months <= 12)
    elif season == 'djf': index = (months >= 12) | (months <= 2)
    elif season == 'mam': index = (months >= 3) & (months <= 5)
    elif season == 'jja': index = (months >= 6) & (months <= 8)
    elif season == 'son': index = (months >= 9) & (months <= 11)
    elif season == 'jfm': index = (months >= 1) & (months <= 3)
    return ds.sel(time=index)


def subselect_xy_domain_from_dim(dim,domain,grid):
    """  
    sub-selects xy domain from dim                                                                                                       
    """
    if grid == '0.25x0.25':
        if domain == 'scandinavia':
            dim.latitude   = np.flip(np.arange(53,73.25,0.25))
            dim.longitude  = np.arange(2,32.25,0.25)
        elif domain == 'vestland':
            dim.latitude   = np.flip(np.arange(59,62.75,0.25))
            dim.longitude  = np.arange(4,8.75,0.25)
        elif domain == 'northern_europe':
            dim.latitude   = np.flip(np.arange(53.25,73.75,0.25))
            dim.longitude  = np.arange(-27,45.25,0.25)
        elif domain == 'southern_europe':
            dim.latitude   = np.flip(np.arange(33,53.25,0.25))
            dim.longitude  = np.arange(-27,45.25,0.25)
        elif domain == 'western_europe':
            dim.latitude   = np.arange(33,73.75,0.25)
            dim.longitude  = np.arange(-27,9.0,0.25)
        elif domain == 'eastern_europe':
            dim.latitude   = np.arange(33,73.75,0.25)
            dim.longitude  = np.arange(9.0,45.25,0.25)            
        elif domain == 'iberia':
            dim.latitude   = np.flip(np.arange(35,45.25,0.25))
            dim.longitude  = np.arange(-12,3.25,0.25)
    elif grid == '0.5x0.5':
        if domain == 'scandinavia':
            dim.latitude   = np.flip(np.arange(53,73.5,0.5))
            dim.longitude  = np.arange(2,32.5,0.5)
        elif domain == 'vestland':
            dim.latitude   = np.flip(np.arange(59,63,0.5))
            dim.longitude  = np.arange(4,9,0.5)
        elif domain == 'northern_europe':
            dim.latitude   = np.flip(np.arange(53,74,0.5))
            dim.longitude  = np.arange(-27,45.5,0.5)
        elif domain == 'southern_europe':
           dim.latitude   = np.flip(np.arange(33,53,0.5))
           dim.longitude  = np.arange(-27,45.5,0.5)
        elif domain == 'iberia':
            dim.latitude   = np.flip(np.arange(35,45.5,0.5))
            dim.longitude  = np.arange(-12,3.5,0.5)
            
    dim.nlatitude  = dim.latitude.size
    dim.nlongitude = dim.longitude.size
    return dim


def to_netcdf_with_compression(data,comp_lev,path,filename):
    """
    Uses xarray's native compression to write to netcdf with compression
    using to_netcdf function
    """
    # Define your compression options
    #compression_opts = {'zlib': True, 'complevel': comp_lev, 'shuffle': True}
    compression_opts = {'zlib': True, 'complevel': comp_lev}
    
    # Check if data is a DataArray or Dataset, set encoding and write to netcdf
    if isinstance(data, xr.DataArray):
        encoding = {data.name: compression_opts}  # Use the name of the DataArray
        data.to_netcdf(path+filename, format='NETCDF4', engine='netcdf4', encoding=encoding)
    elif isinstance(data, xr.Dataset):
        encoding = {var: compression_opts for var in data.data_vars}  # Apply to all variables
        data.to_netcdf(path+filename, format='NETCDF4', engine='netcdf4', encoding=encoding)
    else:
        raise TypeError("The array must be either an xarray DataArray or Dataset")
    return



def compress_file(comp_lev,ncfiletype,filename,path_out):
    """  
    wrapper for compressing file using nccopy
    """
    cmd           = 'nccopy -k ' + str(ncfiletype) + ' -s -d ' + str(comp_lev) + ' '
    filename_comp = 'temp_' + filename
    os.system(cmd + path_out + filename + ' ' + path_out + filename_comp)
    os.system('mv ' + path_out + filename_comp + ' ' + path_out + filename)
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
