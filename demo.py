from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
import tkinter as tk 

Triple = namedtuple("Triple", ["x", "y", "z"])

class HermertParametersView(tk.Frame):
    
    def __init__(self, master, parameters, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.parameters = parameters

        for parameter in self.parameters.parameters:
            parameter.entry = ParameterEntry(self, parameter)

        for i, parameter in enumerate(self.parameters.parameters):
            parameter.entry.grid(row = i, column = 0)

class ParameterEntry(tk.Frame):
    
    def __init__(self, master, parameter, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.external_var = parameter.var
        self.state_var = parameter.custom

        self.external_var.trace("w", self.set_from_external)

        self.state_var.trace("w", self.set_state)

        self.internal_var = tk.StringVar(self, value = "")
        self.unit_text_var = tk.StringVar(self, "")

        self.set_unit(Units.meter)
        self.set_from_external()

        self.edit_check = tk.Checkbutton(self, variable=self.state_var, onvalue=True, offvalue=False)
        self.entry = tk.Entry(self, textvariable=self.internal_var, state = "disabled", width=5)
        self.entry.bind("<Return>", self.set_from_internal)
        self.entry.bind("<Tab>", self.set_from_internal)
        self.entry.bind("<FocusOut>", self.set_from_internal)

        self.unit_label = tk.Label(self, textvariable=self.unit_text_var)
    
        self.edit_check.grid(row=0, column=0)
        self.entry.grid(row=0, column=1)
        self.unit_label.grid(row=0, column=2)

    def set_unit(self, unit):
        """Change unit of the displayed value"""
        self.unit = unit
        self.unit_text_var.set(unit.symbol)
        self.internal_var.set(self.external_var.get() * unit.convertion_factor)

    def set_from_external(self, *args):
        """Set displayed value from external value"""
        self.internal_var.set(self.external_var.get() * self.unit.convertion_factor)

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


class HelmertParameters():
    """Class for keeping order in helmert parameters"""

    Triple = namedtuple("Triple", ["x", "y", "z"])
    Parameter = namedtuple("Parameter", ["var", "custom"])

    def __init__(self):
        self.parameter_list = []

        self.list = [HelmertParameters.Parameter(tk.StringVar(root, value = 0), tk.BooleanVar(root, value = 0)) for i in range(9)]

        self.translation = Triple(*self.list[0:2])
        self.scale = Triple(*self.list[2:5])
        self.rotation = Triple(*self.list[5:])


    def set(self, values):
        """hmm"""
        calculated_vars = [par.var for par in self.list if not par.custom.get()]
        assert len(values) == len(calculated_vars), "Cannot match parameters"

        for var, val in zip(calculated_vars, values):
            var.set(val)

    def lock_parameters(self, design_matrix, observation_matrix):
        save = []
        
        for i, par in self.list:
            if par.custom.get():
                observation_matrix = observation_matrix - design_matrix[:, i] * par.var.get()
            else:
                save.append(i)

        design_matrix = design_matrix[:, save]

        return design_matrix, observation_matrix

    def vector_form(self):
        c = 
        s = 
        r = 



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
    micro_arcsecond = Unit("m\'", 206264.806 * 10**3)
    timesecond = Unit("µ", 13750.9871*10**6)


root = tk.Tk()
parameters = HelmertParameters()
HermertParametersView(root, parameters).grid(row=0,column=0)
root.mainloop()