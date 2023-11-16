# list of useful hardcoded coordinate grids ecwmwf s2s & era5 data
# with both low and high resolution.

import numpy as np

timescale = np.arange(1,7,1)
time      = np.arange(1,47,1)
latitude  = np.flip(np.arange(33,73.75,0.25)) # hack
longitude = np.arange(-27,45.25,0.25)

ntimescale = timescale.size
ntime      = time.size
nlatitude  = latitude.size
nlongitude = longitude.size
