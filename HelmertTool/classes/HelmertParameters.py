from collections import namedtuple
import numpy as np
import tkinter as tk 

class HelmertParameters():
    """Class for keeping order in helmert parameters. Currently dependent on keeping the parameters within a sorted list which might be unstable"""

    no_value = np.nan
   
    class Parameter:
        """Tkinter variable based dataclass for a parameter with an uncertainty sigma. Is_custom indicates wheter the parameter is calculated or supplied by the user"""
        def __init__(self):
            self.value = tk.DoubleVar(value = 0)
            self.sigma = tk.DoubleVar(value = np.nan)
            self.is_custom = tk.BooleanVar(value = False)

    def __init__(self):
        self.list = [self.Parameter() for i in range(9)]
        
        Triple = namedtuple("Triple", ["x", "y", "z"])
        self.translation = Triple(*self.list[0:3])
        self.scale = Triple(*self.list[3:6])
        self.rotation = Triple(*self.list[6:])

        self.type = None
        
    def get(self):
        if self.type == "7":
            return [*self.list[:3], *self.list[5:]]
        if self.type == "8":
            return [*self.list[:3], *self.list[4:]]
        else:
            return self.list

    def set(self, values, sigmas = None):
        """Updates the non custom parameters as a list of values and (optionally) sigmas, matching by order"""

        non_custom_parameters = [par for par in self.list if not par.is_custom.get()]
        assert len(values) == len(non_custom_parameters), "Cannot match given parameters to "

        if not sigmas is None: 
            for par, value, sigma in zip(non_custom_parameters, values, sigmas):
                par.value.set(value)
                par.sigma.set(sigma)
        else:
            for par, value in zip(non_custom_parameters, values):
                par.value.set(value)
                par.sigma.set(self.no_value)

    def custom_parameters(self):
        """Returns a boolean vector indicating which parameters are custom"""
        return [par.is_custom.get() for par in self.list]

    def as_string(self):
        """Returns the parameters as a formated string"""
        pass
#     def repr(self, unit, scale):

#         params = scale_parameters(self.parameters, unit, scale)

#         result =  f"""
# HELMERT TRANSFORMATION PARAMETERS
#            X                    Y                    Z 
# C       = {params["C"].T}
# S       = {params["S"].T}
# ω       = {params["OMEGA"].T}

# """
#         if self.sigmas:
#             sigmas = scale_parameters(self.sigmas, unit, scale)
#             result += f"""
# HELMERT PARAMETER UNCERTAINTIES
# C_sigma = {sigmas["C"].T}
# S_sigma = {sigmas["S"].T}
# ω_sigma = {sigmas["OMEGA"].T}

# """

#         return result

    def as_numpy(self):
        """Returns the parameters as numpy vectors suitable for performing a transformation"""
        return {"C" : np.array([par.value.get() for par in self.translation]).reshape((3,1)),
                "S" : np.array([par.value.get() for par in self.scale]).reshape(3,1),
                "OMEGA" : np.array([par.value.get() for par in self.rotation]).reshape(3,1)}