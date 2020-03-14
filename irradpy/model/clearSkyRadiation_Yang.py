### 60-Yang 2005

###References:
# Yang, K., & Koike, T. (2005). A general model to estimate hourly and daily solar radiation for hydrological studies. Water Resources Research, 41(10).

###Inputs:
#  Esc=1361.1   [Wm-2]             (Solar constant)
#  sza          [radians]          (zenith_angle)
#  press        [mb]               (local barometric)
#  ang_beta     [dimensionless]    (Angstrom turbidity coefficient)
#  ozone        [atm.cm]           (total columnar amount of ozone)
#  wv           [atm.cm]           (total columnar amount of water vapour)

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from numpy import sin, cos, log, log10, power, pi, exp
from .solarGeometry import time2dayth, time2yearth

class ClearSkyYang:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def Yang(self, sza, wv, ozone, ang_beta):
        # Extraterrestrial irradiance
        Esc = 1361.1
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        am = 1 / (cos(sza) + 0.15 * power(57.296 * (pi / 2 - sza) / pi * 180 + 3.885, -1.253))
        ama = am * self.press / 1013.25

        # the broadband radiative transmittance due to permanent gas absorption
        Tg = exp(-0.0117 * power(ama, 0.3139))

        # the broadband radiative transmittance due to Rayleigh scattering
        Tr = exp(-0.008735 * ama * power(0.547 + 0.014 * ama - 0.00038 * ama * ama + 4.6e-6 * power(ama, 3), -4.08))

        # the broadband radiative transmittance due to water vapor absorption
        Tw = (0.909 - 0.036 * log(wv * am))
        Tw[Tw > 1] = 1

        # the broadband radiative transmittance due to Ozone absorption
        Toz = exp(-0.0365 * power(am * ozone, 0.7136))

        # the broadband radiative transmittance due to Aerosol extinction
        Ta = exp(-am * ang_beta * power(0.6777 + 0.1464 * (am * ang_beta) - 0.00626 * power(am * ang_beta, 2), -1.3))

        # the broadband solar beam radiative transmittance
        Tbclear = Toz * Tw * Tg * Tr * Ta - 0.013
        Tbclear[Tbclear < 0] = 0

        # the broadband solar diffuse radiative transmittance
        Tdclear = 0.5 * (Toz * Tg * Tw * (1 - Ta * Tr) + 0.013)

        # direct beam irradiance
        EbnYang = Eext * Tbclear
        # diffuse horizontal irradiance
        EdhYang = Eext * cos(sza) * Tdclear
        # global horizontal irradiance
        EghYang = EbnYang * cos(sza) + EdhYang

        # Quality control
        lower = 0
        EbnYang[EbnYang < lower] = 0
        EdhYang[EdhYang < lower] = 0
        EghYang[EghYang < lower] = 0
        return [EbnYang, EdhYang, EghYang]