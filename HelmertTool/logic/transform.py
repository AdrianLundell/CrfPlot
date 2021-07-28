import pandas as pd
import geopandas as gpd
import numpy as np 
import matplotlib.pyplot as plt

import HelmertTool.logic.regression as regression

def calculate_parameters(df_from: pd.DataFrame, df_to: pd.DataFrame, weighted: bool, type: str, parameters):
    """Calculates Helmert parameters with a single scale factor using least squares, weighted or ordinary"""
    
    design_matrix = get_design_matrix(df_from, type)
    observation_matrix = get_obeservation_matrix(df_from, df_to)

    design_matrix, observation_matrix = fix_parameters(parameters, design_matrix, observation_matrix)

    if weighted:
        observation_var_matrix = get_var_matrix(df_from, df_to)
        calculated_parameters, parameter_uncertainties = regression.weighted_least_squares(design_matrix, observation_matrix, observation_var_matrix)
    else:
        calculated_parameters, parameter_uncertainties = regression.ordinary_least_squares(design_matrix, observation_matrix), None

    if type == "7":
        calculated_parameters = np.insert(calculated_parameters, slice(4,5), [calculated_parameters[3],calculated_parameters[3]])
    if type == "8":
        calculated_parameters = np.insert(calculated_parameters, 4, calculated_parameters[3])

    return calculated_parameters, parameter_uncertainties

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

def fix_parameters(parameters, design_matrix, observation_matrix):
    """"""
    save = []
    
    for i, par in enumerate(parameters.get()):
        if par.is_custom.get():
            observation_matrix = observation_matrix - design_matrix[:, i] * par.value.get()
        else:
            save.append(i)

    design_matrix = design_matrix[:, save]

    return design_matrix, observation_matrix

def helmert_transform(df: pd.DataFrame, parameters):
    """Returns a new dataframe with coordinates transformed according tp the helmert infinitecimal form"""
    X = np.vstack((df.X, df.Y, df.Z)) 
    parameters = parameters.as_numpy()
    
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


