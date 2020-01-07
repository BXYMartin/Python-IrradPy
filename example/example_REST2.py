import numpy as np
import clearskypy
import os
from matplotlib import pyplot as plt

if __name__ == '__main__':
    # Set the number of sites and randomly generate locations
    # lats,lons need to be np.ndarray
    lats = np.array([84.2, 10.3, -60.021])

    lons = np.array([-160.444, 5.224, 132.4424])
    elevs = np.array([12, 638, 977])
    # Set the time you want to run， here we use time from a data set, you can change it.
    # time need to be np.ndarray ,dtype = np.datetime64
    time = np.arange('2010-01-01T00:15:00', '2010-01-01T23:45:00', dtype='datetime64[m]')
    # create a ClearskyRest class with lat, lon, elev, time and data set path.
    dataset_dir = os.path.join(os.getcwd(), 'MERRA2_data/')

    test_rest2 = clearskypy.model.ClearSkyRest(lats, lons, elevs, time, dataset_dir)
    # run the rest2 model
    [ghi, dni, dhi] = test_rest2.REST2v5()


    plt.title('EXAMPLE for REST2 ')
    plt.xlabel('Time UTC+0')
    plt.ylabel('Irrandance')
    plt.plot(time, ghi[:, 1], ls='-')

    plt.plot(time, dni[:, 1], ls='--')

    plt.plot(time, dhi[:, 1], ls='-.')

    plt.legend(['GHI_SITE1', 'DNI_SITE1', 'DHI_SITE1'])

    plt.show()


