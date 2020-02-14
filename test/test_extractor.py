import numpy as np
import irradpy


def test_extract_MERRA2(lats, lons, datavecs, elevs):
    """
    extract data from merra2

    lats lons elevs need to be numpy.ndarray ,same size ,match every station
    """

    # safety check
    if np.size(lats, 0) != np.size(lons, 0) and np.size(lons, 0) != np.size(elevs, 0):
        print('ERROR: lats , lons , elevs dimention not match')
        return -1

    aer_pool = ['TOTEXTTAU', 'TOTSCATAU', 'TOTANGSTR']
    rad_pool = ['ALBEDO']
    slv_pool = ['TO3', 'TQV', 'PS']
    asm_pool = ['PHIS']

    aerpath = 'path to aer dataset'
    radpath = 'path to rad dataset'
    slvpath = 'path to slv dataset'
    asmpath = 'path to asm dataset'

    aer_var = irradpy.extractor.extract_dataset(lats, lons, aerpath, aer_pool, datavecs)
    rad_var = irradpy.extractor.extract_dataset(lats, lons, radpath, rad_pool, datavecs)
    slv_var = irradpy.extractor.extract_dataset(lats, lons, slvpath, slv_pool, datavecs)
    asm_var = irradpy.extractor.extract_dataset(lats, lons, asmpath, asm_pool, datavecs, interpolate=False)

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
    lats = np.random.random(2) * 90
    lons = np.random.random(2) * 360 - 180
    date = ['2019-01-01T12:30:00', '2019-01-04T11:45:00', '2019-01-05T01:30:00']
    datapathlist = ['path to dataset1', 'path to dataset2']
    rad_pool = ['ALBEDO']
    test = irradpy.extractor.extract_dataset_list(lats, lons, datapathlist, rad_pool, date, interpolate=True)
    print(test)


if __name__ == '__main__':
    test_extract_dataset_list()
