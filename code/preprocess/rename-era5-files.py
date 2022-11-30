"""                                                                                                                                                                                                                        
renames era5 files to lincude grid resolution in filename
"""

import numpy  as np
import xarray as xr
import os
from forsikring import config

# INPUT ----------------------------------------------- 
grid       = '0.5/0.5' # '0.25/0.25' or '0.5/0.5'
variables  = ['tp','mxtpr','rn','mxrn6','mxtp6']
years      = np.arange(1995,2022,1)
write2file = True
# -----------------------------------------------------       

for variable in variables:

    if grid == '0.25/0.25':
        path       = config.dirs['era5_daily'] + '/0.25x0.25/' + variable + '/'
        gridstring = '0.25x0.25'
    elif grid == '0.5/0.5':
        path       = config.dirs['era5_daily'] + '/0.5x0.5/' + variable + '/'
        gridstring = '0.5x0.5'
        
    for year in years:

        if write2file == True:
            filename_old = variable + '_' + str(year) + '.nc'
            filename_new = variable + '_' + gridstring + '_' + str(year) + '.nc'
            print('renaming ' + filename_old + ' to ' + filename_new)
            os.rename(path + filename_old,path + filename_new)
