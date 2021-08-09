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
    
    column_names = ["Station_Name", "X", "Y", "Z", "X_sigma", "Y_sigma", "Z_sigma"]
    column_specs = [(10, 26), (37,50), (50, 64), (64,77), (79,85), (86,92), (93,99)]
    
    df = pd.read_fwf(fpath, skiprows=7, header = None)
    df = df.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
    df.columns = ["Domes", "Station_Name", "Tech", "Code", "X", "Y", "Z", "X_sigma", "Y_sigma", "Z_sigma", "Soln"]
    if df.Code.dtype == float:
        df.Code = df.Code.astype(str).str.zfill(4)
        
    df.Soln = df.Soln.fillna(1)
    
    df = df.dropna()    
    df = df.reset_index(drop=True)
    df[["X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma"]] = df[["X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma"]].astype(np.float64)

    df = calculate_long_lat(df)
    df = df.set_index(df.Station_Name)
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