import numpy as np
import clearskypy
import os
import pvlib
import xarray as xr


def test_extract_MERRA2(lats, lons, datavecs, elevs, aerpath, radpath, slvpath, asmpath):
    """
    extract data from merra2

    lats lons elevs need to be numpy.ndarray ,same size ,match every station

    lats and lons define  stations as a list
    """

    # safety check
    if np.size(lats, 0) != np.size(lons, 0) and np.size(lons, 0) != np.size(elevs, 0):
        print('ERROR: lats , lons , elevs dimention not match')
        return -1

    aer_pool = ['TOTEXTTAU', 'TOTSCATAU', 'TOTANGSTR']
    rad_pool = ['ALBEDO']
    slv_pool = ['TO3', 'TQV', 'PS']
    asm_pool = ['PHIS']

    aer_var = clearskypy.extractor.extract_dataset(lats, lons, aerpath, aer_pool, datavecs)
    rad_var = clearskypy.extractor.extract_dataset(lats, lons, radpath, rad_pool, datavecs)
    slv_var = clearskypy.extractor.extract_dataset(lats, lons, slvpath, slv_pool, datavecs)
    asm_var = clearskypy.extractor.extract_dataset(lats, lons, asmpath, asm_pool, datavecs, interpolate=False)

    tot_aer_ext = aer_var[1]
    AOD_550 = aer_var[0]
    tot_angst = aer_var[2]
    ozone = slv_var[0]
    albedo = rad_var[0]
    water_vapour = slv_var[1]
    pressure = slv_var[2]
    phis = asm_var[0]

    water_vapour = water_vapour * 0.1
    ozone = ozone * 0.001
    h = phis / 9.80665
    h0 = elevs
    Ha = 2100
    scale_height = np.exp((h0 - h) / Ha)
    AOD_550 = AOD_550 * scale_height.T
    water_vapour = water_vapour * scale_height.T
    tot_angst[tot_angst < 0] = 0
    return [tot_aer_ext, AOD_550, tot_angst, ozone, albedo, water_vapour, pressure]


def test_extract_dataset_list():
    """
    Another method to extract data from a list of data set.

    :return: same as extract_dataset
    """
    lats = np.random.random(2) * 90
    lons = np.random.random(2) * 360 - 180
    date = ['2019-01-01T12:30:00', '2019-01-04T11:45:00', '2019-01-05T01:30:00']
    datapathlist = ['path to dataset1', 'path to dataset2']
    rad_pool = ['ALBEDO']
    test = clearskypy.extractor.extract_dataset_list(lats, lons, datapathlist, rad_pool, date, interpolate=True)
    return test


def data_eext_builder(number_sites, size_zenith):
    esc = 1366.1
    ndd = np.linspace(0, 1, size_zenith).reshape([size_zenith, 1])  # dayth from 1.1 per year
    beta = (2 * np.pi * ndd) / 365
    Eext = esc * (1.00011 + 0.034221 * np.cos(beta) + 0.00128 * np.sin(beta) + 0.000719 * np.cos(
        2 * beta) + 0.000077 * np.sin(
        2 * beta))
    Eext = np.tile(Eext, number_sites)
    return Eext


def example_for_rest2(station_number, allgrid=False, elevs=1):
    datadir = './MERRA2_data/'
    dataset_list = [os.listdir(datadir)]

    aerpath = datadir + dataset_list[0][0]
    slvpath = datadir + dataset_list[0][4]
    radpath = datadir + dataset_list[0][1]
    asmpath = datadir + dataset_list[0][2]

    dataset = xr.open_dataset(aerpath)
    time = dataset['time'].data
    time = np.unique(time)
    timesize = time.size
    '''
    All grid will caculate all data points from data set, if the dataset is globla, that means over 200,000 points
    random points cost much less than all grid
    '''
    if allgrid:

        lons_grid = dataset['lon'].data
        lats_grid = dataset['lat'].data
        lons = np.empty([lons_grid.size * lats_grid.size, ])
        lats = np.empty([lons_grid.size * lats_grid.size, ])
        zenith = np.empty([timesize, lons_grid.size * lats_grid.size])
        for index_lats in range(lats_grid.size):
            for index_lons in range(lons_grid.size):
                lons[index_lons * (index_lats - 1) + index_lons] = lons_grid[index_lons]
                lats[index_lons * (index_lats - 1) + index_lons] = lats_grid[index_lats]
                solpos = pvlib.solarposition.get_solarposition(time, lats_grid[index_lats], lons_grid[index_lons])
                zenith[:, index_lons * (index_lats - 1) + index_lons] = np.array(solpos['apparent_zenith']).reshape(
                    [timesize, 1])[:, 0]

    else:
        lats = np.random.random(station_number) * 90
        lons = np.random.random(station_number) * 360 - 180

        zenith = np.empty([timesize, station_number])
        for index_station in range(station_number):
            solpos = pvlib.solarposition.get_solarposition(time, lats[index_station], lons[index_station])
            zenith[:, index_station] = np.array(solpos['apparent_zenith']).reshape(
                [timesize, 1])[:, 0]

    'extract data from dataset by extractor'
    merra2_data_for_rest2 = test_extract_MERRA2(lats, lons, time, elevs, aerpath, radpath, slvpath, asmpath)

    '''Generate some additional data randmly'''

    Eext = data_eext_builder(station_number, timesize)
    nitrogen_dioxide = np.tile(np.linspace(0.0002, 0.0003, timesize).reshape([timesize, 1]), station_number)

    '''
    pvlib return zenith as degree but rest2 need radians
    '''
    zenith = np.deg2rad(zenith)  #

    [ghi, dni, dhi] = clearskypy.model.clear_sky_reset2(zenith, Eext, merra2_data_for_rest2[6],
                                                        merra2_data_for_rest2[5], merra2_data_for_rest2[3],
                                                        nitrogen_dioxide, merra2_data_for_rest2[1],
                                                        merra2_data_for_rest2[2], merra2_data_for_rest2[4])

    return [ghi, dni, dhi]


if __name__ == '__main__':
    print(example_for_rest2(10))
