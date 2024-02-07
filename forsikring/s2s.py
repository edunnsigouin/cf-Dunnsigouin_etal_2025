"""
Collection of miscellaneous functions + look up dictionaries 
for ecmwf s2s model data 
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
import os
from datetime   import datetime
from scipy      import signal, ndimage, stats

# dictionary of model versions with (start,end)     
model_version_specs = dict(
    ECMWF = dict(
        CY43R1 = ('2016-11-22','2017-07-10'),
        CY43R3 = ('2017-07-11','2018-06-05'),
        CY45R1 = ('2018-06-06','2019-06-10'),
        CY46R1 = ('2019-06-11','2020-06-29'),
        CY47R1 = ('2020-06-30','2021-05-10'),
        CY47R2 = ('2021-05-11','2021-10-11'),
        CY47R3 = ('2021-10-12',datetime.strftime(datetime.today(),"%Y-%m-%d"))
    )
)

def which_mv_for_init(fc_init_date,model='ECMWF',fmt='%Y-%m-%d'):
    """    
    return model version for a specified initialization date and model 
    INPUT:  
            fc_init_date:   date string YYYY-mm-dd, datetime.datetime    
                            or pandas.Timestamp
            model:          string for the modeling center (currently just
                            'ECMWF' is valid)
                            default: 'ECMWF'
            fmt:            string specifying the date format,  
                            default: '%Y-%m-%d'  
    OUTPUT:                                                                                                                                                
            model version as string
    """
    if isinstance(fc_init_date,str):
        # convert date string to datetime object: 
        fc_init_datetime = pd.Timestamp(fc_init_date)

    elif isinstance(fc_init_date,pd.Timestamp):
        fc_init_datetime = fc_init_date

    elif isinstance(fc_init_date,datetime.datetime):
        fc_init_datetime = pd.Timestamp(fc_init_date)

    else:
        raise TypeError(
            'Input of invalid type was given to date_to_model.which_mv_for_init'
            )
        return None

    # got through the model versions from the above dictionary:
    for MV,mv_dates in model_version_specs[model].items():
        # convert first and last dates to datetime:

        mv_first = pd.Timestamp(mv_dates[0])
        mv_last  = pd.Timestamp(mv_dates[-1])

        # check if the given date is within the current model version's 
        # start and end dates:
        if  mv_first <= fc_init_datetime <= mv_last:
            valid_version = MV
    try:
        return valid_version
    except:
        
        raise ValueError(
            'No matching model version found...'
            )
        return None


def get_forecast_dates(first_forecast_date,number_forecasts,season):
    """
    generate set of continuous dates on mondays and thursdays starting on init_start
    with length init_n
    """

    SEASONS = {
        'djf': [12, 1, 2],                  # December to February
        'mam': [3, 4, 5],                   # March to May
        'jja': [6, 7, 8],                   # June to August
        'son': [9, 10, 11],                  # September to November
        'ndjfm': [11, 12, 1, 2, 3],          
        'mjjas': [5, 6, 7, 8, 9],
        'annual': [1,2,3,4,5,6,7,8,9,10,11,12] # all year
    }
    
    if season not in SEASONS:
        raise ValueError(f"Invalid season. Choose from: {', '.join(SEASONS.keys())}")

    dates_monday          = pd.date_range(first_forecast_date, periods=number_forecasts, freq="W-MON") # forecasts that start monday
    dates_thursday        = pd.date_range(first_forecast_date, periods=number_forecasts, freq="W-THU")
    forecast_dates        = dates_monday.union(dates_thursday)
    forecast_dates        = forecast_dates[:number_forecasts]
    forecast_dates        = forecast_dates[forecast_dates.month.isin(SEASONS[season])]
    
    return forecast_dates



def grib_to_netcdf(path,filename_grb,filename_nc):
    """
    wrapper for eccode's grib_to_netcdf function
    """
    os.system('grib_to_netcdf ' + path + filename_grb + ' -I step -o ' + path + filename_nc)
    os.system('rm ' +  path + filename_grb)
    return


def convert_2_binary_RL08MWR(data,threshold):
    """
    Converts forecast data into binary. 1 above a given 
    threshold and zero below
    """
    # converts to true/false then 1's and 0's
    binary_data = (data >= threshold).astype(np.int32)
    
    return binary_data


def preprocess(ds,grid,time_flag):
    '''change time dim from calendar dates to numbers'''
    if time_flag == 'time':
        if grid == '0.25x0.25':
            ds['time'] = np.arange(1,16,1) 
        elif grid == '0.5x0.5':
            ds['time'] = np.arange(16,47,1) 
    elif time_flag == 'timescale':
        if grid == '0.25x0.25':
            ds['time'] = np.arange(1,5,1)
        elif grid == '0.5x0.5':
            ds['time'] = np.arange(1,3,1)
    return ds



def mask_significant_values_from_bootstrap(data_array, threshold):
    """
    Determine significance from bootstrapped samples based on a given threshold.

    Parameters:
    - data_array (xr.DataArray): The input data array with a dimension 'number_shuffle_bootstrap'. 
    - threshold (float): The quantile threshold for significance determination.                                                                                               
    Returns: 
    - xr.DataArray: A data array with 1s for non-significant values and nan values for significant ones. 
    """
    # two sided test. e.g. 5% significance means 2.5% percentile > 0.                                                                       
    threshold = threshold/2

    # Calculate the quantile values
    quantile_values = data_array.quantile(threshold, dim='number_shuffle_bootstrap', skipna=True)

    # Determine significance and mask significant values with nan
    significance_mask   = quantile_values < 0
    masked_significance = significance_mask.where(significance_mask, np.nan)

    return masked_significance.rename('significance')



def mask_skill_values(data_array):
    """ 
    test
    """
    significance_mask   = np.isnan(data_array)
    masked_significance = significance_mask.where(significance_mask, np.nan)

    return masked_significance
