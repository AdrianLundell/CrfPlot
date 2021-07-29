import tkinter as tk 
import tkinter.ttk as ttk
from numpy import pad 
import pandas as pd 
import numpy as np 

#Must be a better way of structuring this?
from HelmertTool.interface.FileSelecter import FileSelecter
from HelmertTool.interface.ParameterView import ParameterView
from HelmertTool.interface.Plot import Plot
from HelmertTool.interface.SelectStations import SelectStationsWindow 

from HelmertTool.classes.HelmertTransform import HelmertTransform

from HelmertTool.interface.InterfaceState import InterfaceState
import HelmertTool.logic.load as load

class MainWindow(tk.Tk):
    """Main application class for the helmert transfrom interface"""

    file_formats = [".sta", ".ssc"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #Data
        self.df_from = None
        self.df_to = None
        self.stations = None
        self.transform = None 

        self.state = InterfaceState(self)

        #Create Tkinter widgets
        self.data_frame = tk.Frame(self)
        self.from_file_selecter_label = ttk.Label(self.data_frame, text="Transform from:")
        self.from_file_selecter = FileSelecter(self.data_frame, self.state.transform.from_file_path, self.file_formats)
        self.to_file_selecter_label = ttk.Label(self.data_frame, text="Transform to:")
        self.to_file_selecter = FileSelecter(self.data_frame, self.state.transform.to_file_path, self.file_formats)
        self.select_stations_button = ttk.Button(self.data_frame, text="Select stations", state = "disable")
        
        self.line1 = ttk.Separator(self, orient = "horizontal")

        self.config_frame = tk.Frame(self)
        self.weighted_button_label = ttk.Label(self.config_frame, text="Weighted")
        self.weighted_button = ttk.Checkbutton(self.config_frame, variable=self.state.transform.weighted, onvalue=True, offvalue=False)
        self.transform_type_combo_label = ttk.Label(self.config_frame, text="N parameters")
        self.transform_type_combo = ttk.Combobox(self.config_frame, textvariable=self.state.transform.type, values = ['7', '8', '9'], width=3)
        self.calculate_button = ttk.Button(self.config_frame, text = "Calculate parameter")
        self.transform_button = ttk.Button(self.config_frame, text = "Transform")
        self.reset_button = ttk.Button(self.config_frame, text = "Reset parameters")
        
        self.line2 = ttk.Separator(self, orient = "horizontal")

        self.parameter_frame = tk.Frame(self)
        self.parameter_view = ParameterView(self.parameter_frame)

        self.plot_frame = tk.Frame(self)
        self.plot = Plot(self.plot_frame, 2, 1)        

        #Place Tkinter widgets
        self.data_frame.grid(row=0, column=0, padx=10, pady=10)
        self.from_file_selecter_label.grid(row=0, column=0, sticky="w")
        self.from_file_selecter.grid(row=1, column=0, sticky="ew", pady=4)
        self.to_file_selecter_label.grid(row=2, column=0, sticky="w")
        self.to_file_selecter.grid(row=3, column=0, sticky="ew", pady=4)
        self.select_stations_button.grid(row=4, column=0, sticky = "w", pady=10)

        self.line1.grid(row=1, column=0, sticky="ew")

        self.config_frame.grid(row=2, column=0, padx=10, pady=10)
        self.weighted_button_label.grid(row=0, column=0)
        self.weighted_button.grid(row=1, column=0)
        self.transform_type_combo_label.grid(row=0, column=1)
        self.transform_type_combo.grid(row=1, column=1)
        self.calculate_button.grid(row=1, column=2)
        self.transform_button.grid(row=1, column=3)
        self.reset_button.grid(row=1, column=4)

        self.line2.grid(row=3, column=0, sticky="ew")

        self.parameter_frame.grid(row=4, column=0, padx=10, pady=10)
        self.parameter_view.pack()

        self.plot_frame.grid(row=0, column=1, rowspan=5)
        self.plot.pack()
        
        #Bind actions
        self.state.transform.from_file_path.trace_add("write", self.df_from_change)
        self.state.transform.to_file_path.trace_add("write", self.df_to_change)
        self.select_stations_button.config(command = self.select_stations)

        self.state.transform.type.trace_add("write", self.parameter_view.scale_type_change)

        self.calculate_button.config(command = self.calculate_parameters)
        self.transform_button.config(command = self.calculate_transform)
        self.reset_button.config(command = self.reset_parameters)

    def select_stations(self, *args):
        """Open station selection window"""
        self.select_stations_window = SelectStationsWindow(self)

    def df_from_change(self, *args):
        """Called on from_file change. Updates the df_from and calls new_helmert_transform"""
        if not self.state.transform.from_file_path.get()=="":
            self.df_from = load.load_sta(self.state.transform.from_file_path.get())
            self.set_stations()

    def df_to_change(self, *args):
        """Called on to_file change. Updates the df_from and calls new_helmert_transform"""
        if not self.state.transform.to_file_path.get()=="":
            self.df_to = load.load_sta(self.state.transform.to_file_path.get())
            self.set_stations()

    def set_stations(self):
        """Updates the station list as the intersection of stations"""
        if not self.df_from is None and not self.df_to is None:
            station_intersection = self.df_from.Station_Name.isin(self.df_to.Station_Name)
            df_from = self.df_from[station_intersection]
            df_to = self.df_to[station_intersection]

            sigmas = np.sqrt(df_from.X_sigma**2 + df_from.Y_sigma**2 + df_from.Z_sigma**2 + df_to.X_sigma**2 + df_to.Y_sigma**2 + df_to.Z_sigma**2) 
            stations = df_from.Station_Name

            self.stations = pd.DataFrame({"Station_Name" : stations, "Sigma" : sigmas, "Selected" : True})
            self.select_stations_button.config(state = "normal")

    def calculate_parameters(self, *args):
        pass 

    def calculate_transform(self, *args):
        pass 

    def reset_parameters(self, *args):
        """Reset all parameter values to zero"""
        for parameter in self.state.parameters.get_parameter_dict().values():
            parameter.value.set(0)
            if self.state.transform.weighted:
                parameter.sigma.set(0)
            else:
                #TODO: No value?
                parameter.sigma.set(0) 

    # def new_helmert_transform(self, *args):
    #     """Runs a new helmert transform and updates the interface if both df_to and df_from are loaded"""
    #     if not self.to_file_path.get() == "" and not self.from_file_path.get() == "":

    #         df_from = self.df_from[self.stations.Selected]
    #         df_to = self.df_to[self.stations.Selected]

    #         self.transform = HelmertTransform(df_from, df_to, self.parameters, self.weighted.get(), self.transform_type.get())
        
    #         self.update_plot()
    #         self.update_parameter_display()

    # def update_plot(self, *args):
    #     self.plot.clear()
    #     self.transform.plot_residuals(self.plot.axes[0], self.plot.axes[1], self.plot_transformed.get())
    #     self.plot.draw()