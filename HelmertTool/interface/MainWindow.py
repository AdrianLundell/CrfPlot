import tkinter as tk 
import tkinter.ttk as ttk 
import pandas as pd 

#Must be a better way of structuring this?
from HelmertTool.interface.FileSelecter import FileSelecter
from HelmertTool.interface.ParameterView import ParameterView
from HelmertTool.interface.Plot import Plot
from HelmertTool.interface.SelectStations import SelectStationsWindow 

from HelmertTool.classes.HelmertParameters import HelmertParameters
from HelmertTool.classes.HelmertTransform import HelmertTransform

from HelmertTool.logic.load import *

class MainWindow(tk.Tk):
    """Main application class for the helmert transfrom interface"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.file_formats = [".sta", ".ssc"]
        self.df_from = None
        self.df_to = None

        self.stations = None
        self.parameters = HelmertParameters()

        self.rotation_unit = tk.StringVar(self, value="si")
        self.rotation_unit.trace("w", self.update_parameter_display)
        self.translation_unit = tk.StringVar(self, value = "mm")
        self.translation_unit.trace("w", self.update_parameter_display)

        self.epoch = tk.StringVar(self)
        self.epoch.trace("w", self.new_helmert_transform)
        self.epoch.trace("w", self.df_from_change)
        self.epoch.trace("w", self.df_to_change)

        self.to_file_path = tk.StringVar(self)
        self.to_file_path.trace("w", self.new_helmert_transform)
        self.to_file_path.trace("w", self.df_to_change)
        
        self.from_file_path = tk.StringVar(self)
        self.from_file_path.trace("w", self.new_helmert_transform)
        self.from_file_path.trace("w", self.df_from_change)
        
        self.weighted = tk.BooleanVar(self, False)
        self.weighted.trace("w", self.weighted_change)
        self.transform_type = tk.StringVar(self, '9')
        self.transform_type.trace("w", self.transform_type_change)

        #Plot variables
        self.plot_transformed = tk.BooleanVar(self, value=True)
        self.plot_transformed.trace("w", self.update_plot)

        self.results_frame = tk.Frame(self)
        self.plot = Plot(self.results_frame, 2, 1)
        self.parameter_view = ParameterView(self, self.parameters)

        self.control_frame = tk.Frame(self)
        self.from_file_selecter_label = ttk.Label(self.control_frame, text="Transform from")
        self.from_file_selecter = FileSelecter(self.control_frame, self.from_file_path, self.file_formats)
        self.to_file_selecter_label = ttk.Label(self.control_frame, text="Transform to")
        self.to_file_selecter = FileSelecter(self.control_frame, self.to_file_path, self.file_formats)
        
        self.weighted_button_label = ttk.Label(self.control_frame, text="Weighted")
        self.weighted_button = ttk.Checkbutton(self.control_frame, variable=self.weighted, onvalue=True, offvalue=False)
        self.transform_type_combo_label = ttk.Label(self.control_frame, text="N parameters")
        self.transform_type_combo = ttk.Combobox(self.control_frame, textvariable=self.transform_type, values = ['7', '8', '9'])

        self.epoch_entry_label = ttk.Label(self.control_frame, text="Epoch")
        self.epoch_entry = ttk.Entry(self.control_frame, textvariable=self.epoch)

        self.rotation_check_label = ttk.Label(self.control_frame, text="Rotation unit [classic/si]")
        self.rotation_check = ttk.Checkbutton(self.control_frame, variable=self.rotation_unit, onvalue="sec", offvalue="si")
        self.translation_check_label = ttk.Label(self.control_frame, text="Scale unit [cm/mm]")
        self.translation_check = ttk.Checkbutton(self.control_frame, variable=self.translation_unit, onvalue="cm", offvalue="mm")

        self.plot_transformed_label = tk.Label(self.control_frame, text="Plot transformed/ original")
        self.plot_transformed_check = tk.Checkbutton(self.control_frame, variable=self.plot_transformed, onvalue=True, offvalue=False)
        
        self.select_stations_button = ttk.Button(self.control_frame, text="Select stations", command = self.select_stations, state = "disable")

        self.place_elements()

    def select_stations(self, *args):
        """Open station selection window"""
        self.select_stations_window = SelectStationsWindow(self)

    def place_elements(self):
        """Geometry management"""

        self.plot.grid(row=0, column=0, sticky="NESW")
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.columnconfigure(1, weight=2)
        self.results_frame.rowconfigure(0, weight=1)

        self.select_stations_button.grid(row=1, column=8)

        self.to_file_selecter_label.grid(row=0, column=0, sticky = "EW")
        self.to_file_selecter.grid(row=0, column=1, sticky="EW")
        self.from_file_selecter_label.grid(row=1, column=0, sticky = "EW")
        self.from_file_selecter.grid(row=1, column=1, sticky="EW")
        
        self.weighted_button_label.grid(row=0, column=2)
        self.weighted_button.grid(row=1, column=2, sticky= "EW")
        self.transform_type_combo_label.grid(row=0, column=3)
        self.transform_type_combo.grid(row=1, column=3, sticky= "EW")
        #self.epoch_entry_label.grid(row=0, column=4)
        #self.epoch_entry.grid(row=1, column=4)
        
        #self.rotation_check_label.grid(row=0, column=5)
        #self.rotation_check.grid(row=1, column=5)
        #self.translation_check_label.grid(row=0, column=6)
        #self.translation_check.grid(row=1, column=6)
        
        self.plot_transformed_label.grid(row=0, column=7)
        self.plot_transformed_check.grid(row=1, column=7)


        self.parameter_view.grid(row=1, column=0)
        self.control_frame.grid(row=0, column=0)
        self.results_frame.grid(row=0, rowspan=2, column=1)
        

    def df_from_change(self, *args):
        """Called on from_file change. Updates the df_from and calls new_helmert_transform"""
        if not self.from_file_path.get()=="":
            self.df_from = load_sta(self.from_file_path.get(), self.epoch.get())
            self.set_stations()

    def df_to_change(self, *args):
        """Called on to_file change. Updates the df_from and calls new_helmert_transform"""
        if not self.to_file_path.get()=="":
            self.df_to = load_sta(self.to_file_path.get(), self.epoch.get())
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

    def new_helmert_transform(self, *args):
        """Runs a new helmert transform and updates the interface if both df_to and df_from are loaded"""

        if not self.to_file_path.get() == "" and not self.from_file_path.get() == "":

            df_from = self.df_from[self.stations.Selected]
            df_to = self.df_to[self.stations.Selected]

            self.transform = HelmertTransform(df_from, df_to, self.parameters, self.weighted.get(), self.transform_type.get())
        
            self.update_plot()
            self.update_parameter_display()

    def update_plot(self, *args):
        self.plot.clear()
        self.transform.plot_residuals(self.plot.axes[0], self.plot.axes[1], self.plot_transformed.get())
        self.plot.draw()

    def update_parameter_display(self, *args):
        """Updates the parameter display"""
        pass
       # self.parameters.set(self.transform.parameters)
        #if not self.to_file_path.get() == "" and not self.from_file_path.get() == "":
        #    self.parameter_display.set(self.transform.repr(self.rotation_unit.get(), self.translation_unit.get()))

    def weighted_change(self, *args):
        """Called on weighted change"""
        self.new_helmert_transform()

    def transform_type_change(self, *args):
        """Called on transform_type change"""
        self.new_helmert_transform()