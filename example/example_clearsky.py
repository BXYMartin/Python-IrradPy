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
    time = clearskypy.model.timeseries_builder(timedef, time_delta)

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



    plt.figure(1)

    plt.title('EXAMPLE for REST2 ')

    plt.subplot(221)
    plt.plot(time[:, 0], ghics[:, 0], ls='-')
    plt.plot(time[:, 0], dnics[:, 0], ls='--')
    plt.plot(time[:, 0], difcs[:, 0], ls='-.')
    plt.xlabel('Time UTC+0')
    plt.ylabel('Irrandance')
    plt.legend(['GHI_SITE1', 'DNI_SITE1', 'DHI_SITE1'])

    plt.subplot(222)
    plt.plot(time[:, 1], ghics[:, 1], ls='-')
    plt.plot(time[:, 1], dnics[:, 1], ls='--')
    plt.plot(time[:, 1], difcs[:, 1], ls='-.')
    plt.xlabel('Time UTC+0')
    plt.ylabel('Irrandance')
    plt.legend(['GHI_SITE2', 'DNI_SITE2', 'DHI_SITE2'])

    plt.subplot(223)
    plt.plot(time[:, 2], ghics[:, 2], ls='-')
    plt.plot(time[:, 2], dnics[:, 2], ls='--')
    plt.plot(time[:, 2], difcs[:, 2], ls='-.')
    plt.xlabel('Time UTC+0')
    plt.ylabel('Irrandance')
    plt.legend(['GHI_SITE3', 'DNI_SITE3', 'DHI_SITE3'])

    plt.show()


