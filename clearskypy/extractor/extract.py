import xarray as xr
import numpy as np


def extract_dataset(lats, lons, dataset_path, variables, datevecs, interpolate=True):
    """
    extract variables from dataset

    interpolate default to be TRUE Warning:if dataset coordinate less than datevecs dimention, interpolate will
    increase the coordinate of dataset and cause error !!!


    only for extract data from single dataset

     """
    dataset = xr.open_dataset(dataset_path).sel(lat=lats, lon=lons, method='nearest')[
        variables]  # ectract nearest stations point for given lats and lons
    if dataset['time'].size > 1:
        if interpolate:
            dataset_interpolation = dataset.interp(time=datevecs)  # use datevecs to interpolate
        else:
            dataset_interpolation = dataset
    else:
        dataset_interpolation = dataset

    lons_fixed = dataset_interpolation['lon'].data  # station lons
    lats_fixed = dataset_interpolation['lat'].data  # station_lats
    var = []
    for index_variables in variables:
        if interpolate:
            station_data = np.empty([len(datevecs), len(lats_fixed)], dtype=float)
            for index_station in range(len(lons_fixed)):
                station_data[:, index_station] = np.array([dataset_interpolation[index_variables].sel(
                    lat=lats_fixed[index_station], lon=lons_fixed[index_station]).data]).T[:, 0]
        else:
            station_data = np.empty([len(lons_fixed), 1], dtype=float)  # for phis
            for index_station in range(len(lons_fixed)):
                station_data[index_station, :] = np.array([dataset_interpolation[index_variables].sel(
                    lat=lats_fixed[index_station], lon=lons_fixed[index_station]).data])[:, 0]
        var.append(station_data)

    return var


def extract_MERRA2(lats, lons, datavecs, elevs=1):
    """extract data from merra2 """

    # safety check
    if np.size(lats, 0) != np.size(lons, 0):
        print('ERROR: lats and lons dimention not match')
        return -1


    aer_pool = ['TOTEXTTAU', 'TOTSCATAU', 'TOTANGSTR']
    rad_pool = ['ALBEDO']
    slv_pool = ['TO3', 'TQV', 'PS']
    asm_pool = ['PHIS']

    aerpath = 'dir_to_aer_dataset'
    radpath = 'dir_to_rad_dataset'
    slvpath = 'dir_to_slv_dataset'
    asmpath = 'dir_to_asm_dataset'

    aer_var = extract_dataset(lats, lons, aerpath, aer_pool, datavecs)
    rad_var = extract_dataset(lats, lons, radpath, rad_pool, datavecs)
    slv_var = extract_dataset(lats, lons, slvpath, slv_pool, datavecs)
    asm_var = extract_dataset(lats, lons, asmpath, asm_pool, datavecs, interpolate=False)

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


if __name__ == '__main__':
    '''test extract script'''
    lats = np.random.random(2) * 90
    lons = np.random.random(2) * 360 - 180
    date = ['2018-01-01T00:30:00', '2018-01-01T01:45:00', '2018-01-01T02:30:00']
    var = extract_MERRA2(lats, lons, date)
