import numpy as np
import clearskypy
import os
import pvlib
import xarray as xr
import datetime
from matplotlib import pyplot as plt

if __name__ == '__main__':
       # set some example latitudes, longitudes and elevations
    # latitudes range from -90 (south pole) to +90 (north pole) in degrees
    latitudes = np.array([1.300350, 39.976060,32.881034])
    # longitudes range from -180 (west) through 0 at prime meridian to +180 (east)
    longitudes = np.array([103.771630, 116.344477, -117.233575])
    # elevations are in metres, this influences some solar elevation angles and scale height corrections
    elevations = np.array([30, 50.2, 62])
     
    # set the time series that you wish to model. Thi can be unique per locaton.
    # first, specify the temporal resolution in minutes
    time_delta = 10  # minute
    # timedef is a list of [(start time , end time)] for each location defined. 
    timedef = [('2010-01-01T00:15:00', '2010-01-01T23:45:00'), 
               ('2010-06-01T00:15:00', '2010-06-01T23:45:00'),
               ('2010-09-01T00:15:00', '2010-09-01T23:45:00')]
    # use timeseries_builder to build time series for different station
    time = clearskypy.model.timeseries_builder(timedef, time_delta)

    # specify where the downloaded dataset is. It is best to use the os.path.join function
    dataset_dir = os.path.join("E:", "MERRA2", "MERRA2_data", '')
    
    # create a ClearskyRest class with lat, lon, elev, time and data set path.
    test_mac = clearskypy.model.ClearSkyMAC2(latitudes, longitudes, elevations, time, dataset_dir)
    # run the mac2 model
    [Egh, Edn, Edh] = test_mac.MAC2()

    plt.figure(1)

    plt.title('EXAMPLE for MAC2 ')

    plt.subplot(221)
    plt.plot(time[:, 0], Egh[:, 0], ls='-')
    plt.plot(time[:, 0], Edn[:, 0], ls='--')
    plt.plot(time[:, 0], Edh[:, 0], ls='-.')
    plt.xlabel('Time UTC+0')
    plt.ylabel('Irrandance')
    plt.legend(['GHI_SITE1', 'DNI_SITE1', 'DHI_SITE1'])

    plt.subplot(222)
    plt.plot(time[:, 1], Egh[:, 1], ls='-')
    plt.plot(time[:, 1], Edn[:, 1], ls='--')
    plt.plot(time[:, 1], Edh[:, 1], ls='-.')
    plt.xlabel('Time UTC+0')
    plt.ylabel('Irrandance')
    plt.legend(['GHI_SITE2', 'DNI_SITE2', 'DHI_SITE2'])

    plt.subplot(223)
    plt.plot(time[:, 2], Egh[:, 2], ls='-')
    plt.plot(time[:, 2], Edn[:, 2], ls='--')
    plt.plot(time[:, 2], Edh[:, 2], ls='-.')
    plt.xlabel('Time UTC+0')
    plt.ylabel('Irrandance')
    plt.legend(['GHI_SITE3', 'DNI_SITE3', 'DHI_SITE3'])

    plt.show()

