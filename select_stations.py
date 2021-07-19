import tkinter as tk
from tkinter import ttk

import pandas as pd 

class SelectStationsWindow(tk.Tk):
    
    def __init__(self, master, *args, **kwargs):
        super().__init__()
        self.stations = master
        
        self.init_rows_and_header_frame()
        self.rows = {}

        for station in self.stations.itertuples():
            row = SelectStationsRow(self.rows_frame, station, self.set_selection)            
            self.rows[station.Index] = row
        
        self.header_frame.columnconfigure(0, minsize=100)
        self.header_frame.columnconfigure(1, minsize=100)
        self.header_frame.columnconfigure(2, minsize=100)

        self.rows_frame.columnconfigure(0, minsize=100)
        self.rows_frame.columnconfigure(1, minsize=100)
        self.rows_frame.columnconfigure(2, minsize=100)

        self.grid()

        tk.Button(self.header_frame, text = "Select", command = self.sort_by_select()).grid(row=0, column=0)
        tk.Button(self.header_frame, text = "Station name", command = self.sort_by_name).grid(row=0, column=1)
        tk.Button(self.header_frame, text = "Sigma", command = self.sort_by_sigma).grid(row=0, column=2)


    def grid(self):
        for row_index, station_index in enumerate(self.stations.index):  
            self.rows[station_index].grid(row_index)

    def set_selection(self, index, value):
        self.stations.at[index, "Selected"] = value

    def sort_by_name(self):
        self.stations = self.stations.sort_values(by="Station_Name")
        self.grid()

    def sort_by_sigma(self):
        self.stations = self.stations.sort_values(by="Sigma")
        self.grid()

    def init_rows_and_header_frame(self):
        canvas = tk.Canvas(self, highlightthickness=0, height=170, width=500)
        canvas.grid(row=4, column=0, sticky="nsew")
        header_canvas = tk.Canvas(self, highlightthickness=0, height=23) #!Hardcoded height
        header_canvas.grid(row=2, column=0, sticky="we")

        def xview(*args):
            canvas.xview(*args)
            header_canvas.xview(*args)

        yscrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        yscrollbar.grid(row=4, column=1, sticky = "ns")
        xscrollbar = tk.Scrollbar(self, orient="horizontal", command=xview)
        xscrollbar.grid(row=5, column=0, sticky = "we")

        canvas.configure(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
        header_canvas.configure(xscrollcommand=xscrollbar.set)

        self.rows_frame = tk.Frame(canvas)
        self.header_frame = tk.Frame(header_canvas)
        canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")   
        header_canvas.create_window((0, 0), window=self.header_frame, anchor="nw")
        
        def scroll_config(*args):
            """Sets scroll region for table and header"""
            region = (0,0, header_canvas.bbox("all")[2], canvas.bbox("all")[3])
            canvas.configure(scrollregion=region)
            header_canvas.configure(scrollregion=header_canvas.bbox("all"))

        self.rows_frame.bind("<Configure>", scroll_config)
        self.header_frame.bind("<Configure>", scroll_config)



class SelectStationsRow():

    def __init__(self, master, station, set_selection, *args, **kwargs):

        self.master = master 
        self.set_selection = set_selection

        self.var = tk.BooleanVar(self.master, value = station.Selected)
        self.var.trace("w", lambda *args: self.set_selection(station.Index, self.var.get()))

        self.check = tk.Checkbutton(self.master, variable=self.var, onvalue=True, offvalue=False)
        self.station_name_label = tk.Label(self.master, text = station.Station_Name)
        self.sigma_label = tk.Label(self.master, text = station.Sigma)

    def grid(self, row):
        self.check.grid_forget()
        self.check.grid(row=row, column=0)
        self.station_name_label.grid_forget()
        self.station_name_label.grid(row=row, column=1)
        self.sigma_label.grid_forget()
        self.sigma_label.grid(row=row, column=2)

test_data = pd.DataFrame({"Station_Name" : ["a", "b", "c"], "Sigma" : [1,20,3], "Selected" :True})

main = SelectStationsWindow(test_data)
main.mainloop()

