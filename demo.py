from collections import namedtuple
import tkinter as tk
import tkinter.ttk as ttk 

from logic import * 


Triple = namedtuple("Triple", ["x", "y", "z"])

class HermertParametersView(tk.Frame):
    def __init__(self, master, parameters, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.parameters = parameters
        self.scale_unit_var = tk.StringVar(self, value = "mm")
        self.scale_unit_var.trace("w", self.scale_unit_change)
        self.rotation_unit_var = tk.StringVar(self, value = "si")
        self.rotation_unit_var.trace("w", self.rotation_unit_change)
        
        for parameter in self.parameters.list:
            parameter.entry = ParameterEntry(self, parameter)

        ttk.Label(self, text = "Translation").grid(row=0, column=0)
        for i, parameter in enumerate(self.parameters.translation, 1):
            parameter.entry.set_unit(Units.meter)
            parameter.entry.grid(row = i, column = 0)

        ttk.Label(self, text = "Scale").grid(row=0, column=1)
        for i, parameter in enumerate(self.parameters.scale, 1):
            parameter.entry.set_unit(Units.nano_meter)
            parameter.entry.grid(row = i, column = 1)

        ttk.Label(self, text = "Rotation").grid(row=0, column=2)
        for i, parameter in enumerate(self.parameters.rotation, 1):
            parameter.entry.set_unit(Units.nano_radian)
            parameter.entry.grid(row = i, column = 2)

        ttk.Checkbutton(self, variable=self.scale_unit_var, onvalue="mm", offvalue="cm").grid(row=4, column=1)
        ttk.Checkbutton(self, variable=self.rotation_unit_var, onvalue="si", offvalue="classic").grid(row=4, column=2)

        ttk.Button(self, text = "Calculate", command= self.calculate).grid(row=5, column = 1)

    def calculate(self, *args):
        df_from = load_sta("C:/Users/Adrian/Documents/NVI/CrfPlot/data/2020d.sta")
        df_to = load_sta("C:/Users/Adrian/Documents/NVI/CrfPlot/data/2020d_off_0_0_10p_rate_0_0_0.sta")

        type = "9"
        design_matrix = get_design_matrix(df_from, type)
        observation_matrix = get_obeservation_matrix(df_from, df_to)
        design_matrix, observation_matrix = self.parameters.lock_parameters(design_matrix, observation_matrix)
        
        observation_var_matrix = get_var_matrix(df_from, df_to)
        parameters = regression.ordinary_least_squares(design_matrix, observation_matrix)
        #parameter_uncertainties = rename_parameters(parameter_uncertainties, type)

        self.parameters.set(parameters)

    def scale_unit_change(self, *args):
        if self.scale_unit_var.get() == "mm":
            for par in self.parameters.scale:
                par.entry.set_unit(Units.milli_meter)
        elif self.scale_unit_var.get() == "cm":
            for par in self.parameters.scale:
                par.entry.set_unit(Units.centi_meter)

    def rotation_unit_change(self, *args):
        if self.rotation_unit_var.get() == "si":
            self.parameters.rotation.x.entry.set_unit(Units.nano_radian)
            self.parameters.rotation.y.entry.set_unit(Units.nano_radian)
            self.parameters.rotation.z.entry.set_unit(Units.nano_radian)

        elif self.rotation_unit_var.get() == "classic":
            self.parameters.rotation.x.entry.set_unit(Units.micro_arcsecond)
            self.parameters.rotation.y.entry.set_unit(Units.micro_arcsecond)
            self.parameters.rotation.z.entry.set_unit(Units.timesecond)

class ParameterEntry(tk.Frame):
    
    def __init__(self, master, parameter, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.external_var = parameter.value
        self.state_var = parameter.is_custom
        self.sigma_var = parameter.sigma

        self.external_var.trace("w", self.set_from_external)
        self.state_var.trace("w", self.set_state)

        self.internal_var = tk.StringVar(self, value = "")
        self.unit_text_var = tk.StringVar(self, "")

        self.set_unit(Units.meter)
        self.set_from_external()

        self.edit_check = ttk.Checkbutton(self, variable=self.state_var, onvalue=True, offvalue=False)
        self.entry = ttk.Entry(self, textvariable=self.internal_var, state = "disabled", width=10)
        self.plus_minus_sign = ttk.Label(self, text = "±")
        self.sigma_entry = ttk.Entry(self, textvariable=self.sigma_var, state = "disabled", width=10)

        self.entry.bind("<Return>", self.set_from_internal)
        self.entry.bind("<Tab>", self.set_from_internal)
        self.entry.bind("<FocusOut>", self.set_from_internal)

        self.unit_label = ttk.Label(self, textvariable=self.unit_text_var, width=5)
    
        self.edit_check.grid(row=0, column=0)
        self.entry.grid(row=0, column=1)
        self.plus_minus_sign.grid(row=0, column=2)
        self.sigma_entry.grid(row=0, column=3)
        self.unit_label.grid(row=0, column=4)

    def set_unit(self, unit):
        """Change unit of the displayed value"""
        self.unit = unit
        self.unit_text_var.set(unit.symbol)
        self.internal_var.set(self.external_var.get() * unit.convertion_factor)

    def set_from_external(self, *args):
        """Set displayed value from external value"""
        value = self.external_var.get()
        if value == np.nan:
            self.internal_var.set("N/A")
        else:
            value = value * self.unit.convertion_factor
            self.internal_var.set(round(value, 5))

        sigma = self.sigma_var.get()
        if sigma == np.nan:
            self.sigma_var.set("N/A")
        else:
            sigma = sigma * self.unit.convertion_factor
            self.sigma_var.set(round(sigma, 5))


    def set_from_internal(self, *args):
        """Set external value from entered internal value, reset on failure"""
        new_value = self.internal_var.get()
        
        try: 
            new_value = float(new_value)/self.unit.convertion_factor
            assert self.validate(new_value)

            self.external_var.set(new_value)            
        except: 
            self.set_from_external()

    def validate(self, value):
        """Validation, (currently not in use)"""
        return True

    def set_state(self, *args):
        """Enable/ disable entry field based on the state variable"""
        state = "normal" if self.state_var.get() else "disabled"
        self.entry.config(state=state)
        self.sigma_entry.config(state=state)


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
    """Collection of units and the factor to convert to it from standard SI-units (meter, radians)"""
    Unit = namedtuple("Unit", ["symbol", "convertion_factor"])
    
    #Length units
    nano_meter = Unit("nm", 10**9)
    micro_meter = Unit("µm", 10**6)
    milli_meter = Unit("mm", 10**3)
    centi_meter = Unit("cm", 10**2)
    meter = Unit("m", 1)

    #Angles
    nano_radian = Unit("nrad", 10**9)
    micro_arcsecond = Unit("mas", 206264.806 * 10**3)
    timesecond = Unit("µts", 13750.9871*10**6)


root = tk.Tk()
parameters = HelmertParameters()
HermertParametersView(root, parameters).grid(row=0,column=0)
root.mainloop()