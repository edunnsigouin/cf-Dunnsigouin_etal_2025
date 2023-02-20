"""
Collection of useful miscellaneous functions
"""

import time
import numpy  as np
import xarray as xr

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
    with cosine weighting in lat
    """
    weights = np.cos(np.deg2rad(ds.latitude))
    ds      = ds.weighted(weights).mean(dim=('latitude','longitude'))
    return ds        


def convert_xyt_np_to_xr(array,name,description,units,dim):
    """
    converts xyt numpy array to xarray dataset 
    """
    da = xr.DataArray(
            data=array,
            dims=["time","latitude", "longitude"],
            coords=dict(longitude=(["longitude"], dim.longitude),
                        latitude=(["latitude"], dim.latitude),
                        time=dim.time),
            attrs=dict(description=description,
                       units=units))
    ds = da.to_dataset(name=name)

    return ds


def get_domain_dim(domain,dim):
    """
    outputs lat and lon array of domain
    given as a string
    """
    if domain == 'europe':
        dim = dim
    elif domain == 'nordic':
        dim.latitude   = np.flip(np.arange(53,73.75,0.25))
        dim.longitude  = np.arange(0,35.25,0.25)
        dim.nlatitude  = dim.latitude.size
        dim.nlongitude = dim.longitude.size
    
    return dim
