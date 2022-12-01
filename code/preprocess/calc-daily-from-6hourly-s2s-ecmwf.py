"""
Calculates daily quantities based off of downloaded 6hourly 
s2s ecmwf mars data
"""

import numpy    as np
import xarray   as xr
import pandas   as pd
import os
from forsikring import date_to_model  as d2m
from forsikring import config,misc,s2smisc

# INPUT ----------------------------------------------- 
variables     = ['tp']                  
dtypes        = ['cf']             # control & perturbed forecasts/hindcasts
product       = 'hindcast'              # hindcast or forecast ?
mon_thu_start = ['20210104','20210107'] # first monday & thursday initialization date of forecast
num_i_weeks   = 1                       # number of forecasts/hindcast intialization dates to download
grid          = '0.25/0.25'             # '0.25/0.25' or '0.5/0.5'
comp_lev      = 5                       # level of compression with nccopy (1-10)
write2file    = False
# -----------------------------------------------------            

# define encoding for compression when writing to file
#encoding = {'dtype':'int16',
#            'scale_factor':9.26033143309001e-06,
#            'add_offset':0.303424019736627,
#            '_FillValue':-9999,
#            'missing_value':-9999}


dates_monday_thursday = s2smisc.get_monday_thursday_dates(mon_thu_start,num_i_weeks)

for variable in variables:
    for date in dates_monday_thursday:
        for dtype in dtypes:

            misc.tic()
            
            datestring = date.strftime('%Y-%m-%d')
            print('variable: ' + variable + ', date: ' + datestring + ', dtype: ' + dtype)
            
            path_in    = config.dirs[product + '_6hourly']
            path_out   = config.dirs[product + '_daily']

            if grid == '0.25/0.25':
                gridstring = '0.25x0.25'
            elif grid == '0.5/0.5':
                gridstring = '0.5x0.5'
                
            forcastcycle  = d2m.which_mv_for_init(datestring,model='ECMWF',fmt='%Y-%m-%d')
            basename      = '%s_%s_%s_%s'%(forcastcycle,gridstring,datestring,dtype)
                
            if variable == 'tp': # daily accumulated precip (m)
                filename_in               = path_in + variable + '/' + variable + '_' + basename + '.nc'
                filename_out              = path_out + variable + '/' + variable + '_' + basename + '.nc'

                """
                ds                        = xr.open_dataset(filename_in,mask_and_scale=False)
                scale_factor              = ds[variable].attrs['scale_factor']
                add_offset                = ds[variable].attrs['add_offset']
                _FillValue                = ds[variable].attrs['_FillValue']
                missing_value             = ds[variable].attrs['missing_value']
                encoding                  = {variable:{'dtype':'int16','scale_factor':scale_factor,'add_offset':add_offset,
                                                       '_FillValue':_FillValue,'missing_value':missing_value}}
                ds.close()
                """

                ds                        = xr.open_dataset(filename_in)
                #ds                        = ds.resample(time='1D').sum('time')
                #ds.tp.attrs['units']      = 'm'
                #ds.tp.attrs['long_name']  = 'daily accumulated precipitation'

                dataMin      = ds[variable].min().values
                dataMax      = ds[variable].max().values
                add_offset   = dataMin
                scale_factor = (dataMax - dataMin) / (2^1000 - 1)
                print(scale_factor)
                encoding     = {variable:{'dtype':'int16',
                                          'scale_factor':scale_factor,
                                          'add_offset':add_offset,
                                          '_FillValue':-32767,
                                          'missing_value':-32767}}

                if write2file:
                    ds.to_netcdf(filename_out,encoding=encoding)
                    #ds.to_netcdf(filename_out,encoding={variable:encoding})
                    #ds.to_netcdf(filename_out)  
                ds.close()
                
