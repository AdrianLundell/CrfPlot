import pandas as pd
import geopandas as gpd
import numpy as np 
import matplotlib.pyplot as plt
import regression

#CLASSES----------------------------------------------------------------------------------------------------------------
class HelmertTransform():
    """Wraps all analysis and visulisation of a helmert transform from df_from to df_to of the given type in a single object"""

    weighted : bool                 #True for weighted least squares regression 
    type : str                      #Type of helmert transform: 7, 8, or 9 parameters ()
    parameters : dict               #Calculated helmert parameters
    df_to : pd.DataFrame            #Values to transform from
    df_from : pd.DataFrame          #Values to transfrom to
    df_transformed : pd.DataFrame   #Transformed values
    epoch : float                   #Epoch for value in modified julian date

    def __init__(self, df_from: pd.DataFrame, df_to: pd.DataFrame, weighted: bool = False, type: str = "7", epoch = 0):
        self.weighted = weighted 
        self.type = type
        self.epoch = epoch
    
        self.df_to = df_to
        self.df_from = df_from
        self.df_from = calculate_residuals(df_from, df_to) 
        self.df_from = decompose_residuals(df_from)

        self.parameters, self.sigmas = calculate_parameters(df_from, df_to, weighted, type)
        self.df_transformed = helmert_transform(df_from, self.parameters)
        
        self.df_transformed = calculate_residuals(self.df_transformed, df_to) 
        self.df_transformed = decompose_residuals(self.df_transformed)

    def repr(self, unit, scale):

        params = scale_parameters(self.parameters, unit, scale)

        result =  f"""
HELMERT TRANSFORMATION PARAMETERS
           X                    Y                    Z 
C       = {params["C"].T}
S       = {params["S"].T}
ω       = {params["OMEGA"].T}

"""
        if self.sigmas:
            sigmas = scale_parameters(self.sigmas, unit, scale)
            result += f"""
HELMERT PARAMETER UNCERTAINTIES
C_sigma = {sigmas["C"].T}
S_sigma = {sigmas["S"].T}
ω_sigma = {sigmas["OMEGA"].T}

"""

        return result


    def plot_sites(self, ax: plt.Axes):
        plot_sites(self.df_from, ax)
        plot_sites(self.df_to, ax)
        plot_sites(self.df_transformed, ax)

    def plot_residuals(self, ax1: plt.Axes, ax2: plt.Axes, plot_transformed):
        plot_residuals(self.df_to, self.df_from, self.df_transformed, ax1, ax2, plot_transformed)

    def plot_residuals_hist(self, ax1, ax2):
        plot_residuals_hist(self.df_from, self.df_transformed, ax1, ax2)

#HELMERT TRANSFORMATION FUNCTIONS--------------------------------------------------------------------------------------------
def calculate_parameters(df_from: pd.DataFrame, df_to: pd.DataFrame, weighted: bool, type: str):
    """Calculates Helmert parameters with a single scale factor using least squares, weighted or ordinary"""
    
    design_matrix = get_design_matrix(df_from, type)
    observation_matrix = get_obeservation_matrix(df_from, df_to)

    if weighted:
        observation_var_matrix = get_var_matrix(df_from, df_to)
        parameters, parameter_uncertainties = regression.weighted_least_squares(design_matrix, observation_matrix, observation_var_matrix)
        parameter_uncertainties = rename_parameters(parameter_uncertainties, type)
    else:
        parameters, parameter_uncertainties = regression.ordinary_least_squares(design_matrix, observation_matrix), None

    parameters = rename_parameters(parameters, type)

    return parameters, parameter_uncertainties

def get_obeservation_matrix(df_from: pd.DataFrame, df_to: pd.DataFrame):
    """Creates an observation matrix for an OLS parameter fitting of a Helmert-transform"""
    observation_matrix = np.hstack((df_to.X-df_from.X, df_to.Y-df_from.Y, df_to.Z-df_from.Z))
    return observation_matrix
    
def get_design_matrix(df: pd.DataFrame, type: str):
    """Creates a design matrix for an OLS parameter fitting of a Helmer transform with seven, eight, or nine parameters"""
    n = len(df.index)
    zero = np.zeros(n)
    one = np.ones(n)

    if type == "7":
        design_matrix_x = np.vstack((one, zero, zero, df.X, zero, df.Z, -df.Y))
        design_matrix_y = np.vstack((zero, one, zero, df.Y, -df.Z, zero, df.X))
        design_matrix_z = np.vstack((zero, zero, one, df.Z, df.Y, -df.X, zero))
    elif type == "8":
        design_matrix_x = np.vstack((one, zero, zero, df.X, zero, zero, df.Z, -df.Y))
        design_matrix_y = np.vstack((zero, one, zero, df.Y, zero, -df.Z, zero, df.X))
        design_matrix_z = np.vstack((zero, zero, one, zero, df.Z, df.Y, -df.X, zero))
    elif type == "9":
        design_matrix_x = np.vstack((one, zero, zero, df.X, zero, zero, zero, df.Z, -df.Y))
        design_matrix_y = np.vstack((zero, one, zero, zero, df.Y, zero, -df.Z, zero, df.X))
        design_matrix_z = np.vstack((zero, zero, one, zero, zero, df.Z, df.Y, -df.X, zero))
    else:
        raise Exception("Unrecoginzed type")     

    design_matrix = np.hstack((design_matrix_x, design_matrix_y, design_matrix_z)).T
    return design_matrix

