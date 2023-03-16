"""
Calculates and plots the fractional skill score plot from 
an idealized rain band case shown in Fig. 4 of Roberts and 
Lean 2008 MWR.
"""

import numpy as np
from matplotlib  import pyplot as plt

def calc_frac(N,Nx,Ny,data):
    """
    Generates fractions following equations 2 and 3 from
    Roberts and Lean 2008 MWR given binary input data
    """

    frac = np.zeros([2*N-1,Nx,Ny])
    
    for n in range(1,2*N,2):
        for i in range(0,Nx):
            for j in range(0,Ny):

                k             = np.arange(0, n, dtype=int)
                l             = np.arange(0, n, dtype=int)
                ii            = (i + k  - (n-1)/2).astype(int)
                jj            = (j + l  - (n-1)/2).astype(int)
                temp_ii       = np.copy(ii)
                temp_jj       = np.copy(jj)
                ii            = ii[(temp_ii > -1) & (temp_ii < Nx)]
                jj            = jj[(temp_jj > -1) & (temp_jj < Ny)]
                frac[n-1,i,j] = data[ii[0]:ii[-1]+1,jj[0]:jj[-1]+1].sum(axis=0).sum(axis=0)/n**2
    
    return frac



# INPUT -----------------------
Nx         = 25
Ny         = 25
N          = np.maximum(Nx,Ny)
write2file = False
# -----------------------------

# initialize array of rain bands
Io      = np.zeros([Nx,Ny])
Im      = np.zeros([Nx,Ny])
Io[:,0] = 1
Im[:,10] = 1

#print(Io)
#print(Im)

# calc fractions
O = calc_frac(N,Nx,Ny,Io)
M = calc_frac(N,Nx,Ny,Im)

# calc MSE
error   = (O - M)**2
MSE     = error.sum(axis=2).sum(axis=1)/Nx/Ny

MSE_REF = (1/Nx/Ny)*(np.sum(np.sum(O**2,axis=2),axis=1) + np.sum(np.sum(M**2,axis=2),axis=1))


# calc fractional skill score
FSS =  1.0 - MSE/MSE_REF

# plot 
fontsize  = 11
figsize   = np.array([4*1.61,4])
fig,ax    = plt.subplots(nrows=1,ncols=1,figsize=(figsize[0],figsize[1]))

x = np.arange(0,2*N,2)
ax.plot(x,FSS[x],'k*')
plt.tight_layout()
plt.show()


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

