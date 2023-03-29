"""
compares scipy.signal.convolve2d and scipy.ndimage.convolve
"""

import numpy  as np
import xarray as xr
from scipy    import signal,ndimage

NH         = 3
win        = np.ones((NH,NH))
win        = win[None,None,:,:]

print(win.shape)

data          = np.zeros((3,3,3,3))
data[0,0,1,1] = 18.0
data[1,1,1,1] = 9.0

# method 1
#frac1 = signal.convolve2d(data, win, mode='same', boundary='fill',fillvalue=0.0)/NH**2

# method2
frac2 = ndimage.convolve(data, win, mode='constant', cval=0.0, origin=0)/NH**2

print(data[1,1,:,:])
print(win[0,0,:,:])
#print(frac1[:,:])
print(frac2[1,1,:,:])

