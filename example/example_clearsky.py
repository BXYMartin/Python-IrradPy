import numpy as np
import clearskypy
import os
from matplotlib import pyplot as plt

if __name__ == '__main__':
    # set some example latitudes, longitudes and elevations
    # latitudes range from -90 (south pole) to +90 (north pole) in degrees
    latitudes = np.array([[1.300341, 39.97937]])
    # longitudes range from -180 (west) through 0 at prime meridian to +180 (east)
    longitudes = np.array([[103.771663, 116.34653]]) 
    # elevations are in metres, this influences some solar elevation angles and scale height corrections
    elevations = np.array([[43, 53]])

    # set the time series that you wish to model. Thi can be unique per locaton.
    # first, specify the temporal resolution in minutes
    time_delta = 10  # minute
    # timedef is a list of [(start time , end time)] for each location defined. 
    timedef = [('2010-01-01T08:00:00', '2010-01-02T08:00:00'), 
               ('2010-09-01T08:00:00', '2010-09-02T08:00:00')]  
    # use timeseries_builder to build time series for different station
    time = clearskypy.model.timeseries_builder(timedef, time_delta, np.size(latitudes))

    # specify where the downloaded dataset is. It is best to use the os.path.join function
    dataset_dir = os.path.join(os.getcwd(), 'MERRA2_data', '')
   
    # build the clear-sky REST2v5 model object
    test_rest2 = clearskypy.model.ClearSkyREST2v5(latitudes, longitudes, elevations, time, dataset_dir)
    # run the REST2v5 clear-sky model
    [ghics_rest2, dnics_rest2, difcs_rest2] = test_rest2.REST2v5()
    
    # create the MAC2 model class object
    test_mac = clearskypy.model.ClearSkyMAC2(latitudes, longitudes, elevations, time, dataset_dir)
    # run the MAC2 model
    [ghics_mac2, dnics_mac2, difcs_mac2] = test_mac.MAC2()

    # Create a figure showing the data of both clear-sky estimates
    fig = plt.figure(1)
    plt.style.use('ggplot')

    ax = plt.subplot(121)
    # Remove the plot frame lines. They are unnecessary chartjunk.   
    ax.spines["top"].set_visible(False)    
    ax.spines["bottom"].set_visible(False)    
    ax.spines["right"].set_visible(False)    
    ax.spines["left"].set_visible(False)
    plt.plot(time[:, 0], ghics_rest2[:, 0], ls='-')
    plt.plot(time[:, 0], dnics_rest2[:, 0], ls='--')
    plt.plot(time[:, 0], difcs_rest2[:, 0], ls='-.')
    ax.set_xlabel('Time UTC')
    ax.set_ylabel('Irradiance')
    ax.set_title('REST2v5', fontsize=12, )
    ax.title.set_
    # Limit the range of the plot to only where the data is.    
    # Avoid unnecessary whitespace.    
    plt.ylim(0, 700)    
    #plt.xlim(1968, 2014)    

    plt.subplot(122)
    plt.title('MAC2')
    plt.plot(time[:, 1], ghics_mac2[:, 1], ls='-')
    plt.plot(time[:, 1], dnics_mac2[:, 1], ls='--')
    plt.plot(time[:, 1], difcs_mac2[:, 1], ls='-.')
    plt.xlabel('Time UTC')
    plt.ylabel('Irradiance')
    plt.legend(['GHIcs', 'DNIcs', 'DIFcs'])

    plt.show()

    
    # Save the data to file
    for i in range(time.shape[1]):
            savedata = [time[:, i], ghics_rest2[:, i], dnics_rest2[:, i],
                        difcs_rest2[:, i], ghics_mac2[:, i], dnics_mac2[:, i],
                        difcs_mac2[:, i]]      
            savefname = 'site[' + str(latitudes[0,i]) + ',' + str(longitudes[0,i]) +'].txt'
            np.savetxt(savefname, savedata, fmt=['%s']+['%.4f']*6, delimiter=',',)
         
