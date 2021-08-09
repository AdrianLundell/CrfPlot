#%%
from HelmertTool.transform import * 
from HelmertTool.load import load_sta

#%% Test of parameters

df = load_sta("2020d.sta")

#%%
parameters = {"translation_x" : 0.0016,
              "translation_y" : 0.0019, 
              "translation_z" : 0.0024,
              "scale_x" : -0.02*10**-9, 
              "scale_y" : -0.02*10**-9, 
              "scale_z" : -0.02*10**-9,
              "rotation_x" : 0, 
              "rotation_y" : 0,
              "rotation_z" : 0}

df_new = helmert_transform(df, parameters)

parameters, sigmas = calculate_parameters(df, df_new, False, "7")
print(parameters)