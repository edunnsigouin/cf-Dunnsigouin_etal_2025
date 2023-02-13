# list of useful hardcoded coordinate grids ecwmwf s2s & era5 data
# with low resolution

import numpy as np

time       = np.arange(15,46,1)
latitude   = np.flip(np.arange(33,74,0.5))
longitude  = np.arange(-27,45.5,0.5)

ntime      = time.size
nlatitude  = latitude.size
nlongitude = longitude.size
