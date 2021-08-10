import pandas as pd 
import numpy as np

def load_sta(fpath: str, epoch: float = 0):
    """Load a .sta TRF file to a pandas dataframe"""

    column_names = ["Value_Type", "Station_Name", "Date", "X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma", ]
    column_specs = [(0,7), (10, 19), (19,25), (31,45), (52, 59), (65,79), (87,93), (99,113), (120,127)]
    
    df = pd.read_fwf(fpath, colspecs=column_specs, header=None, names = column_names)

    df = df[df["Value_Type"]=="STA_GCX"]
    df["Station_Name"] = df["Station_Name"].str.replace("_", "")
    df["Date"] = pd.to_datetime(df["Date"], format = "%y%m%d")
    df["Date"] = timestamp_to_year(df["Date"])
    df = df.reset_index(drop=True)
    df[["X", "Y", "Z"]] = df[["X", "Y", "Z"]].astype(np.float64)*10**-3
    df[["X_sigma", "Y_sigma", "Z_sigma"]] = df[["X_sigma", "Y_sigma", "Z_sigma"]].astype(np.float64)*10**-3

    df = df.drop(columns="Value_Type")
    
    df = calculate_long_lat(df)
    return df


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
    df = calculate_long_lat(df)

    return df

def calculate_long_lat(df: pd.DataFrame):
    """Add columns with LONG/LAT cooridnates to df derived from XYZ coordinates from df"""

    df["LONG"] = np.degrees(np.arcsin(df.Z/(6371*10**3)))
    df["LAT"] = np.degrees(np.arctan2(df.Y, df.X))

    return df

def timestamp_to_year(timestamp):
    jd = pd.DatetimeIndex(timestamp).to_julian_date()
    jd2000 = pd.Timestamp(year=2000, month=1, day=1).to_julian_date()
    year = (jd - jd2000)/365.25 + 2000

    return year