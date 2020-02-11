import numpy as np
import os
import warnings
from ..extractor.extract import extract_dataset_list, extract_dataset, extract_for_MERRA2
from .solarGeometry import *
import pandas as pd

class ClearSkyMAC2:

    def __init__(self, lat: np.ndarray, lon: np.ndarray, elev, time, datadir, pandas=True):
        if lat.shape != lon.shape:
            raise Exception('lat and lon not match...')
        if np.max(np.abs(lat)) > 90:
            raise Exception('90<= lattitude <=90, reset your latitude')
        if np.max(np.abs(lon)) > 180:
            raise Exception('-180<= lontitude <=180, reset your lontitude')

        station_num = np.size(lat)
        self.lat = lat.reshape([station_num, ])
        self.lon = lon.reshape([station_num, ])
        self.elev = elev.reshape([station_num, 1])
        self.time = time
        self.datadir = datadir
        self.pandas_output = pandas

    def clear_sky_MAC2(self, sza, Angstrom_exponent, pressure, wv, AOD550, albedo, Eext, components):
        """
        clear_sky_model MAC2 1982

        Every Variable Need to be np.ndarry. np.matrix will cause fatal error

        ASSUMPTION: all data is in 1-min resolution and all vectors(size: n*1)
        perfectly match each other in terms of time stamps.

        sza   = Zenith angle in degrees. Corresponding to all inputs.
        Earth_radius = Earth heliocentric radius(AU). Eext=Esc*Earth_radius^-2.
        pressure = Local barometric pressure in [mb].
        wv = Total precipitable water vapour in [cm].
        ang_beta = Angstrom turbidity coefficient ¦Â.
        ang_alpha = Angstrom exponent ¦Á.
        albedo = Ground albedo.

        components = 1, output = Edn
        components = 2, output = [Edn, Edh]
        components = 3, output = [Egh, Edn, Edh]

        matlab version coded by Xixi Sun according to Davies and Mckay 1982 <Estimating solar irradiance and components>
        """
        warnings.filterwarnings("ignore")

        ang_alpha = Angstrom_exponent
        ang_beta = AOD550 / (np.power(0.55, -ang_alpha))

        sza[sza > 90] = np.nan
        datapoints = np.size(sza, 0) * np.size(sza, 1)
        # Extraterrestrial irradiance

        eext = Eext
        # Air Mass
        amm = 35 / np.power((1224 * np.power(np.cos(np.deg2rad(sza)), 2) + 1), 0.5)
        amm[amm < 0] = 0

        # Ozone Transmittance
        ozone = 0.35  # Davies and Mckay 1982 set ozone a fixed value of 3.5mm
        xo = amm * (ozone * 10)  # Davies and Mckay 1982 ozone unit is mm, here in the code unit is cm
        ao = ((0.1082 * xo) / (np.power((1 + 13.86 * xo), 0.805))) + (
                (0.00658 * xo) / (1 + np.power((10.36 * xo), 3))) + (
                     0.002118 * xo / (1 + 0.0042 * xo + 3.23e-6 * np.power(xo, 2)))
        to = 1 - ao

        # Rayleigh Transmittance  (linear interpolation based on  Table 2 in Davies and Mckay 1982 )
        tr = amm
        ammbasis = amm.reshape((datapoints, 1), order='F')
        amms = np.array([0.5, 1, 1.2, 1.4, 1.6, 1.8, 2.0, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6, 10, 30]).reshape(16, 1)
        t_rs = np.array(
            [.9385, .8973, .8830, .8696, .8572, .8455, .8344, .7872, .7673, .7493, .7328, .7177, .7037, .6907, .6108,
             .4364]).reshape(16, 1)
        tr = np.interp(ammbasis[:, 0], amms[:, 0], t_rs[:, 0])
        tr = tr.reshape(np.size(sza, 0), np.size(sza, 1), order='F')

        # Aerosols Transmittance, borrowed from BH 1981
        t_a = ang_beta * (np.power(0.38, -ang_alpha) * 0.2758 + np.power(0.5, -ang_alpha) * 0.35)
        TA = np.exp(-t_a * amm)

        # Water Vapor Transmittance
        xw = amm * wv * 10 * np.power((pressure / 1013.25), 0.75)
        aw = 0.29 * xw / (np.power((1 + 14.15 * xw), 0.635) + 0.5925 * xw)
        # Forward Scatter
        szajiao = sza.reshape((datapoints, 1), order='F')
        szajiaos = np.array([0, 25.8, 36.9, 45.6, 53.1, 60.0, 66.4, 72.5, 78.5, 90]).reshape(10, 1)
        fs = np.array([.92, .91, .89, .86, .83, .78, .71, .67, .60, .60]).reshape(10, 1)
        f = np.interp(szajiao[:, 0], szajiaos[:, 0], fs[:, 0])
        f = f.reshape(np.size(sza, 0), np.size(sza, 1), order='F')

        lower = 0
        if components == 1:
            # Direct normal irradiance
            EbnMAC2 = eext * (to * tr - aw) * TA
            EbnMAC2[EbnMAC2 < lower] = lower  # Quality control

            output = EbnMAC2
        elif components == 2:
            # Direct normal irradiance
            EbnMAC2 = eext * (to * tr - aw) * TA
            EbnMAC2[EbnMAC2 < lower] = lower  # Quality control

            # Diffuse horizontal irradiance
            # diffuse components from Rayleigh scatter
            DR = eext * np.cos(np.deg2rad(sza)) * to * (1 - tr) / 2
            # diffuse components from scattering by aerosol
            DA = eext * np.cos(np.deg2rad(sza)) * (to * tr - aw) * (
                    1 - TA) * 0.75 * f  # w0 = 0.75 according to Table5 in Davies and Mckay 1982
            # diffuse horizontal irradiance
            Taaa = np.power(0.95,
                            1.66)  # Taaa is TA determined at amm=1.66, k=0.95 according to Table5 in Davies and Mckay 1982
            poub = 0.0685 + (1 - Taaa) * 0.75 * (
                    1 - 0.83)  # f' is f determined at amm=1.66, f' equals  0.83, estimate theta when amm=1.66,
            # theta near 53 degree
            EdhMAC2 = poub * albedo * (EbnMAC2 * np.cos(np.deg2rad(sza)) + DR + DA) / (1 - poub * albedo) + DR + DA
            EdhMAC2[EdhMAC2 < lower] = lower  # Quality control

            output = [EbnMAC2, EdhMAC2]
        else:
            # Direct normal irradiance
            EbnMAC2 = eext * (to * tr - aw) * TA
            EbnMAC2[EbnMAC2 < lower] = lower  # Quality control

            # Diffuse horizontal irradiance
            # diffuse components from Rayleigh scatter
            DR = eext * np.cos(np.deg2rad(sza)) * to * (1 - tr) / 2
            # diffuse components from scattering by aerosol
            DA = eext * np.cos(np.deg2rad(sza)) * (to * tr - aw) * (
                    1 - TA) * 0.75 * f  # w0 = 0.75 according to Table5 in Davies and Mckay 1982
            # diffuse horizontal irradiance
            Taaa = np.power(0.95,
                            1.66)  # Taaa is TA determined at amm=1.66, k=0.95 according to Table5 in Davies and Mckay 1982
            poub = 0.0685 + (1 - Taaa) * 0.75 * (
                    1 - 0.83)  # f' is f determined at amm=1.66, f' equals  0.83, estimate theta when amm=1.66,
            # theta near 53 degree
            EdhMAC2 = poub * albedo * (EbnMAC2 * np.cos(np.deg2rad(sza)) + DR + DA) / (1 - poub * albedo) + DR + DA
            EdhMAC2[EdhMAC2 < lower] = lower  # Quality control

            # Global horizontal irradiance
            EghMAC2 = (EbnMAC2 * np.cos(np.deg2rad(sza)) + DR + DA) / (1 - poub * albedo)
            EghMAC2[EghMAC2 < lower] = lower  # Quality control

            EghMAC2[np.isnan(EghMAC2)] = 0
            EbnMAC2[np.isnan(EbnMAC2)] = 0
            EdhMAC2[np.isnan(EdhMAC2)] = 0

            output = [EghMAC2, EbnMAC2, EdhMAC2]

        return output

    def MAC2(self, components=3):
        """
        run mac2 model with arguments downloaded in data set

        components = 1, output = Edn
        components = 2, output = [Edn, Edh]
        components = 3, output = [Egh, Edn, Edh]

        matlab version coded by Xixi Sun according to Davies and Mckay 1982 <Estimating solar irradiance and components>

        :return: [Egh, Edn, Edh]
        """

        same_flag = 1

        for i in range(len(self.time) - 1):
            if self.time[i + 1].shape == self.time[0].shape:
                if (self.time[i + 1] != self.time[0]).any():
                    same_flag = 0
            else:
                same_flag = 0

        if same_flag == 1:

            zenith_angle = latlon2solarzenith(self.lat, self.lon, self.time.T)
            Eext = data_eext_builder(self.time.T)

            [tot_aer_ext, AOD550, Angstrom_exponent, ozone, surface_albedo, water_vapour, pressure,
             nitrogen_dioxide] = extract_for_MERRA2(self.lat, self.lon, self.time.T, self.elev, self.datadir)

            [Egh, Edn, Edh] = self.clear_sky_MAC2(zenith_angle, Angstrom_exponent, pressure, water_vapour, AOD550,
                                                  surface_albedo, Eext, components)
            if self.pandas_output:
                col_index = ['GHI', 'DNI', 'DIF']
                station_data_list = []
                for index in range(len(self.time)):
                    time_temp = (self.time[index]).reshape(self.time[index].size, 1)
                    row_index = time_temp[:, 0]
                    station_data = pd.DataFrame(np.hstack((Egh[:, index][:, np.newaxis], Edn[:, index][:, np.newaxis], Edh[:, index][:, np.newaxis])), index=row_index, columns=col_index)
                    station_data_list.append(station_data)

                return station_data_list

            else:
                Egh = Egh.T
                Edn = Edn.T
                Edh = Edh.T
                return [Egh, Edn, Edh]
        else:
            Egh = []
            Edn = []
            Edh = []
            col_index = ['GHI', 'DNI', 'DIF']
            station_data_list = []

            for index in range(len(self.time)):
                time_temp = (self.time[index]).reshape(self.time[index].size, 1)
                zenith_angle = latlon2solarzenith(self.lat[index], self.lon[index], time_temp)
                Eext = data_eext_builder(time_temp)
                row_index = time_temp[:, 0]
                [tot_aer_ext, AOD550, Angstrom_exponent, ozone, surface_albedo, water_vapour, pressure,
                 nitrogen_dioxide] = extract_for_MERRA2(self.lat[index], self.lon[index], time_temp,
                                                        self.elev[index], self.datadir)
                [Egh_i, Edn_i, Edh_i] = self.clear_sky_MAC2(zenith_angle, Angstrom_exponent, pressure,
                                                            water_vapour, AOD550, surface_albedo, Eext,
                                                            components)
                if self.pandas_output:
                    station_data = pd.DataFrame(np.hstack((Egh_i, Edn_i, Edh_i)), index=row_index, columns=col_index)
                    station_data_list.append(station_data)
                else:
                    Egh.append(Egh_i)
                    Edn.append(Edn_i)
                    Edh.append(Edh_i)
            if self.pandas_output:
                return station_data_list
            else:
                return [Egh, Edn, Edh]
