import geopandas as gpd
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt

worldmap = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

def plot_sites3D(df: pd.DataFrame):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.scatter3D(df.X, df.Y, df.Z)
    plt.show()

def plot_sites(df: pd.DataFrame, ax: plt.Axes):
    """Plots the station sites scattered over a world map to ax"""
    worldmap.plot(color="lightgrey", ax=ax)
    ax.scatter(df.LAT, df.LONG, s=4)
    #for x,y,s in zip(df.LAT, df.LONG, df.Station_Name):
    #    plt.text(x,y,s, fontsize=5)
    ax.grid()
    
def plot_residuals(df_to, df_from, df_transformed, ax1, ax2, plot_transformed):
    """Plots UEN-residuals scattered over a world map to axes"""
    worldmap.plot(color="lightgrey", ax=ax1)
    #ax1.quiver(df_from.LAT, df_from.LONG, df_from.dE, df_from.dN, color="b")
    if plot_transformed:
        q = ax1.quiver(df_transformed.LAT, df_transformed.LONG, df_transformed.dE, df_transformed.dN, color="k", scale=2)
    else:
        q = ax1.quiver(df_from.LAT, df_from.LONG, df_from.dE, df_from.dN, color="k", scale=2)

    ax1.quiverkey(q, 0.9,1.05,2*10**-1, "2e-1 m", color = "red")
    ax1.set_title("NE-residual components")
    ax1.grid()

    worldmap.plot(color="lightgrey", ax=ax2)
    if plot_transformed:
        q = ax2.quiver(df_transformed.LAT, df_transformed.LONG, np.zeros(len(df_from.dU)), df_transformed.dU, scale=2)
    else:
        q = ax2.quiver(df_from.LAT, df_from.LONG, np.zeros(len(df_from.dU)), df_from.dU, scale=2)

    ax2.set_title("UP-residual component")
    ax2.quiverkey(q, 0.9,1.05,2*10**-1, "2e-1 m", color = "red")
    ax2.grid()

def plot_residuals_hist(df_from, df_transformed, ax1, ax2):
    """Plots UEN-residuals plotted over value"""
    ax1.hist([df_from.dU, df_from.dE, df_from.dN], 200, stacked=True)
    ax2.hist([df_transformed.dU, df_transformed.dE, df_transformed.dN], 200, stacked=True)

