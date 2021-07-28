import tkinter as tk 
import tkinter.ttk as ttk 

from HelmertTool.interface.ParameterEntry import ParameterEntry
import HelmertTool.logic.units as units 

class ParameterView(tk.Frame):
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
            parameter.entry.set_unit(units.meter)
            parameter.entry.grid(row = i, column = 0)

        ttk.Label(self, text = "Scale").grid(row=0, column=1)
        for i, parameter in enumerate(self.parameters.scale, 1):
            parameter.entry.set_unit(units.nano_meter)
            parameter.entry.grid(row = i, column = 1)

        ttk.Label(self, text = "Rotation").grid(row=0, column=2)
        for i, parameter in enumerate(self.parameters.rotation, 1):
            parameter.entry.set_unit(units.nano_radian)
            parameter.entry.grid(row = i, column = 2)

        ttk.Checkbutton(self, variable=self.scale_unit_var, onvalue="mm", offvalue="cm").grid(row=4, column=1)
        ttk.Checkbutton(self, variable=self.rotation_unit_var, onvalue="si", offvalue="classic").grid(row=4, column=2)


    def calculate(self, *args):
        pass
        # df_from = load_sta("C:/Users/Adrian/Documents/NVI/CrfPlot/data/2020d.sta")
        # df_to = load_sta("C:/Users/Adrian/Documents/NVI/CrfPlot/data/2020d_off_0_0_10p_rate_0_0_0.sta")

        # type = "9"
        # design_matrix = get_design_matrix(df_from, type)
        # observation_matrix = get_obeservation_matrix(df_from, df_to)
        # design_matrix, observation_matrix = self.parameters.lock_parameters(design_matrix, observation_matrix)
        
        # observation_var_matrix = get_var_matrix(df_from, df_to)
        # parameters = regression.ordinary_least_squares(design_matrix, observation_matrix)
        # #parameter_uncertainties = rename_parameters(parameter_uncertainties, type)

        # self.parameters.set(parameters)

    def scale_unit_change(self, *args):
        if self.scale_unit_var.get() == "mm":
            for par in self.parameters.scale:
                par.entry.set_unit(units.milli_meter)
        elif self.scale_unit_var.get() == "cm":
            for par in self.parameters.scale:
                par.entry.set_unit(units.centi_meter)

    def rotation_unit_change(self, *args):
        if self.rotation_unit_var.get() == "si":
            self.parameters.rotation.x.entry.set_unit(units.nano_radian)
            self.parameters.rotation.y.entry.set_unit(units.nano_radian)
            self.parameters.rotation.z.entry.set_unit(units.nano_radian)

        elif self.rotation_unit_var.get() == "classic":
            self.parameters.rotation.x.entry.set_unit(units.micro_arcsecond)
            self.parameters.rotation.y.entry.set_unit(units.micro_arcsecond)
            self.parameters.rotation.z.entry.set_unit(units.timesecond)
