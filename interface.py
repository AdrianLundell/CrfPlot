import tkinter as tk 
import tkinter.filedialog
import tkinter.ttk as ttk 
import os 

from logic import * 

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

class MainWindow(tk.Tk):
    """Main application class for the helmert transfrom interface"""

    file_formats : list 
    df_from : pd.DataFrame
    df_to : pd.DataFrame

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.file_formats = [".sta", ".ssc"]
        self.df_from = None
        self.df_to = None

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
        self.transform_type = tk.StringVar(self, '7')
        self.transform_type.trace("w", self.transform_type_change)

        #Plot variables
        self.plot_transformed = tk.BooleanVar(self, value=True)
        self.plot_transformed.trace("w", self.update_plot)

        self.results_frame = tk.Frame(self)
        self.plot = Plot(self.results_frame, 2, 1)
        self.parameter_display = ParameterDisplay(self.results_frame)

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

        self.place_elements()

    def place_elements(self):
        """Geometry management"""

        self.plot.grid(row=0, column=0, sticky="NESW")
        self.parameter_display.grid(row=0, column=1, sticky="NESW", pady=(0,40))
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.columnconfigure(1, weight=2)
        self.results_frame.rowconfigure(0, weight=1)
        self.results_frame.pack(expand=True, side="top", fill="both")

        self.to_file_selecter_label.grid(row=0, column=0, sticky = "EW")
        self.to_file_selecter.grid(row=0, column=1, sticky="EW")
        self.from_file_selecter_label.grid(row=1, column=0, sticky = "EW")
        self.from_file_selecter.grid(row=1, column=1, sticky="EW")
        
        self.weighted_button_label.grid(row=0, column=2)
        self.weighted_button.grid(row=1, column=2, sticky= "EW")
        self.transform_type_combo_label.grid(row=0, column=3)
        self.transform_type_combo.grid(row=1, column=3, sticky= "EW")
        self.epoch_entry_label.grid(row=0, column=4)
        self.epoch_entry.grid(row=1, column=4)
        
        self.rotation_check_label.grid(row=0, column=5)
        self.rotation_check.grid(row=1, column=5)
        self.translation_check_label.grid(row=0, column=6)
        self.translation_check.grid(row=1, column=6)
        
        self.plot_transformed_label.grid(row=0, column=7)
        self.plot_transformed_check.grid(row=1, column=7)

        self.control_frame.pack(expand=False, side="bottom", pady=40)
        

    def df_from_change(self, *args):
        """Called on from_file change. Updates the df_from and calls new_helmert_transform"""
        if not self.from_file_path.get()=="":
            self.df_from = load_sta(self.from_file_path.get(), self.epoch.get())

    def df_to_change(self, *args):
        """Called on to_file change. Updates the df_from and calls new_helmert_transform"""
        if not self.to_file_path.get()=="":
            self.df_to = load_sta(self.to_file_path.get(), self.epoch.get())

    def new_helmert_transform(self, *args):
        """Runs a new helmert transform and updates the interface if both df_to and df_from are loaded"""

        if not self.to_file_path.get() == "" and not self.from_file_path.get() == "":
            self.transform = HelmertTransform(self.df_from, self.df_to, self.weighted.get(), self.transform_type.get())
        
            self.update_plot()

            self.update_parameter_display()

    def update_plot(self, *args):
        self.plot.clear()
        self.transform.plot_residuals(self.plot.axes[0], self.plot.axes[1], self.plot_transformed.get())
        self.plot.draw()

    def update_parameter_display(self, *args):
        """Updates the parameter display"""
        if not self.to_file_path.get() == "" and not self.from_file_path.get() == "":
            self.parameter_display.set(self.transform.repr(self.rotation_unit.get(), self.translation_unit.get()))

    def weighted_change(self, *args):
        """Called on weighted change"""
        self.new_helmert_transform()

    def transform_type_change(self, *args):
        """Called on transform_type change"""
        self.new_helmert_transform()

class FileSelecter(tk.Frame):
    """Custom tkinter widget for selecting a file through txt entry or a dialog button with validation"""

    file_formats : list
    external_var : tk.StringVar
    internal_var : tk.StringVar
    file_entry : ttk.Entry
    file_button : ttk.Button

    def __init__(self, master, external_var, file_formats, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.file_formats = file_formats
        self.external_var = external_var
        self.internal_var = tk.StringVar(self)

        self.file_entry = ttk.Entry(self, textvariable = self.internal_var)
        self.file_entry.bind("<FocusOut>", self.file_change, add = "+")
        self.file_entry.bind("<Tab>", self.file_change, add = "+")
        self.file_entry.bind("<Return>", self.file_change, add = "+")

        self.file_button = ttk.Button(self, command = self.file_dialog, text="Open")
        self.place_elements()

    def place_elements(self):
        """Geometry management"""
        self.file_entry.grid(row=0, column=0, sticky="EW")
        self.file_button.grid(row=0, column=1, sticky="W")
        
        self.columnconfigure(0, weight=1)

    def file_dialog(self, *args):
        """Opens a file dialog window and updates the interval value"""
        new_file_path = tk.filedialog.askopenfilename(title="Select EOP-file", 
                                            filetypes=[("TRF-files", self.file_formats)])
                                            #initialdir = self.intital_dir)
        self.internal_var.set(new_file_path)
        self.file_change()
    
    def file_change(self, *args):
        """Updates the external var if the current path is valid, else reverts the internal var"""
        new_file_path = self.internal_var.get() 
        
        if self.validate(new_file_path):
            self.external_var.set(new_file_path)
        else:
            old_file_path = self.external_var.get()
            self.internal_var.set(old_file_path)

    def validate(self, file_path):
        """Checks that the file path is valid and is not already selected"""
        existing_path = os.path.exists(file_path)
        same_path = (file_path == self.external_var.get())
        
        name, format = os.path.splitext(file_path)
        correct_format = (format.lower() in self.file_formats)
        
        return not same_path and existing_path and correct_format

class Plot(tk.Frame):
    """Custom tkinter widget for using matplotlib with the interface"""

    def __init__(self, master, subplot_rows, subplot_cols, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.fig, self.axes = plt.subplots(subplot_rows, subplot_cols, figsize=(7,7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)    
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(expand=True, fill='both')

    def clear(self):
        """Clear all axes"""
        if isinstance(self.axes, np.ndarray):
            for ax in self.axes:
                ax.clear()
        else:      
            self.axes.clear()

    def draw(self):
        """Show plot"""
        self.canvas.draw()

class ParameterDisplay(tk.Frame):
    """Custom tkinter widget for easy display of text"""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.text = tk.Text(self, state = "disabled")
        self.text.pack(expand=True, fill='both')

    def set(self, string : str):
        """Set text to string"""
        self.text.config(state = "normal")
        self.text.delete('1.0', tk.END)
        self.text.insert('1.0', string)
        self.text.config(state = "disabled")

main = MainWindow()
main.mainloop()