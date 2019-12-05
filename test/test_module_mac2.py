import clearskypy
import numpy as np


def model_test():
    size_sza = 181
    sza = np.arange(-90, 91).reshape([size_sza, 1])
    Earth_radius = np.linspace(1, 1.1, size_sza).reshape([size_sza, 1])
    pressure = np.linspace(960, 1012, size_sza).reshape([size_sza, 1])
    wv = np.linspace(7, 2, size_sza).reshape([size_sza, 1])
    ang_beta = np.linspace(1.1, 1.3, size_sza).reshape([size_sza, 1])
    ang_alpha = np.linspace(1, 1.1, size_sza).reshape([size_sza, 1])
    albedo = np.linspace(0.3, 0.35, size_sza).reshape([size_sza, 1])
    components = 3
    output = clearskypy.model.clear_sky_mac2(sza, Earth_radius, pressure, wv, ang_beta, ang_alpha, albedo, components)
    return output


if __name__ == '__main__':
    print(model_test())
