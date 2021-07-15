import numpy as np

def ordinary_least_squares(design_matrix: np.array, observation_matrix: np.array, parameter_names: list = None):
    """Ordinary least squares fit"""
    parameters = np.linalg.inv(design_matrix.T @ design_matrix) @ design_matrix.T @ observation_matrix
    parameters = parameters_to_dict(parameters, parameter_names)

    return parameters

def weighted_least_squares(design_matrix: np.array, observation_matrix: np.array, observation_var_matrix: np.array, parameter_names: list = None):
    """Weighted least squares fit under the assumption of uncorrelated measurement errors"""
    weight_matrix = np.linalg.inv(observation_var_matrix)

    parameter_uncertainties = np.inv(design_matrix.T @ weight_matrix @ design_matrix)
    parameters = parameter_uncertainties @ design_matrix.T @ weight_matrix @ observation_matrix

    return parameters_to_dict(parameters, parameter_names), parameters_to_dict(parameter_uncertainties, parameter_names)

def parameters_to_dict(self, parameters, parameter_names: list = None):
    """Puts an array of parameters into a readable dict form"""
    if parameter_names:
        assert len(parameters) == len(parameter_names), "Parameters and parameter names must be of equal lenght"
        parameter_dict = {name : par for par, name in zip(parameters, parameter_names)}
    else:
        parameter_dict =  {f"C{i}" : par for par, i in enumerate(parameters)}

    return parameter_dict

def r_squared(x: np.array, y: np.array, prediction_model: callable):
    """R squared value of a fit of x to y with given parameters"""
    residuals = y - prediction_model(x) 
    y_mean = np.mean(y)
    ss_tot = sum(y - y_mean)
    ss_res = sum(residuals**2)
    r_squared = 1-ss_res/ss_tot

    return r_squared

def weighted_rms(x: np.array, y:np.array, y_var:np.array, prediction_model):
    """Weighted root mean squared of residuals of fit of x to y with given parameters and uncertainties"""
    residuals = y - prediction_model(x)
    weighted_sum = sum(residuals**2/y_var**2)
    weighted_normalisation = sum(1/y_var**2)
    weighted_rms = np.sqrt(weighted_sum/weighted_normalisation)

    return weighted_rms
