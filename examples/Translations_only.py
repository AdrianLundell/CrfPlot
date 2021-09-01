#%%
from HelmertTool.transform import *
from HelmertTool.regression import *
from HelmertTool.load import *
import numpy as np

#%%
b = load_sta("C:/Users/Adrian/Documents/NVI/HelmertTool/data/2020d.sta")
a = load_sta("C:/Users/Adrian/Documents/NVI/HelmertTool/data/2020d_off_0_0_10p_rate_0_0_0.sta")
n = len(a.index) 

residuals = (a[["X", "Y", "Z"]] - b[["X", "Y", "Z"]])*1000
variances = (a[["X_sigma", "Y_sigma", "Z_sigma"]]*1000)**2 + (b[["X_sigma", "Y_sigma", "Z_sigma"]]*1000)**2

#%% Calculate translation parameters, seperate calculations
for dim in ["X", "Y", "Z"]:
    X = np.ones((n,1))
    y = np.array(residuals[dim]).reshape(n,1)
    y_var = np.diag(variances[dim + "_sigma"])

    o_par = ordinary_least_squares(X, y)
    w_par, w_par_unsc = weighted_least_squares(X, y, y_var)

    print(f"{dim} : {o_par}/{w_par}/{w_par_unsc['C0']} (par/weight par/unsc)")

#%%Calculate translation parameters, one calculation 
X_list = []
y_list = []
y_var_list = []

for i, dim in enumerate(["X", "Y", "Z"]):
    X_temp = np.zeros((n,3))
    X_temp[:,i:i+1] = np.ones((n,1))
    X_list.append(X_temp)

    y_list.append(np.array(residuals[dim]).reshape(n,1))
    y_var_list.append(np.array(variances[dim + "_sigma"]).reshape(n))

X = np.vstack(X_list)
y = np.vstack(y_list)
y_var = np.diag(np.hstack(y_var_list))

o_par = ordinary_least_squares(X, y)
w_par, w_par_unsc = weighted_least_squares(X, y, y_var)

print(o_par, w_par, w_par_unsc)

"""
Unweighted Transform:	55,30	13,95	6,65
			
Weighted Transform	51,54230329	63,59747675	58,64105015
Sigma	0,272189593	0,169984491	0,17453374
			
			
			
Chi-square(No translation)	99130	280280	147091
Chi-square(After)	63272	140302	34204
			
Note that chi-square is reduced.			

"""