"""
        elif variable == 'rn': # daily accumulated rain (precip - snowfall, m)
            dir_in1      = path_in + 'tp/'
            dir_in2      = path_in + 'sf/'
            dir_out      = path_out + variable + '/'
            filename1_in = 'tp_' + gridstring + '_' + str(year) + '.nc'
            filename2_in = 'sf_' + gridstring + '_' + str(year) + '.nc'
            ds1          = xr.open_dataset(dir_in1 + filename1_in)
            ds2          = xr.open_dataset(dir_in2 + filename2_in)
            ds1          = ds1.resample(time='1D').sum('time')
            ds2          = ds2.resample(time='1D').sum('time')
            ds1['tp']    = ds1['tp'] - ds2['sf']
            if write2file:
                filename_out              = 'rn_' + gridstring + '_' + str(year) + '.nc'
                ds1                       = ds1.rename({'tp':'rn'})
                ds1.rn.attrs['units']     = 'm'
                ds1.rn.attrs['long_name'] = 'daily accumulated rainfall'
                ds1.to_netcdf(dir_out + filename_out)
            ds1.close()
            ds2.close()
            
        elif variable == 'mxtp6': # daily maximum 6 hour accumulated precip (m)
            dir_in                    = path_in + 'tp/'
            dir_out                   = path_out + variable + '/'
            filename_in               = 'tp_' + gridstring + '_' + str(year) + '.nc'
            filename_out              =	variable + '_' + gridstring + '_' + str(year) + '.nc'
            ds                        = xr.open_dataset(dir_in + filename_in)
            ds                        = ds.resample(time='1D').max('time')
            ds.tp.attrs['units']      = 'm'
            ds.tp.attrs['long_name']  = 'daily maximum 6 hour accumulated precipitation'
            if write2file:
                ds.to_netcdf(dir_out + filename_out)
            ds.close()

        elif variable == 'mxtpr': # daily maximum timestep precipitation rate (kgm-2s-1)
            dir_in                      = path_in + variable + '/'
            dir_out                     = path_out + variable + '/'
            filename_in                 = variable + '_' + gridstring + '_' + str(year) + '.nc'
            filename_out                = variable + '_' + gridstring + '_' + str(year) + '.nc'
            ds                          = xr.open_dataset(dir_in + filename_in)
            ds                          = ds.resample(time='1D').max('time')
            ds.mxtpr.attrs['units']     = 'kg m**-2 s**-1'
            ds.mxtpr.attrs['long_name'] = 'daily maximum timestep precipitation rate'
            if write2file:
                ds.to_netcdf(dir_out + filename_out)
            ds.close()
            
        elif variable == 'mxrn6': # daily maximum 6 hour accumulated rain (precip - snowfall, m)
            dir_in1      = path_in + 'tp/'
            dir_in2      = path_in + 'sf/'
            dir_out      = path_out + variable + '/'
            filename1_in = 'tp_' + gridstring + '_' + str(year) + '.nc'
            filename2_in = 'sf_' + gridstring + '_' + str(year) + '.nc'
            ds1          = xr.open_dataset(dir_in1 + filename1_in)
            ds2          = xr.open_dataset(dir_in2 + filename2_in)
            da           = (ds1['tp'] - ds2['sf']).resample(time='1D').max('time')
            if write2file:
                filename_out             = variable + '_' + gridstring + '_' + str(year) + '.nc'
                da.name                  = variable
                da.attrs['units']        = 'm'
                da.attrs['long_name']    = 'daily maximum 6 hour accumulated rainfall'
                da.to_netcdf(dir_out + filename_out)
            ds1.close()
            ds2.close()
            da.close()
            
        print('compress file to reduce space..')
        cmd               = 'nccopy -k 3 -s -d ' + str(comp_lev) + ' '
        filename_out_comp = 'compressed_' + variable + '_' + gridstring + '_' + str(year) + '.nc'
        os.system(cmd + dir_out + filename_out + ' ' + dir_out + filename_out_comp)
        os.system('mv ' + dir_out + filename_out_comp + ' ' + dir_out + filename_out)
        
        misc.toc()
"""