def get_var_matrix(df_from: pd.DataFrame, df_to: pd.DataFrame):
    """Creates a weight matrix for a WLS parameter fitting of a Helmer transform""" 
    sigma = df_from.X_sigma**2 + df_from.Y_sigma**2 + df_from.Z_sigma**2 + df_to.X_sigma**2 + df_to.Y_sigma**2 + df_to.Z_sigma**2 
    sigma = sigma.to_numpy()
    weight_matrix = np.diag(np.tile(sigma,3))
    
    return weight_matrix

def scale_parameters(parameters, rotation_unit, translation_unit):
    
    scaled_parameters = {}
    if translation_unit == "cm":
        scaled_parameters["C"] = parameters["C"]*100 #cm
    elif translation_unit == "mm":
        scaled_parameters["C"] = parameters["C"]*1000 #mm
    
    scaled_parameters["S"] = parameters["S"]*10**9 ##ppb

    if rotation_unit == "sec":
        arcseconds_per_radian =  206264.806
        timeseconds_per_radian = 13750.9871
        scaled_parameters["OMEGA"] = np.zeros((3,1))
        scaled_parameters["OMEGA"][0:2] = parameters["OMEGA"][0:2] * arcseconds_per_radian * 10**3 #mas
        scaled_parameters["OMEGA"][2] = parameters["OMEGA"][2] * timeseconds_per_radian * 10**6 #uas
    elif rotation_unit == "si":
        scaled_parameters["OMEGA"] = parameters["OMEGA"] * 10**9
        
    return scaled_parameters
     
def rename_parameters(params, type):
    """"""
    c =  np.array([params["C0"], params["C1"], params["C2"]]).reshape(3,1)
    if type == "7":
           s =  np.array([params["C3"], params["C3"], params["C3"]]).reshape(3,1)
           omega =  np.array([params["C4"], params["C5"], params["C6"]]).reshape(3,1)
    elif type == "8":
           s =  np.array([params["C3"], params["C3"], params["C4"]]).reshape(3,1)
           omega =  np.array([params["C5"], params["C6"], params["C7"]]).reshape(3,1)
    elif type == "9":
           s =  np.array([params["C3"], params["C4"], params["C5"]]).reshape(3,1)
           omega =  np.array([params["C6"], params["C7"], params["C8"]]).reshape(3,1)
    
    return {"C" : c, "S": s, "OMEGA" : omega}

def helmert_transform_full_form(df: pd.DataFrame, parameters: dict):
    """Returns a new dataframe with transformed coordinates"""
    coords = parameters["C"] + (1+parameters["S"]) * parameters["R"] @ np.vstack((df.X, df.Y, df.Z)) 
    transformed_df = pd.DataFrame({"X": coords[0,:], 
                                   "Y" : coords[1,:], 
                                   "Z" : coords[2,:], 
                                   "Station_Name" : df.Station_Name,
                                   "LAT" : df.LAT,
                                   "LONG" : df.LONG})

    return transformed_df

def helmert_transform(df: pd.DataFrame, parameters: dict):
    """Returns a new dataframe with coordinates transformed according tp the helmert infinitecimal form"""
    X = np.vstack((df.X, df.Y, df.Z)) 
    coords = parameters["C"] + parameters["S"] * X + np.cross(parameters["OMEGA"], X, axis=0) + X
    transformed_df = pd.DataFrame({"X": coords[0,:], 
                                   "Y" : coords[1,:], 
                                   "Z" : coords[2,:], 
                                   "Station_Name" : df.Station_Name,
                                   "LAT" : df.LAT,
                                   "LONG" : df.LONG})

    return transformed_df

#RESIDUAL HANDLING FUNCTIONS-------------------------------------------------------------------------------------------------
def calculate_residuals(df_from: pd.DataFrame, df_to: pd.DataFrame):
    """Returns the from dataframe with computed residuals"""
    df_from["dX"] = df_from.X-df_to.X
    df_from["dY"] = df_from.Y-df_to.Y
    df_from["dZ"] = df_from.Z-df_to.Z

    return df_from

