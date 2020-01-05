import numpy as np
import clearskypy
import os
import pvlib
import xarray as xr
import datetime
from matplotlib import pyplot as plt

if __name__ == '__main__':
    # Set the number of sites and randomly generate locations
    # lats,lons need to be np.ndarray
    station_number = 3
    lats = np.random.random(station_number) * 90
    lons = np.random.random(station_number) * 360 - 180

    # Set the time you want to run， here we use time from a data set, you can change it.
    # time need to be np.ndarray ,dtype = np.datetime64
    dataset = xr.open_dataset('./MERRA2_data/aer-rad-slv_merra2_reanalysis_2010-01-01.nc')
    time = dataset['time'].data
    time = np.unique(time)

    # create a ClearskyRest class with lat, lon, elev, time and data set path.
    test_mac = clearskypy.model.ClearSkyMac(lats, lons, 1, time, './MERRA2_data/')
    # run the mac2 model
    [Egh, Edn, Edh] = test_mac.mac2(3)


    Egh[np.isnan(Egh)] = 0
    Edn[np.isnan(Edn)] = 0
    Edh[np.isnan(Edh)] = 0


    plt.title('EXAMPLE for MAC2 ')
    plt.xlabel('Time UTC+0')
    plt.ylabel('Irrandance')
    plt.plot(time, Egh[:, 0], ls='-')

    plt.plot(time, Edn[:, 0], ls='--')

    plt.plot(time, Edh[:, 0], ls='-.')

    plt.legend(['EGH_SITE1', 'EDN_SITE1', 'EDH_SITE1'])

    plt.show()

