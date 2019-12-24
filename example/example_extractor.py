import numpy as np
import clearskypy
import os
import pvlib
import xarray as xr
import datetime


if __name__ == '__main__':
    # Set the number of sites and randomly generate locations
    # lats,lons need to be np.ndarray
    station_number = 3
    lats = np.random.random(station_number) * 90
    lons = np.random.random(station_number) * 360 - 180
    # Set the time you want to run， here we use time from a data set, you can change it.
    # time need to be np.ndarray ,dtype = np.datetime64
    dataset = xr.open_dataset('./MERRA2_data/aer-rad-slv_merra2_reanalysis_2018-01-01.nc')
    time = dataset['time'].data
    time = np.unique(time)

    # create a ClearskyRest class with lat, lon, elev, time and data set path.
    test_model = clearskypy.model.ClearSkyRest(lats, lons, 1, time, './MERRA2_data/')
    # run the rest2 model
    [ghi, dni, dhi] = test_model.rest2()

    print(ghi)
    print(dni)
    print(dhi)
