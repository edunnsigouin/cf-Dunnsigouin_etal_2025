"""                                                                                                                                                                                       
explore Trygs new dataset
"""

import numpy    as np
import pandas   as pd
import xarray   as xr
from investor   import config, misc
from matplotlib import pyplot as plt

# input ---------------------------
write2file = False
# --------------------------------- 

# Load the Excel file into a pandas DataFrame
path_in      = config.dirs['raw_tryg']
path_out     = config.dirs['processed_tryg']
filename_in  = path_in + '24-12-05-climate_futures_20241004_exposure_and_claims_nhh.csv'
#filename_out = path_out + 'tryg_' + variable + '_claims_monthly.nc'
df           = pd.read_csv(filename_in)

print(df)

column_titles = df.columns
print(column_titles)

for date in df['MUNICIPALITY']:
    if date == 3322:
        print(date)
