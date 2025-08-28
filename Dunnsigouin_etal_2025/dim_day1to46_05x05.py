# list of useful hardcoded coordinate grids ecwmwf s2s & era5 data
# with low resolution

import numpy as np

timescale  = np.arange(1,7,1)
time       = np.arange(1,47,1)
latitude   = np.flip(np.arange(33,74,0.5))
longitude  = np.arange(-27,45.5,0.5)

ntimescale = timescale.size
ntime      = time.size
nlatitude  = latitude.size
nlongitude = longitude.size
