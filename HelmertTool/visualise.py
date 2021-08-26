import geopandas as gpd
import pandas as pd 
import numpy as np
import matplotlib.image as mpimg
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
    
def plot_residuals(df, ax1, ax2):
    """Plots UEN-residuals scattered over a world map to axes"""
    worldmap.plot(color="lightgrey", ax=ax1)
    worldmap.plot(color="lightgrey", ax=ax2)

    #img = mpimg.imread('C:/Users/Adrian/Documents/NVI/map.png')
    #ax1.imshow(img, )
    #ax2.imshow(img)
    ax1.set_title("NE-residual components")
    ax2.set_title("UP-residual component")

    #ax1.quiver(df_from.LAT, df_from.LONG, df_from.dE, df_from.dN, color="b")
    if not df is None:
        q = ax1.quiver(df.LONG, df.LAT, df.dE, df.dN, color="k", scale=2)
        ax1.quiverkey(q, 0.9,1.05, 10**-1, "10 cm", color = "red")

        q = ax2.quiver(df.LONG, df.LAT, np.zeros(len(df.dU)), df.dU, scale=2)
        ax2.quiverkey(q, 0.9,1.05, 10**-1, "10 cm", color = "red")
    
    ax1.grid()
    ax2.grid()

def plot_residuals_hist(df_from, df_transformed, ax1, ax2):
    """Plots UEN-residuals plotted over value"""
    ax1.hist([df_from.dU, df_from.dE, df_from.dN], 200, stacked=True)
    ax2.hist([df_transformed.dU, df_transformed.dE, df_transformed.dN], 200, stacked=True)

