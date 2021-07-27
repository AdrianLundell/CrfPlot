from collections import namedtuple
import tkinter as tk
import tkinter.ttk as ttk 

from logic import * 





class HelmertParameters():
    """Class for keeping order in helmert parameters"""

    no_value = np.nan
    Triple = namedtuple("Triple", ["x", "y", "z"])
   
    class Parameter:
        def __init__(self):
            self.value = tk.DoubleVar(root, value = 0)
            self.sigma = tk.DoubleVar(root, value = np.nan)
            self.is_custom = tk.BooleanVar(root, value = False)

    def __init__(self):
        self.list = [HelmertParameters.Parameter() for i in range(9)]
        self.translation = Triple(*self.list[0:3])
        self.scale = Triple(*self.list[3:6])
        self.rotation = Triple(*self.list[6:])

    def set(self, values, sigmas = None):
        """"""
        non_custom_parameters = [par for par in self.list if not par.is_custom.get()]
        assert len(values) == len(non_custom_parameters), "Cannot match parameters"

        if sigmas: 
            for par, value, sigma in zip(non_custom_parameters, values, sigmas):
                par.value.set(value)
                par.sigma.set(sigma)
        else:
            for par, value in zip(non_custom_parameters, values):
                par.value.set(value)
                par.sigma.set(self.no_value)

    def lock_parameters(self, design_matrix, observation_matrix):
        """"""
        save = []
        
        for i, par in enumerate(self.list):
            if par.is_custom.get():
                observation_matrix = observation_matrix - design_matrix[:, i] * par.value.get()
            else:
                save.append(i)

        design_matrix = design_matrix[:, save]

        return design_matrix, observation_matrix

    def vector_form(self):
        pass



class Units():



root = tk.Tk()
parameters = HelmertParameters()
HermertParametersView(root, parameters).grid(row=0,column=0)
root.mainloop()