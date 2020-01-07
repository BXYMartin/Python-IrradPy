import numpy as np
import clearskypy
import os
import pvlib
import xarray as xr
import datetime
from matplotlib import pyplot as plt

if __name__ == '__main__':
    # lats,lons need to be np.ndarray

    lats = np.array([84.2, 10.3, -60.021])

    lons = np.array([-160.444, 5.224, 132.4424])

    elevs = np.array([12, 638, 977])
    # time need to be np.ndarray ,dtype = np.datetime64
    time_delta = 10  # minute
    # timedef is a list of (start time , end time) for each site
    timedef = [('2010-01-01T00:15:00', '2010-01-01T23:45:00'), ('2010-06-01T00:15:00', '2010-06-01T23:45:00'),
               ('2010-09-01T00:15:00', '2010-09-01T23:45:00')]
    # use timeseries_builder to build time series for different station
    time_new = clearskypy.model.timeseries_builder(timedef, time_delta)

    dataset_dir = os.path.join(os.getcwd(), 'MERRA2_data', '')

    # create a ClearskyRest class with lat, lon, elev, time and data set path.
    test_mac = clearskypy.model.ClearSkyMAC(lats, lons, elevs, time_new, dataset_dir)
    # run the mac2 model
    [Egh, Edn, Edh] = test_mac.MAC2()


    plt.title('EXAMPLE for MAC2 ')
    plt.xlabel('Time UTC+0')
    plt.ylabel('Irrandance')
    plt.plot(time_new[:, 1], Egh[:, 1], ls='-')

    plt.plot(time_new[:, 1], Edn[:, 1], ls='--')

    plt.plot(time_new[:, 1], Edh[:, 1], ls='-.')

    plt.legend(['EGH_SITE1', 'EDN_SITE1', 'EDH_SITE1'])

    plt.show()

