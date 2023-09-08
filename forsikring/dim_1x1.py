# list of useful hardcoded coordinate grids for 1x1 resolution data


import numpy as np

latitude  = np.flip(np.arange(33,75,1.0))
longitude = np.arange(-27,46,1.0)

nlatitude  = latitude.size
nlongitude = longitude.size
