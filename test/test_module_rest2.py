import clearskypy
import numpy as np


def data_eext_builder(number_sites, size_zenith):
    esc = 1366.1
    ndd = np.linspace(0, 1, size_zenith).reshape([size_zenith, 1])  # dayth from 1.1 per year
    beta = (2 * np.pi * ndd) / 365
    Eext = esc * (1.00011 + 0.034221 * np.cos(beta) + 0.00128 * np.sin(beta) + 0.000719 * np.cos(
        2 * beta) + 0.000077 * np.sin(
        2 * beta))
    Eext = np.tile(Eext, number_sites)
    return Eext


def model_test():
    number_sites = 1
    size_zenith = 181
    zenith_angle = np.tile(np.deg2rad(np.arange(-90, 91).reshape([size_zenith, 1])), number_sites)
    pressure = np.tile(np.linspace(960, 1012, size_zenith).reshape([size_zenith, 1]), number_sites)
    water_vapour = np.tile(np.linspace(7, 2, size_zenith).reshape([size_zenith, 1]), number_sites)
    ozone = np.tile(np.linspace(0.02, 0.06, size_zenith).reshape([size_zenith, 1]), number_sites)
    nitrogen_dioxide = np.tile(np.linspace(0.0002, 0.0003, size_zenith).reshape([size_zenith, 1]), number_sites)
    AOD550 = np.tile(np.linspace(0.2, 0.4, size_zenith).reshape([size_zenith, 1]), number_sites)
    Angstrom_exponent = np.tile(np.linspace(1.1, 1.3, size_zenith).reshape([size_zenith, 1]), number_sites)
    surface_albedo = np.tile(np.linspace(0.3, 0.35, size_zenith).reshape([size_zenith, 1]), number_sites)
    Eext = data_eext_builder(number_sites, size_zenith)
    [ghi, dni, dhi] = clearskypy.model.clear_sky_reset2(zenith_angle, Eext, pressure, water_vapour, ozone,
                                                         nitrogen_dioxide, AOD550, Angstrom_exponent, surface_albedo)

    return 1


if __name__ == '__main__':
    model_test()
