"""
Collection of useful miscellaneous functions
"""

import time
import numpy  as np
import xarray as xr
from scipy    import signal

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
        if domain == 'nordic':
            dim.latitude   = np.flip(np.arange(53,73.75,0.25))
            dim.longitude  = np.arange(0,35.25,0.25)
        elif domain == 'vestland':
            dim.latitude   = np.flip(np.arange(59,62.75,0.25))
            dim.longitude  = np.arange(4,8.75,0.25)
    elif grid == '0.5x0.5':
        if domain == 'nordic':
            dim.latitude   = np.flip(np.arange(53,74,0.5))
            dim.longitude  = np.arange(0,35.5,0.5)
        elif domain == 'vestland':
            dim.latitude   = np.flip(np.arange(59,63,0.5))
            dim.longitude  = np.arange(4,9,0.5)
    dim.nlatitude  = dim.latitude.size
    dim.nlongitude = dim.longitude.size
    return dim
