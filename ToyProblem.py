#%%
from logic import *
from regression import *
import numpy as np

b = load_sta("C:/Users/Adrian/Documents/NVI/CrfPlot/data/2020d.sta")
a = load_sta("C:/Users/Adrian/Documents/NVI/CrfPlot/data/2020d_off_0_0_10p_rate_0_0_0.sta")
n = len(a.index) 

residuals = (a[["X", "Y", "Z"]] - b[["X", "Y", "Z"]])*1000
variances = (a[["X_sigma", "Y_sigma", "Z_sigma"]]*1000)**2 + (b[["X_sigma", "Y_sigma", "Z_sigma"]]*1000)**2

#%%
for dim in ["X", "Y", "Z"]:
    X = np.ones((n,1))
    y = np.array(residuals[dim]).reshape(n,1)
    y_var = np.diag(variances[dim + "_sigma"])

    o_par = ordinary_least_squares(X, y)
    w_par, w_par_unsc = weighted_least_squares(X, y, y_var)

    print(f"{dim} : {o_par['C0']}/{w_par['C0']}/{np.sqrt(w_par_unsc['C0'])} (par/weight par/unsc)")

