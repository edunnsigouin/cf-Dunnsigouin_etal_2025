import numpy as np

#X = np.array([[1,1,1],[1,0,0],[0,0,0]])
X = np.random.choice([0, 1], size=(100,100))

Y = np.zeros_like(X)
Y[:,:] = X.sum(axis=1).sum(axis=0)/(X.shape(0)*X.shape(1))

print(Y.shape)
print(X.shape)

"""
print(Y)

error = (X - Y)**2

MSE = error.sum(axis=1).sum(axis=0)/9

MSE_REF = (1/9)*(np.sum(np.sum(X**2,axis=1),axis=0) + np.sum(np.sum(Y**2,axis=1),axis=0))

FSS = 1 - MSE/MSE_REF

FSS_UNI = 0.5 + x/2 

print(FSS,FSS_UNI)
"""

