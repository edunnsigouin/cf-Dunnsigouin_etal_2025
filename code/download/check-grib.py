import numpy as np
import xarray as xr
from matplotlib              import pyplot as plt

path = '/nird/projects/NS9853K/DATA/S2S/MARS/hindcast/ECMWF/sfc/tp/'
#filename = 'tp_CY47R1_05x05_2021-01-04_pf.grb'
filename = 'test.grib'

ds = xr.open_dataset(path+filename, engine="cfgrib")

print(ds)

plt.plot(ds.tp.values)
#plt.contourf(ds.tp)
plt.show()

#ds = xr.open_dataset('era5-levels-members.grib', engine='cfgrib')
#print(ds)


#plt.contourf(ds.z[0,0,0,:,:])
#plt.show()
