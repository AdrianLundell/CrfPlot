import tkinter as tk 
import tkinter.ttk as ttk 
import numpy as np 

import HelmertTool.logic.units as units

class ParameterEntry(tk.Frame):
    
    def __init__(self, master, parameter, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.external_var = parameter.value
        self.state_var = parameter.is_custom
        self.sigma_var = parameter.sigma

        self.state = None 
        self.master_state_var = None

        self.external_var.trace("w", self.set_from_external)
        self.state_var.trace("w", self.set_state)

        self.internal_var = tk.StringVar(self, value = "")
        self.unit_text_var = tk.StringVar(self, "")

        self.set_unit(units.meter)
        self.set_from_external()

        self.edit_check = ttk.Checkbutton(self, variable=self.state_var, onvalue=True, offvalue=False)
        self.entry = ttk.Entry(self, textvariable=self.internal_var, state = "disabled", width=8)
        self.plus_minus_sign = ttk.Label(self, text = "±")
        self.sigma_entry = ttk.Label(self, textvariable=self.sigma_var)

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

        value = self.external_var.get() * unit.convertion_factor
        self.internal_var.set(value)

        sigma = self.sigma_var.get()
        if sigma == np.nan:
            self.sigma_var.set("N/A")
        else:
            sigma = sigma * self.unit.convertion_factor
            self.sigma_var.set(sigma)


    def set_from_external(self, *args):
        """Set displayed value from external value"""
        value = self.external_var.get()
        if value == np.nan:
            self.internal_var.set("N/A")
        else:
            value = value * self.unit.convertion_factor
            self.internal_var.set(value)

        sigma = self.sigma_var.get()
        if sigma == np.nan:
            self.sigma_var.set("N/A")
        else:
            sigma = sigma * self.unit.convertion_factor
            self.sigma_var.set(sigma)

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
        #self.sigma_entry.config(state=state)

    def set_state_external(self, *args):
        """Set own state variable by an external master_variable"""
        value = self.master_state_var.get()
        self.state_var.set(value)

    def set_checkbox_state(self, state, master_variable):
        """The widget may operate in two states, enabled and following its own state, or disabled and following another master_variable"""
        self.master_state_var = master_variable

        if state == "normal" and not state == self.state:
            try:
                master_variable.trace_remove("write", self.trace_id)
            except:
                pass
            self.edit_check.config(state = "normal")
            
        if state == "disabled" and not state == self.state:
            self.trace_id = master_variable.trace_add("write", self.set_state_external)
            self.edit_check.config(state = "disabled")
            self.set_state_external()
  
        self.state = state 
        