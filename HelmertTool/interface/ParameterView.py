import tkinter as tk 
import tkinter.ttk as ttk 

from HelmertTool.interface.ParameterEntry import ParameterEntry
import HelmertTool.logic.units as units 

class ParameterView(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.state = master.master.state 
        self.entry_dict = {name : ParameterEntry(self, par) for name, par in self.state.parameters.get_parameter_dict().items()}

        ttk.Label(self, text = "Translation").grid(row=0, column=0)
        for i, name in enumerate(self.state.parameters.translation_names,1):
            self.entry_dict[name].set_unit(units.meter)
            self.entry_dict[name].grid(row = i, column = 0)

        ttk.Label(self, text = "Scale").grid(row=0, column=1)
        for i, name in enumerate(self.state.parameters.scale_names,1):
            self.entry_dict[name].set_unit(units.nano_meter)
            self.entry_dict[name].grid(row = i, column = 1)

        ttk.Label(self, text = "Rotation").grid(row=0, column=2)
        for i, name in enumerate(self.state.parameters.rotation_names,1):
            self.entry_dict[name].set_unit(units.nano_radian)
            self.entry_dict[name].grid(row = i, column = 2)

        self.scale_type_change()
        ttk.Checkbutton(self, variable=self.state.display.scale_unit, onvalue="mm", offvalue="cm").grid(row=4, column=1)
        ttk.Checkbutton(self, variable=self.state.display.rotation_unit, onvalue="si", offvalue="classic").grid(row=4, column=2)

        self.state.display.scale_unit.trace_add("write", self.scale_unit_change)
        self.state.display.rotation_unit.trace_add("write", self.rotation_unit_change)

    def scale_unit_change(self, *args):
        if self.state.display.scale_unit.get() == "mm":
            self.entry_dict["scale_x"].set_unit(units.milli_meter)
            self.entry_dict["scale_y"].set_unit(units.milli_meter)
            self.entry_dict["scale_z"].set_unit(units.milli_meter)
        elif self.state.display.scale_unit.get() == "cm":
            self.entry_dict["scale_x"].set_unit(units.centi_meter)
            self.entry_dict["scale_y"].set_unit(units.centi_meter)
            self.entry_dict["scale_z"].set_unit(units.centi_meter)

    def rotation_unit_change(self, *args):
        if self.state.display.rotation_unit.get() == "si":
            self.entry_dict["rotation_x"].set_unit(units.nano_radian)
            self.entry_dict["rotation_y"].set_unit(units.nano_radian)
            self.entry_dict["rotation_z"].set_unit(units.nano_radian)

        elif self.state.display.rotation_unit.get() == "classic":
            self.entry_dict["rotation_x"].set_unit(units.micro_arcsecond)
            self.entry_dict["rotation_y"].set_unit(units.micro_arcsecond)
            self.entry_dict["rotation_z"].set_unit(units.timesecond)

    def scale_type_change(self, *args):    
        """"""
        master_variable = self.state.parameters.is_custom["scale_x"]
        master_value = self.state.parameters.values["scale_x"]

        if self.state.transform.type.get() == "7":
            self.entry_dict["scale_y"].set_checkbox_state("disabled", master_variable, master_value)
            self.entry_dict["scale_z"].set_checkbox_state("disabled", master_variable, master_value)
        if self.state.transform.type.get() == "8":
            self.entry_dict["scale_y"].set_checkbox_state("disabled", master_variable, master_value)
            self.entry_dict["scale_z"].set_checkbox_state("normal", master_variable, master_value)
        if self.state.transform.type.get() == "9":
            self.entry_dict["scale_y"].set_checkbox_state("normal", master_variable, master_value)
            self.entry_dict["scale_z"].set_checkbox_state("normal", master_variable, master_value)