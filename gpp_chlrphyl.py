
import iris
import numpy as np
import matplotlib.pyplot as plt 
from iris.experimental.equalise_cubes import equalise_attributes
from spawnCommand import SpawnCommand
import iris.plot as iplt
import iris.coord_categorisation as icat
import cartopy.crs as ccrs


def create_video():

    #creating the video
    SpawnCommand("rm -f gpp_chlrphyl_movie/gpp_chlrphyl.avi")
    options = ("-r 5 -vcodec png -y -i " 
             + "gpp_chlrphyl_movie/image-%04d.png -r 5 -vcodec msmpeg4v2 -qblur 0.01 -qscale 5 ")
    SpawnCommand("ffmpeg " + options + "gpp_chlrphyl_movie/gpp_chlrphyl.avi")

    #creating the video
#    SpawnCommand("ffmpeg -i image-%04d.png TemperatureVideo1.mp4")
#    SpawnCommand('ffmpeg -i TemperatureVideo1.mp4 -filter:v "setpts=5.0*PTS" gpp.mp4')
#    print ("Deleting the unneeded images...")
#    SpawnCommand("rm -f *.png")
#    SpawnCommand("rm -f TemperatureVideo1.mp4")
    

def myload(x):
    cubes = iris.cube.CubeList([])
    
    for i in range(1, 13):
        for n in range(0, 3):
            tempfile = 'gpp_chlrphyl_1850/'+ x + '/bk179a.p61850' + str("{:02d}".format(i)) + str(n) + '1.nc'
            blockcube = iris.load_cube(tempfile)
            
            cubes.append(blockcube)
    equalise_attributes(cubes)
    cube = cubes.concatenate_cube()

    return (cube)

def main():

    gppcube = myload('gpp')
    chlrphylcube = myload('chlrphyl')
    #data = np.add(gppcube.data, chlrphylcube.data)
    
    gppLbound = np.amin(gppcube.data)
    gppUbound = np.amax(gppcube.data)



    chlrphylLbound = np.amin(chlrphylcube.data)
    chlrphylUbound = np.amax(chlrphylcube.data)
    print(gppLbound, gppUbound)
    print(chlrphylLbound, chlrphylUbound)
       
    icat.add_month(gppcube, 'time')
    months = gppcube.coord('month')
    
    # Set the limits for the loop over years.  
    minTime = 0
    maxTime = 360
    
    fileIndex = 0
    for time in range(minTime, maxTime):

        # Avoid timesteps that are broken - ie, cause a stop with this error:
	# ValueError: A LinearRing must have at least 3 coordinate tuple
        if time in [12, 310, 320, 347, 351, 354]: 
	   continue

        # Set up for larger image.
        figSize = [12, 6]
        fig = plt.figure(figsize=figSize, dpi=200)
        rect = 0,0,200*figSize[0],200*figSize[1]
        fig.add_axes(rect)
        geo_axes = plt.axes(projection=ccrs.PlateCarree())
	
        # We need to fix the boundary of the figure (otherwise we get a black border at left & top).
        # Cartopy removes matplotlib's axes.patch (which normally defines the boundary) and
        # replaces it with outline_patch and background_patch.  It's the former which is causing
        # the black border.  Get the axis object and make its outline patch invisible.
        geo_axes.outline_patch.set_visible(False)
        plt.margins(0,0)
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

        # Contour plot the temperatures and add the coastline.
        
        iplt.contourf(chlrphylcube[time], vmin = chlrphylLbound, vmax = chlrphylUbound, cmap = 'BuGn')
        iplt.contourf(gppcube[time], vmin = gppLbound, vmax = gppUbound, cmap = 'YlGn')
        
        #-6.4358826, 27.94899
        plt.gca().coastlines()
        #plt.colorbar(boundaries = (-6, -3, 0, 4, 8, 12, 16, 20, 25), values = (-6, -3, 0, 4, 8, 12, 16, 20))
        # We need to fix the boundary of the figure (otherwise we get a black border at left & top).
        # Cartopy removes matplotlib's axes.patch (which normally defines the boundary) and
        # replaces it with outline_patch and background_patch.  It's the former which is causing
        # the black border.  Get the axis object and make its outline patch invisible.
        ax = plt.gca()
        ax.outline_patch.set_visible(False)

        # Extract the year value and display it (coordinates used in locating the text are
        # those of the data).
        month = months[time].points[0]

        # Display year on both sides of the display.
        plt.text(-110, 0, month, horizontalalignment='center', 
	         verticalalignment='top', size='large',
	         fontdict={'family' : 'monospace'})
        plt.text( 70, 0, month, horizontalalignment='center', 
	         verticalalignment='top', size='large',
		 fontdict={'family' : 'monospace'})
       
        # Now save the plot in an image file.  The files are numbered sequentially, starting
        # from 000.png; this is so that the ffmpeg command can grok them.
        filename = "gpp_chlrphyl_movie/image-%04d.png" % fileIndex
	fileIndex += 1
#        plt.savefig(filename, bbox_inches='tight', pad_inches=0)
        plt.savefig(filename, dpi=200)
        
        # Discard the figure (otherwise the text will be overwritten
        # by the next iteration).
        plt.close()
       
    print("images made! Now converting to .mp4...")
    create_video()
    print("Opening video...")
    
    
if __name__  == "__main__":
    main()
