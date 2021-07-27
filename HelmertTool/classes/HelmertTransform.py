from HelmertTool.logic.transform import *
from HelmertTool.logic.load import *
from HelmertTool.logic.transform import *
from HelmertTool.logic.plot import *

from HelmertTool.classes.HelmertParameters import HelmertParameters

class HelmertTransform():
    """Wraps all analysis and visulisation of a helmert transform from df_from to df_to of the given type in a single object"""

    weighted : bool                 #True for weighted least squares regression 
    type : str                      #Type of helmert transform: 7, 8, or 9 parameters ()
    parameters : dict               #Calculated helmert parameters
    df_to : pd.DataFrame            #Values to transform from
    df_from : pd.DataFrame          #Values to transfrom to
    df_transformed : pd.DataFrame   #Transformed values
    epoch : float                   #Epoch for value in modified julian date
    
    def __init__(self, df_from: pd.DataFrame, df_to: pd.DataFrame, parameters: HelmertParameters, weighted: bool = False, type: str = "7", epoch = 0):
        self.weighted = weighted 
        self.type = type
        self.epoch = epoch
    
        self.parameters = parameters

        self.df_to = df_to
        self.df_from = df_from
    
        self.df_from = calculate_residuals(df_from, df_to) 
        self.df_from = decompose_residuals(df_from)

        values, sigmas = calculate_parameters(df_from, df_to, weighted, type, parameters)
        self.parameters.set(values, sigmas)
        self.df_transformed = helmert_transform(df_from, self.parameters)
        
        self.df_transformed = calculate_residuals(self.df_transformed, df_to) 
        self.df_transformed = decompose_residuals(self.df_transformed)

    def plot_sites(self, ax: plt.Axes):
        plot_sites(self.df_from, ax)
        plot_sites(self.df_to, ax)
        plot_sites(self.df_transformed, ax)

    def plot_residuals(self, ax1: plt.Axes, ax2: plt.Axes, plot_transformed):
        plot_residuals(self.df_to, self.df_from, self.df_transformed, ax1, ax2, plot_transformed)

    def plot_residuals_hist(self, ax1, ax2):
        plot_residuals_hist(self.df_from, self.df_transformed, ax1, ax2)