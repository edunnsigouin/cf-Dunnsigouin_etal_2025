"""
Plots of a map of the given forecast data domain
"""

from forsikring import verify
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.ticker as mticker

def plot_map(latitude,longitude,domain,figsize,write2file):

    # Create a plot with a specific projection
    plt.figure(figsize=(figsize[0],figsize[1]))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Set the extent to the specified boundaries
    ax.set_extent([longitude[0]-0.14, longitude[-1]+0.14, latitude[-1]-0.14, latitude[0]+0.14])

    # Add features to the map for more details
    ax.add_feature(cfeature.LAND,edgecolor='none')
    ax.add_feature(cfeature.OCEAN)
    
    # gridlines
    gl          = ax.gridlines(draw_labels=True,color='k',linestyle='--')
    ygridlines  = np.arange(latitude[-1],latitude[0]+0.5,0.25) - 0.25/2
    xgridlines  = np.arange(longitude[0],longitude[-1]+0.5,0.25) - 0.25/2
    gl.xlocator = mticker.FixedLocator(xgridlines)
    gl.ylocator = mticker.FixedLocator(ygridlines)
    
    # Display the plot
    plt.title("Map of " + domain,fontsize=13)
    plt.tight_layout()
    if write2file: plt.savefig(figname)
    plt.show()

# Run the function to plot the map
domain     = 'oslo'
write2file = True
figname    = '/nird/home/edu061/cf-forsikring/fig/master/' + domain + '.pdf'
figsize    = np.array([7,7])
dim        = verify.get_data_dimensions('0.25x0.25', 'daily', domain)
plot_map(dim.latitude,dim.longitude,domain,figsize,write2file)

