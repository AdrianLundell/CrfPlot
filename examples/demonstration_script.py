#%%
from HelmertTool.calc import * 
from HelmertTool.io import load_sta
from HelmertTool.units import *

#%% Simplest case 
#load data
frame_from = load_sta("C:/Users/Adrian/Documents/NVI/HelmertTool/data/2020d_off_0_0_10p_rate_0_0_0.sta")
frame_to = load_sta("C:/Users/Adrian/Documents/NVI/HelmertTool/data/2020d.sta")

#Calculate a weighted transform with 7 parameters
parameters, sigmas = calculate_parameters(frame_from, frame_to, weighted=True, type = "7")

#Transform the frame with the calculated parameters
frame_transformed = helmert_transform(frame_from, parameters)

#Calculate residuals between the and decompose from XYZ to NEU coordinates.
frame_transformed = calculate_residuals(frame_transformed, frame_to)
frame_transformed = decompose_residuals(frame_transformed)

#Format data as as a string, print
string = to_string(frame_from, frame_to, frame_transformed, parameters, sigmas)
print(string)

#Syntax to save a file
with open("test_1.txt", "w") as f:
    f.write(string)

#%% Fit only translations
custom_dictionary = {"translation_x" : None, #Entering None tells the function to calculate this parameter
                    "translation_y" : None, 
                    "translation_z" : None,
                    "scale_x" : 0, #Entering a number fixes this parameter of the transform, set to 0 to ignore.
                    "scale_y" : 0, 
                    "scale_z" : 0,
                    "rotation_x" : 0, 
                    "rotation_y" : 0,
                    "rotation_z" : 0}

#Calculate parameters as before but with additional custom dictionary argument
parameters, sigmas = calculate_parameters(frame_from, frame_to, weighted=True, type = "7", custom_dict=custom_dictionary)
print(parameters)

#%% Custom transform
custom_dictionary = {"translation_x" : 0.01,  #meter
                    "translation_y" : 0.01,   #meters
                    "translation_z" : 0.01,   #meters
                    "scale_x" : 0,            #unitless
                    "scale_y" : 0,            #unitless
                    "scale_z" : 0,            #unitless
                    "rotation_x" : 0,         #radians
                    "rotation_y" : 0,         #radians
                    "rotation_z" : 0.01}      #radians

frame_transformed = helmert_transform(frame_from, custom_dictionary)
frame_transformed = calculate_residuals(frame_from, frame_to)
frame_transformed = decompose_residuals(frame_from)

print(frame_transformed)


#%% Loop calculations

#Enter a list of frames to transform from
frame_path_list = ["C:/Users/Adrian/Documents/NVI/HelmertTool/data/2020d_off_0_0_10p_rate_0_0_0.sta",
                   "C:/Users/Adrian/Documents/NVI/HelmertTool/data/2020d_off_0_10p_0_rate_0_0_0.sta",
                   "C:/Users/Adrian/Documents/NVI/HelmertTool/data/2020d_off_10p_0_0_rate_0_0_0.sta"]

#load the frame to transform to
frame_to = load_sta("C:/Users/Adrian/Documents/NVI/HelmertTool/data/2020d.sta")

#Python syntax for looping over a list
for frame_path in frame_path_list:

    #Calculations as previouslt
    frame_from = load_sta(frame_path)
    parameters, sigmas = calculate_parameters(frame_from, frame_to, weighted=True, type = "7")
    
    print(frame_path)
    print(parameters)
    print("")

    #Automatic test of parameters according to some condition
    if abs(parameters["translation_x"]) > 0.1:
        print("Large translaton found for transform from " + frame_path)
        print("")


#%% Data handling in pandas
#%%#Look at values from a single column
X = frame_to.X
print(X)
#or
X = frame_to["X"]
print(X)

#%%Plot histograms
frame_to.hist()

#%% Filtering, for example only use datapoints with small sigma values 
frame_to = frame_to[frame_to.X_sigma < 0.1]

#%%Rescale column
frame_to.X = frame_to.X * 1000
frame_to.Y = frame_to.Y * micro_arcsecond.convertion_factor #A number of unit convertions are available from the units subpackage

#%%Look at single station
row = frame_to[frame_to.Station_Name == "ZELENCHK"]
print(row)