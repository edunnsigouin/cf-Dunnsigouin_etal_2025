"""
Calculates and plots the fractional skill score plot from 
an idealized rain band case shown in Fig. 4 of Roberts and 
Lean 2008 MWR.
"""

import numpy as np

# INPUT -----------------------
Nx         = 3
Ny         = 3
N          = np.maximum(Nx,Ny)
write2file = False
# -----------------------------

# initialize array of rain bands
Io      = np.zeros([Nx,Ny])
Im      = np.zeros([Nx,Ny])
Io[:,0] = 1
Im[:,2] = 1

print(Io)
#print(Im)

# generate fractions
O = np.zeros([N,Nx,Ny])
M = np.zeros([N,Nx,Ny])

for n in range(3,5,2): #range(1,2*N,2):
    for i in range(0,1):#range(0,Nx):
        for j in range(0,1):#range(0,Ny):

            k        = np.arange(0, n, dtype=int)
            l        = np.arange(0, n, dtype=int)
            ii       = (i + k  - (n-1)/2).astype(int)
            jj       = (j + l  - (n-1)/2).astype(int)

            print('n = ',n)
            #print(i,j)
            #print(k,l)
            #print(ii,jj)
            
            temp_ii  = np.copy(ii)
            temp_jj  = np.copy(jj)
            ii       = ii[(temp_ii > -1) & (temp_ii < Nx)]
            jj       = jj[(temp_jj > -1) & (temp_jj < Ny)]

           
            print(Io[ii[0]:ii[-1]+1,jj[0]:jj[-1]+1])
            #print(ii.shape,jj.shape)
            O[n,i,j] = Io[ii,jj].sum(axis=0).sum(axis=0)/n**2 

    

"""
N      = 3     
X      = np.random.choice([0, 1], size=(N,N))
Y      = np.zeros([N,N])
Y[:,:] = X.sum(axis=1).sum(axis=0)/(X.shape[0]*X.shape[1])

error = (X - Y)**2

MSE = error.sum(axis=1).sum(axis=0)/N**2

MSE_REF = (1/N**2)*(np.sum(np.sum(X**2,axis=1),axis=0) + np.sum(np.sum(Y**2,axis=1),axis=0))

FSS = 1 - MSE/MSE_REF

FSS_UNI = 0.5 + Y[0,0]/2 

print(X)
print(Y)
print(FSS,FSS_UNI)
"""

