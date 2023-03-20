"""
Calculates and plots the fractional skill score plot from 
an idealized rain band case shown in Fig. 4 of Roberts and 
Lean 2008 MWR.
"""

import numpy as np
from matplotlib  import pyplot as plt
from forsikring  import misc,config



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





def calc_frac_faggian(N,Nx,Ny,data):
    """
    Generates fractions used summed area tables 
    following equations 3 and 5 from Faggian et al. 2015 mausam 
    given binary input data array. 
    """

    # calculate summed area table
    temp  = np.zeros([Nx,Ny])
    for i in range(0,Nx,1):
        for j in range(0,Ny,1):
            ii        = np.arange(0,i+1,dtype=int)
            jj        = np.arange(0,j+1,dtype=int)
            temp[i,j] = data[ii[0]:ii[-1]+1,jj[0]:jj[-1]+1].sum(axis=0).sum(axis=0) 

    # pad boundaries with zeros        
    SAT                = np.zeros([2*N+Nx,2*N+Ny])
    SAT[N:N+Nx,N:N+Ny] = temp[:,:]
            
    # calculate fractions        
    frac = np.zeros([2*N-1,2*N+Nx,2*N+Ny])     
    for n in range(1,2,2):
        for i in range(N,N+Nx,1):
            for j in range(N,N+Ny,1):
                
                i0 = int(i+(n-1)/2)
                i1 = int(i+(n-1)/2)
                i2 = int(i+(n-1)/2)
                i3 = i

                j0 = int(j-(n-1)/2)
                j1 = int(j+(n-1)/2)
                j2 = j 
                j3 = int(i+(n-1)/2)

                #frac[n,i,j] = (1/n**2)*(SAT[i-(n-1)/2,j-(n-1)/2] + SAT[i+(n-1)/2,j+(n-1)/2] - SAT[i+(n-1)/2,j] - SAT[i,j+(n-1)/2])
                frac[n-1,i,j] = (1/n**2)*(SAT[i0,j0] + SAT[i1,j1] - SAT[i2,j2] - SAT[i3,j3])
                print(SAT[i0,j0],SAT[i1,j1],SAT[i2,j2],SAT[i3,j3])
                
    return frac




# INPUT -----------------------
Nx         = 4
Ny         = 4
N          = np.maximum(Nx,Ny)
write2file = False
# -----------------------------

# define output filename                               
path_out  = config.dirs['fig'] + 'ecmwf/forecast/daily/'
figname   = 'temp'#'fss_RL08_fig04_' + 'Nx' + str(Nx) + '_Ny' + str(Ny) + '.pdf'

# initialize array of rain bands
Io               = np.zeros([Nx,Ny])
Im               = np.zeros([Nx,Ny])

Io = np.array([[1,0,0,0],[0,1,1,0],[0,1,1,0],[0,1,0,0]])

# calc fractions
temp = calc_frac(N,Nx,Ny,Io)
O    = calc_frac_faggian(N,Nx,Ny,Io)

print(temp[0,:,:])
print(O[0,:,:])

"""
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
ax.plot(x+1,FSS[x],color='k',linewidth=1.5)
ax.plot(x+1,FSS[x],marker='o',markersize=fontsize-5,color='k')
    
#ax.axhline(y=FSS_random, color='k', linestyle='--',linewidth=1.25)
#ax.axhline(y=FSS_uniform, color='k', linestyle='--',linewidth=1.25)
    
ax.legend(frameon=False,fontsize=fontsize)
ax.set_xticks(np.arange(0,60,10))
ax.set_xticklabels(np.arange(0,60,10),fontsize=fontsize)
ax.set_yticks(np.round(np.arange(0,1.2,0.2),2))
ax.set_yticklabels(np.round(np.arange(0,1.2,0.2),2),fontsize=fontsize)
ax.set_xlim([0,50])
ax.set_ylim([0,1.0])
ax.set_xlabel('grid squares',fontsize=fontsize)
ax.set_ylabel('fractions skill score',fontsize=fontsize)
plt.tight_layout()
if write2file: plt.savefig(path_out + figname)
plt.show()

"""

