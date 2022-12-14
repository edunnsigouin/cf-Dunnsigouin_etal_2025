"""
Collection of miscellaneous functions + look up dictionaries 
for ecmwf s2s model data 
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
import os
from datetime   import datetime


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



def get_monday_thursday_dates(mon_thu_start,num_i_weeks):
    """
    generate set of continuous monday and thursday dates starting on mon_thu_start[0] and mon_thu_start[1] respectively
    """
    dates_monday          = pd.date_range(mon_thu_start[0], periods=num_i_weeks, freq="7D") # forecasts that start monday
    dates_thursday        = pd.date_range(mon_thu_start[1], periods=num_i_weeks, freq="7D") # forecasts that start thursday
    dates_monday_thursday = dates_monday.union(dates_thursday)
    return dates_monday_thursday


def grib_to_netcdf(path,filename_grb,filename_nc):
    """
    wrapper for eccode's grib_to_netcdf function
    """
    os.system('grib_to_netcdf ' + path + filename_grb + ' -I step -o ' + path + filename_nc)
    os.system('rm ' +  path + filename_grb)
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
