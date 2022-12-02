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
