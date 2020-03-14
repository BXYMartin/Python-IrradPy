### 58-Bashahu 1994

###References:
# Bashahu, M., & Laplaze, D. (1994). An atmospheric model for computing solar radiation. Renewable energy, 4(4), 455-458.

###Inputs:
#  Esc=1367     [Wm-2]             (Solar constant)
#  sza          [radians]          (zenith_angle)
#  press        [mb]               (local barometric)
#  ang_alpha    [dimensionless]    (Angstrom_exponent, also known as alpha)
#  ang_beta     [dimensionless]    (Angstrom turbidity coefficient)
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

class ClearSkyBashahu:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def Bashahu(self, sza, wv, ang_alpha, ang_beta):
        # Extraterrestrial irradiance
        Esc = 1367
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Air Mass for Atwater
        am = 1 / (cos(sza) + 0.15 * power((pi / 2 - sza) / pi * 180 + 3.885, -1.253))
        ama = am * self.press / 1013.25

        # direct beam radiation
        Td = 5.228 / ama * (exp(-0.0002254 * ama) - exp(-0.1409 * ama)) * exp(
            -ama * ang_beta / power(0.6489, ang_alpha)) + 0.00165 * ama + 0.2022 * (
                         1 - ama * ang_beta / power(2.875, ang_alpha))
        Ta = 0.1055 + 0.07053 * log10(ama * wv + 0.07854) * exp(-ama * ang_beta / power(1.519, ang_alpha))
        EbnBashahu = Eext * (Td - Ta)

        # diffuse horizontal radiation
        EdhBashahu = 0.5 * Eext * (1 - Td) * power(cos(sza), 4 / 3)

        # Global horizontal irradiance
        EghBashahu = EbnBashahu * cos(sza) + EdhBashahu

        # Quality control
        lower = 0
        EbnBashahu[EbnBashahu < lower] = 0
        EdhBashahu[EdhBashahu < lower] = 0
        EghBashahu[EghBashahu < lower] = 0
        return [EbnBashahu, EdhBashahu, EghBashahu]
