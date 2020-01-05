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
    station_number = 1
    lats = np.random.random(station_number) * 90
    lons = np.random.random(station_number) * 360 - 180

    # Set the time you want to run， here we use time from a data set, you can change it.
    # time need to be np.ndarray ,dtype = np.datetime64
    dataset = xr.open_dataset('./MERRA2_data/aer-rad-slv_merra2_reanalysis_2010-01-01.nc')
    time = dataset['time'].data
    time = np.unique(time)

    # create a ClearskyRest class with lat, lon, elev, time and data set path.
    #test_model1 = clearskypy.model.ClearSkyRest(lats, lons, 1, time, './MERRA2_data/')
    # run the rest2 model
    #[ghi, dni, dhi] = test_model1.rest2()

    #print(ghi.shape)
    #print(dni.shape)
    #print(dhi.shape)

    test_model2 = clearskypy.model.ClearSkyMac(lats, lons, 1, time, './MERRA2_data/')
    [Egh, Edn, Edh] = test_model2.mac2(3)
    print(Egh)

    '''
    plt.title('example for REST2 model')
    plt.xlabel('date')
    plt.ylabel('irrandance')
    plt.plot(time, ghi[:, 0])
    plt.show()
    '''

