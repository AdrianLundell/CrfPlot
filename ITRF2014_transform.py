#%%
import pandas as pd
import numpy as np


def load_ssc(fpath: str):
    """Load a .ssc TRF file to a pandas dataframe"""
    
    column_names = ["Domes", "Station_Name", "Tech", "Code", "X", "Y", "Z", "X_sigma", "Y_sigma", "Z_sigma", "Soln"]
    column_names_rate = ["Domes", "Station_Name", "Code", "X_v", "Y_v", "Z_v", "X_v_sigma", "Y_v_sigma", "Z_v_sigma", "Soln"]
    if "2008" in fpath:
        column_specs = [(0,9),(9,25),(25,31),(31,36),(36,49),(49,62),(62,75),(75,81),(81,87),(87,93),(95,96)]
        column_specs_rate = [(0, 9), (9, 25),(31,36),(42, 49),(55, 62),(68, 75),(75, 81),(81, 87),(87,93), (95,96)]
    elif "2014" in fpath:
        column_specs = [(0, 9),(9, 25),(25, 31),(31, 36),(36, 50),(50, 64),(64, 78),(78, 85),(85, 92),(92, 99),(100, 102)]
        column_specs_rate = [(0, 9),(9, 25),(31,36),(43, 50),(56, 64),(70, 78),(78, 85),(87,93),(93,99), (100,102)]

    df = pd.read_fwf(fpath, skiprows=7, header=None, colspecs = column_specs, names = column_names)
    df.Soln = df.Soln.fillna(1)
    df = df.dropna()    

    if df.Code.dtype == np.float64:
        df.Code = df.Code.astype(int).astype(str)        
    
    df = df.reset_index(drop=True)
    df = df.set_index(df.Domes.rename("index"))

    df_rate = pd.read_fwf(fpath, skiprows=7, header = None, colspecs=column_specs_rate, names = column_names_rate)
    df_rate.Soln = df_rate.Soln.fillna(method = "ffill", limit = 1)
    df_rate.Soln = df_rate.Soln.fillna(1)
    df_rate.Code = df_rate.Code.fillna(method = "ffill")
    
    df_rate = df_rate[df_rate.Station_Name.isna()]
    df_rate = df_rate.drop(columns = "Station_Name")
    df_rate = df_rate.reset_index(drop=True)
    
    if df_rate.Code.dtype == np.float64:
        df_rate.Code = df_rate.Code.astype(int).astype(str)        
    
    df_rate = df_rate.set_index(df_rate.Domes.rename("index"))
    
    df = df.merge(df_rate, how="inner", on=["Domes", "Soln", "Code"])

    return df


stations_df = pd.read_fwf("C:/Users/Adrian/Documents/NVI/HelmertTool/data/core_network_ITRF2014.txt", skiprows=5, header = None)
stations_df.columns = ["Code", "Domes", "Soln", "Tech", "Station_Name", "LONGLAT"]
stations_df = stations_df.drop(columns="Station_Name")

doris_df_2014 = load_ssc("C:/Users/Adrian/Documents/NVI/HelmertTool/data/ITRF2014_DORIS.SSC")
gnss_df_2014 = load_ssc("C:/Users/Adrian/Documents/NVI/HelmertTool/data/ITRF2014_GNSS.SSC")
gnss_df_2014.Tech = "GPS"
slr_df_2014 = load_ssc("C:/Users/Adrian/Documents/NVI/HelmertTool/data/ITRF2014_SLR.SSC")
vlbi_df_2014 = load_ssc("C:/Users/Adrian/Documents/NVI/HelmertTool/data/ITRF2014_VLBI.SSC")
df_2014 = pd.concat([gnss_df_2014, slr_df_2014, doris_df_2014, vlbi_df_2014])

doris_df_2008 = load_ssc("C:/Users/Adrian/Documents/NVI/HelmertTool/data/ITRF2008_DORIS.SSC")
gnss_df_2008 = load_ssc("C:/Users/Adrian/Documents/NVI/HelmertTool/data/ITRF2008_GNSS.SSC")
gnss_df_2008.Tech = "GPS"
slr_df_2008 = load_ssc("C:/Users/Adrian/Documents/NVI/HelmertTool/data/ITRF2008_SLR.SSC")
vlbi_df_2008 = load_ssc("C:/Users/Adrian/Documents/NVI/HelmertTool/data/ITRF2008_VLBI.SSC")
df_2008 = pd.concat([gnss_df_2008, slr_df_2008, doris_df_2008, vlbi_df_2008])

df_from = stations_df.merge(df_2014, how = "left", on=["Domes", "Soln", "Code"])
df_from[["X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma", "X_v", "Y_v", "Z_v", "X_v_sigma", "Y_v_sigma", "Z_v_sigma"]] = df_from[["X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma", "X_v", "Y_v", "Z_v", "X_v_sigma", "Y_v_sigma", "Z_v_sigma"]].astype(np.float64)
df_from = df_from.set_index(df_from.Domes.rename("index"))
df_from = df_from.sort_index()

df_2008 = df_2008.sort_values("Soln", ascending = True)
df_2008 = df_2008[~df_2008.Domes.duplicated()]
df_to = stations_df.merge(df_2008, how = "left", on=["Domes"])
df_to[["X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma", "X_v", "Y_v", "Z_v", "X_v_sigma", "Y_v_sigma", "Z_v_sigma"]] = df_to[["X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma", "X_v", "Y_v", "Z_v", "X_v_sigma", "Y_v_sigma", "Z_v_sigma"]].astype(np.float64)
df_to = df_to.set_index(df_to.Domes.rename("index"))
df_to.X = df_to.X + 5*df_to.X_v
df_to.Y = df_to.Y + 5*df_to.Y_v 
df_to.Z = df_to.Z + 5*df_to.Z_v 
df_to = df_to.sort_index()


# %% Calculate 
from HelmertTool.transform import *

parameters = {"translation_x" : None,
              "translation_y" : None, 
              "translation_z" : None,
              "scale_x" : None, 
              "scale_y" : None, 
              "scale_z" : None,
              "rotation_x" : None, 
              "rotation_y" : None,
              "rotation_z" : None}

params, sigmas = calculate_parameters(df_from, df_to, weighted = False, type = "7", custom_dict = parameters)

print(
params["translation_x"]*1000,
params["translation_y"]*1000,
params["translation_z"]*1000,
params["scale_x"]*10**9,
params["rotation_x"] * 10**3 * 60*60*180/np.pi,
params["rotation_y"] * 10**3 * 60*60*180/np.pi,
params["rotation_z"] * 10**3 * 60*60*180/np.pi
)

true_parameters = [1.6,	1.9, 2.4, -0.02, 0.000, 0.000, 0.000]
true_sigmas = [0.2, 0.1, 0.1, 0.02, 0.006, 0.006, 0.006]