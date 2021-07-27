import tkinter as tk 
import tkinter.filedialog
import tkinter.ttk as ttk 
import os 

from logic import * 




# class ParameterDisplay(tk.Frame):
#     """Custom tkinter widget for easy display of text"""

#     def __init__(self, master, *args, **kwargs):
#         super().__init__(master, *args, **kwargs)

#         self.text = tk.Text(self, state = "disabled")
#         self.text.pack(expand=True, fill='both')

#     def set(self, string : str):
#         """Set text to string"""
#         self.text.config(state = "normal")
#         self.text.delete('1.0', tk.END)
#         self.text.insert('1.0', string)
#         self.text.config(state = "disabled")



test_data = pd.DataFrame({"Station_Name" : ["a", "b", "c"], "Sigma" : [1,20,3], "Selected" :True})

main = MainWindow()
main.mainloop()