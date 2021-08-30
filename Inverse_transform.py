#%%
from HelmertTool.calc import * 
from HelmertTool.io import load_sta
from HelmertTool.units import *

#%% Simplest case 
frame_from = load_sta("C:/Users/Adrian/Documents/NVI/HelmertTool/data/2020d_off_0_0_10p_rate_0_0_0.sta")
frame_to = load_sta("C:/Users/Adrian/Documents/NVI/HelmertTool/data/2020d.sta")

parameters, sigmas = calculate_parameters(frame_from, frame_to, weighted=True, type = "7")

frame_transformed = helmert_transform(frame_from, parameters)
frame_transformed = calculate_residuals(frame_from, frame_to)
frame_transformed = decompose_residuals(frame_from)

string = to_string(frame_from, frame_to, frame_transformed, parameters, sigmas)
print(string)

with open("test_1.txt", "w") as f:
    f.write(string)

#%% Fit only translations
custom_dictionary = {"translation_x" : None,
                    "translation_y" : None, 
                    "translation_z" : None,
                    "scale_x" : 0, 
                    "scale_y" : 0, 
                    "scale_z" : 0,
                    "rotation_x" : 0, 
                    "rotation_y" : 0,
                    "rotation_z" : 0}

parameters, sigmas = calculate_parameters(frame_from, frame_to, weighted=True, type = "7", custom_dict=custom_dictionary)
print(parameters)

#%% Custom transform
#TODO:Comment units!!! 
custom_dictionary = {"translation_x" : 0.01, 
                    "translation_y" : 0.01, 
                    "translation_z" : 0.01,
                    "scale_x" : 0, 
                    "scale_y" : 0, 
                    "scale_z" : 0,
                    "rotation_x" : 0, 
                    "rotation_y" : 0,
                    "rotation_z" : 0.01}

frame_transformed = helmert_transform(frame_from, custom_dictionary)
frame_transformed = calculate_residuals(frame_from, frame_to)
frame_transformed = decompose_residuals(frame_from)
print(frame_transformed)


#%% Loop calculations
frame_path_list = ["C:/Users/Adrian/Documents/NVI/HelmertTool/data/2020d_off_0_0_10p_rate_0_0_0.sta",
                   "C:/Users/Adrian/Documents/NVI/HelmertTool/data/2020d_off_0_10p_0_rate_0_0_0.sta",
                   "C:/Users/Adrian/Documents/NVI/HelmertTool/data/2020d_off_10p_0_0_rate_0_0_0.sta"]

frame_to = load_sta("C:/Users/Adrian/Documents/NVI/HelmertTool/data/2020d.sta")

for frame_path in frame_path_list:
    frame_from = load_sta(frame_path)

    parameters, sigmas = calculate_parameters(frame_from, frame_to, weighted=True, type = "7")
    
    print(frame_path)
    print(parameters)
    print("")

    #Automatic test of parameters
    if abs(parameters["translation_x"]) > 0.1:
        print("Large translaton found for transform from " + frame_path)
        print("")

#%% Data handling 
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
frame_to.Y = frame_to.Y * micro_arcsecond.convertion_factor


#%%Look at single station
row = frame_to[frame_to.Station_Name == "ZELENCHK"]
print(row)