def decompose_residuals(df):
    """Returns the dataframe with residuals decomposed into U,E,N coordinates"""
    df["dU"] = np.cos(df.LAT)*np.cos(df.LONG)*df.dX + \
                np.cos(df.LAT)*np.sin(df.LONG)*df.dY + \
                np.sin(df.LAT)*df.dZ
    df["dE"] = np.sin(df.LONG)*df.dX + \
                -np.cos(df.LONG)*df.dY + \
            0
    df["dN"] = np.sin(df.LAT)*np.cos(df.LONG)*df.dX + \
               np.sin(df.LAT)*np.sin(df.LONG)*df.dY + \
               (-np.cos(df.LAT)*np.cos(df.LONG)*np.cos(df.LONG)-np.cos(df.LAT)*np.sin(df.LONG)*np.sin(df.LONG))*df.dZ
    
    return df


#PLOTTING FUNCTIONS-------------------------------------------------------------------------------------------------
worldmap = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

def plot_sites3D(df: pd.DataFrame):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.scatter3D(df.X, df.Y, df.Z)
    plt.show()

def plot_sites(df: pd.DataFrame, ax: plt.Axes):
    """Plots the station sites scattered over a world map to ax"""
    worldmap.plot(color="lightgrey", ax=ax)
    ax.scatter(df.LAT, df.LONG, s=4)
    #for x,y,s in zip(df.LAT, df.LONG, df.Station_Name):
    #    plt.text(x,y,s, fontsize=5)
    ax.grid()
    
def plot_residuals(df_to, df_from, df_transformed, ax1, ax2, plot_transformed):
    """Plots UEN-residuals scattered over a world map to axes"""
    worldmap.plot(color="lightgrey", ax=ax1)
    #ax1.quiver(df_from.LAT, df_from.LONG, df_from.dE, df_from.dN, color="b")
    if plot_transformed:
        q = ax1.quiver(df_transformed.LAT, df_transformed.LONG, df_transformed.dE, df_transformed.dN, color="k", scale=2)
    else:
        q = ax1.quiver(df_from.LAT, df_from.LONG, df_from.dE, df_from.dN, color="k", scale=2)

    ax1.quiverkey(q, 0.9,1.05,2*10**-1, "2e-1 m", color = "red")
    ax1.set_title("NE-residual components")
    ax1.grid()

    worldmap.plot(color="lightgrey", ax=ax2)
    if plot_transformed:
        q = ax2.quiver(df_transformed.LAT, df_transformed.LONG, np.zeros(len(df_from.dU)), df_transformed.dU, scale=2)
    else:
        q = ax2.quiver(df_from.LAT, df_from.LONG, np.zeros(len(df_from.dU)), df_from.dU, scale=2)

    ax2.set_title("UP-residual component")
    ax2.quiverkey(q, 0.9,1.05,2*10**-1, "2e-1 m", color = "red")
    ax2.grid()

def plot_residuals_hist(df_from, df_transformed, ax1, ax2):
    """Plots UEN-residuals plotted over value"""
    ax1.hist([df_from.dU, df_from.dE, df_from.dN], 200, stacked=True)
    ax2.hist([df_transformed.dU, df_transformed.dE, df_transformed.dN], 200, stacked=True)


#DATA LOADING FUNCTIONS-------------------------------------------------------------------------------------------------
def load_sta(fpath: str, epoch: float = 0):
    """Load a .sta TRF file to a pandas dataframe"""

    column_names = ["Value_Type", "Station_Name", "Date", "X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma", ]
    column_specs = [(0,7), (10, 19), (19,25), (31,45), (52, 59), (65,79), (87,93), (99,113), (120,127)]
    
    df = pd.read_fwf(fpath, colspecs=column_specs, names = column_names)

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

#Save to csv.
def load_ssc(fpath: str):
    """Load a .ssc TRF file to a pandas dataframe"""
    
    column_names = ["Station_Name", "X", "Y", "Z", "X_sigma", "Y_sigma", "Z_sigma"]
    column_specs = [(10, 26), (37,51), (51, 65), (65,78), (79,85), (86,92), (93,99)]
    
    df = pd.read_fwf(fpath, colspecs=column_specs, names = column_names, skiprows=7)
    df = df.dropna()    
    df = df.reset_index(drop=True)
    df[["X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma"]] = df[["X", "X_sigma", "Y", "Y_sigma", "Z", "Z_sigma"]].astype(np.float64)

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

# """New ideas
# DONE Units: 
#     Rotation 
#         Either nano-radians OR (micro arc second, mas, micro time seconds (differ by a factor of 24))

#         mas: 360 deg, 60 sec
#         Tme 360 deg 24 h 60min 60 sec 
#         Check box

#     Scale 
#         Parts perbillion

#     Translation 
#         millimeters / centimeters checkbox

#     Vector for scale in plot

# Reading files:
#     read in date, .sta : regex on name -> mjd 
#     .ssc: last column

# Put on: Given VLBI XYZ file: Plot up UEN values with ellipes
#     plot vectors and unc. 
#     put ellips at tip of vector
#     this is by memo 


# """