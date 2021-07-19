import numpy as np

def ordinary_least_squares(design_matrix, observation_matrix, parameter_names = None):
    """Ordinary least squares fit"""
    parameters = np.linalg.inv(design_matrix.T @ design_matrix) @ design_matrix.T @ observation_matrix
    parameters = parameters_to_dict(parameters, parameter_names)

    return parameters

def weighted_least_squares(design_matrix, observation_matrix, observation_var_matrix, parameter_names = None):
    """Weighted least squares fit under the assumption of uncorrelated measurement errors"""
    weight_matrix = np.linalg.inv(observation_var_matrix)

    parameter_uncertainties = np.linalg.inv(design_matrix.T @ weight_matrix @ design_matrix)
    parameters = parameter_uncertainties @ design_matrix.T @ weight_matrix @ observation_matrix
    parameter_uncertainties = np.sqrt(np.diag(parameter_uncertainties))

    return parameters_to_dict(parameters, parameter_names), parameters_to_dict(parameter_uncertainties, parameter_names)

def parameters_to_dict(parameters, parameter_names = None):
    """Puts an array of parameters into a readable dict form"""
    if parameter_names:
        assert len(parameters) == len(parameter_names), "Parameters and parameter names must be of equal lenght"
        parameter_dict = {name : par for par, name in zip(parameters, parameter_names)}
    else:
        parameter_dict =  {f"C{i}" : par for i, par in enumerate(list(parameters))}

    return parameter_dict

def r_squared(x, y, prediction_model):
    """R squared value of a fit of x to y with given parameters"""
    residuals = y - prediction_model(x) 
    y_mean = np.mean(y)
    ss_tot = sum(y - y_mean)
    ss_res = sum(residuals**2)
    r_squared = 1-ss_res/ss_tot

    return r_squared

def weighted_rms(x, y, y_var, prediction_model):
    """Weighted root mean squared of residuals of fit of x to y with given parameters and uncertainties"""
    residuals = y - prediction_model(x)
    weighted_sum = sum(residuals**2/y_var**2)
    weighted_normalisation = sum(1/y_var**2)
    weighted_rms = np.sqrt(weighted_sum/weighted_normalisation)

    return weighted_rms
