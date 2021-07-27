#%%
from logic import *
from regression import *
import numpy as np

#%%
b = load_sta("C:/Users/Adrian/Documents/NVI/CrfPlot/data/2020d.sta")
a = load_sta("C:/Users/Adrian/Documents/NVI/CrfPlot/data/2020d_off_0_0_10p_rate_0_0_0.sta")
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

    print(f"{dim} : {o_par['C0']}/{w_par['C0']}/{w_par_unsc['C0']} (par/weight par/unsc)")

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

# %% load data
import pandas as pd
import numpy as np
import logic 

def load_ssc(fpath: str):
    """Load a .ssc TRF file to a pandas dataframe"""
    
    column_names = ["Station_Name", "X", "Y", "Z", "X_sigma", "Y_sigma", "Z_sigma"]
    column_specs = [(10, 26), (37,50), (50, 64), (64,77), (79,85), (86,92), (93,99)]
    
    df = pd.read_fwf(fpath, skiprows=7)
    df = df.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
    df.columns = ["Domes", "Station_Name", "Tech", "Code", "X", "Y", "Z", "X_sigma", "Y_sigma", "Z_sigma", "Soln"]
    df.Soln = df.Soln.fillna(1)
    df = df.dropna()    
    
    if df.Code.dtype == np.float64:
        df.Code = df.Code.astype(int).astype(str)    
    
    df = df.reset_index(drop=True)
    df[["X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma"]] = df[["X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma"]].astype(np.float64)

   # df = calculate_long_lat(df)
    df = df.set_index(df.Station_Name)
    return df


true_parameters = [1.6,	1.9, 2.4, -0.02, 0.000, 0.000, 0.000]
true_sigmas = [0.2, 0.1, 0.1, 0.02, 0.006, 0.006, 0.006]

stations_df = pd.read_fwf("C:/Users/Adrian/Documents/NVI/CrfPlot/data/core_network_ITRF2014.txt", skiprows=5)
stations_df.columns = ["Code", "Domes", "Soln", "Tech", "Station_Name", "LONGLAT"]
stations_df = stations_df.drop(columns="Station_Name")

doris_df_2014 = load_ssc("C:/Users/Adrian/Documents/NVI/CrfPlot/data/ITRF2014_DORIS.SSC")
gnss_df_2014 = load_ssc("C:/Users/Adrian/Documents/NVI/CrfPlot/data/ITRF2014_GNSS.SSC")
gnss_df_2014.Tech = "GPS"
slr_df_2014 = load_ssc("C:/Users/Adrian/Documents/NVI/CrfPlot/data/ITRF2014_SLR.SSC")
vlbi_df_2014 = load_ssc("C:/Users/Adrian/Documents/NVI/CrfPlot/data/ITRF2014_VLBI.SSC")
df_2014 = pd.concat([gnss_df_2014, slr_df_2014, doris_df_2014, vlbi_df_2014])

doris_df_2008 = load_ssc("C:/Users/Adrian/Documents/NVI/CrfPlot/data/ITRF2008_DORIS.SSC")
gnss_df_2008 = load_ssc("C:/Users/Adrian/Documents/NVI/CrfPlot/data/ITRF2008_GNSS.SSC")
gnss_df_2008.Tech = "GPS"
slr_df_2008 = load_ssc("C:/Users/Adrian/Documents/NVI/CrfPlot/data/ITRF2008_SLR.SSC")
vlbi_df_2008 = load_ssc("C:/Users/Adrian/Documents/NVI/CrfPlot/data/ITRF2008_VLBI.SSC")
df_2008 = pd.concat([gnss_df_2008, slr_df_2008, doris_df_2008, vlbi_df_2008])

df_from = stations_df.merge(df_2014, how = "left", on=["Domes", "Soln"])
df_from = df_from.set_index(df_from.Station_Name)

df_to = stations_df.merge(df_2008, how = "left", on=["Domes", "Soln"])
df_to = df_to.set_index(df_to.Station_Name)
# %%
print(logic.calculate_parameters(df_from, df_to, True, "7"))

# %% 
