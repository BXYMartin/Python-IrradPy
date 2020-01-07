import numpy as np
import clearskypy
import os
from matplotlib import pyplot as plt

if __name__ == '__main__':
    # set some example latitudes, longitudes and elevations
    # latitudes range from -90 (south pole) to +90 (north pole) in degrees
    latitudes = np.array([1.300350, 39.976060,32.881034])
    # longitudes range from -180 (west) through 0 at prime meridian to +180 (east)
    longitudes = np.array([103.771630, 116.344477, -117.233575])
    # elevations are in metres, this influences some solar elevation angles and scale height corrections
    elevations = np.array([30, 50.2, 62])
     
    # set the time you want to run， here we use time from a data set, you can change it.
    # time need to be np.ndarray ,dtype = np.datetime64
    time = np.arange('2010-01-01T00:15:00', '2010-01-01T23:45:00', dtype='datetime64[m]')
    
    # specify where the downloaded dataset is. It is best to use the os.path.join function
    dataset_dir = os.path.join(os.getcwd(), 'MERRA2_data/')

    # build the clear-sky REST2v5 model object
    test_rest2 = clearskypy.model.ClearSkyRest(latitudes, longitudes, elevations, time, dataset_dir)
    # run the REST2v5 clear-sky model
    [ghics, dnics, difcs] = test_rest2.REST2v5()


    plt.title('EXAMPLE for REST2 ')
    plt.xlabel('Time UTC+0')
    plt.ylabel('Irrandance')
    plt.plot(time, ghics[:, 1], ls='-')

    plt.plot(time, dnics[:, 1], ls='--')

    plt.plot(time, difcs[:, 1], ls='-.')

    plt.legend(['GHI_SITE1', 'DNI_SITE1', 'DHI_SITE1'])

    plt.show()


