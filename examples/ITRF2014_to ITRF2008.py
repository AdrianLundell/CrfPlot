"""
Sample script for transforming between the ITRF2014 and ITRF2008 frame with the HelmertTool library and Pandas, runnable as a live python script.
See: https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2016JB013098 for detalis on the transform.
"""

#%% Imports
import pandas as pd
import numpy as np
from HelmertTool.load import load_ssc
from HelmertTool.transform import calculate_parameters

#%% Load data
#Load defining stations
stations_df = pd.read_fwf("data/core_network_ITRF2014.txt", skiprows=5, header = None)
stations_df.columns = ["Code", "Domes", "Soln", "Tech", "Station_Name", "LONGLAT"]
stations_df = stations_df.drop(columns="Station_Name")

#Concat all files from 2014 and 2008 into two dataframes
doris_df_2014 = load_ssc("data/ITRF2014_DORIS.SSC")
gnss_df_2014 = load_ssc("data/ITRF2014_GNSS.SSC")
gnss_df_2014.Tech = "GPS"
slr_df_2014 = load_ssc("data/ITRF2014_SLR.SSC")
vlbi_df_2014 = load_ssc("data/ITRF2014_VLBI.SSC")
df_2014 = pd.concat([gnss_df_2014, slr_df_2014, doris_df_2014, vlbi_df_2014])

doris_df_2008 = load_ssc("data/ITRF2008_DORIS.SSC")
gnss_df_2008 = load_ssc("data/ITRF2008_GNSS.SSC")
gnss_df_2008.Tech = "GPS"
slr_df_2008 = load_ssc("data/ITRF2008_SLR.SSC")
vlbi_df_2008 = load_ssc("data/ITRF2008_VLBI.SSC")
df_2008 = pd.concat([gnss_df_2008, slr_df_2008, doris_df_2008, vlbi_df_2008])

#%% Transform data
#Select stations from the 2014 frame matching the defining stations file
df_from = stations_df.merge(df_2014, how = "left", on=["Domes", "Soln", "Code"])
df_from[["X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma", "X_v", "Y_v", "Z_v", "X_v_sigma", "Y_v_sigma", "Z_v_sigma"]] = df_from[["X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma", "X_v", "Y_v", "Z_v", "X_v_sigma", "Y_v_sigma", "Z_v_sigma"]].astype(np.float64)
df_from = df_from.set_index(df_from.Domes.rename("index"))
df_from = df_from.sort_index()

#Select stations from the 2014 frame matching the defining stations file, keeping only the latest solution numbers
df_2008 = df_2008.sort_values("Soln", ascending = True)
df_2008 = df_2008[~df_2008.Domes.duplicated()]
df_to = stations_df.merge(df_2008, how = "left", on=["Domes"])
df_to[["X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma", "X_v", "Y_v", "Z_v", "X_v_sigma", "Y_v_sigma", "Z_v_sigma"]] = df_to[["X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma", "X_v", "Y_v", "Z_v", "X_v_sigma", "Y_v_sigma", "Z_v_sigma"]].astype(np.float64)
df_to = df_to.set_index(df_to.Domes.rename("index"))
df_to = df_to.sort_index()

#Propagate the data from 2008 to match the epoch of the 2014 data
df_to.X = df_to.X + 5*df_to.X_v 
df_to.Y = df_to.Y + 5*df_to.Y_v 
df_to.Z = df_to.Z + 5*df_to.Z_v 

# %% Calculate a weighted standard 7 parameter transform, the results should match the values given below
#Parameters : 1.6[mm],	1.9[mm], 2.4[mm], -0.02[ppb],  0.000[mas],  0.000[mas],  0.000[mas]
#Sigmas     : 0.2[mm],  0.1[mm], 0.1[mm],  0.02[ppb],  0.006[mas],  0.006[mas],  0.006[mas]

params, sigmas = calculate_parameters(df_from, df_to, weighted = True, type = "7")
print(params)
print(sigmas)

