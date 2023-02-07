# list of useful hardcoded coordinate grids ecwmwf s2s & era5 data
# with high resolution

import numpy as np

time      = np.arange(0,15,1)
latitude  = np.flip(np.arange(33,73.75,0.25))
longitude = np.arange(-27,45.25,0.25)

ntime      = time.size
nlatitude  = latitude.size
nlongitude = longitude.size
