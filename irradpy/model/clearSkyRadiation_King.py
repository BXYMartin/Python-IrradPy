### 48-King 1979

###References:
# King, R., & Buckius, R. O. (1979). Direct solar transmittance for a clear sky. Solar Energy, 22(3), 297-301.
# Badescu, V., Gueymard, C. A., Cheval, S., Oprea, C., Baciu, M., Dumitrescu, A., ... & Rada, C. (2013). Accuracy analysis for fifty-four clear-sky solar radiation models using routine hourly global irradiance measurements in Romania. Renewable Energy, 55, 85-103.

###Inputs:
#  Esc=1366.1   [Wm-2]             (Solar constant)
#  sza          [radians]          (zenith_angle)
#  press        [mb]               (local barometric)
#  albedo       [double]           (surface/ground albedo)
#  wv           [atm.cm]           (total columnar amount of water vapour)
#  ang_beta     [dimensionless]    (Angstrom turbidity coefficient)

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from .solarGeometry import time2dayth, time2yearth

class ClearSkyKing:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def King(self, sza, wv, albedo, ang_beta):
        # Extraterrestrial irradiance
        Esc = 1366.1
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Air mass corrected for elevation
        amk = 1 / (np.cos(sza) + 0.15 * np.power((np.pi / 2 - sza) / np.pi * 180 + 3.885, -1.253))
        am = amk * self.press / 1013.25
        amb = amk * ang_beta
        a1 = 0.5

        Tscat = (5.228 / am) * (np.exp(-0.0002254 * am) - np.exp(-0.1409 * am)) * np.exp(
            -amb / np.power(0.6489, 1.3)) + 0.00165 * am + 0.2022 * (1 - amb / np.power(2.875, 1.3))

        Tabs = (0.1055 + 0.07053 * np.log10(amk * wv + 0.07854)) * np.exp(-amb / np.power(1.519, 1.3))

        # direct normal radiation
        EbnKing = Eext * (Tscat - Tabs)

        taul = 0.8336 + 0.17257 * ang_beta - 0.64595 * np.exp(-7.4296 * np.power(ang_beta, 1.5))
        Tml = np.exp(-am * taul)
        F1 = 2 * (1 + 2 * np.cos(sza) + (1 - 2 * np.cos(sza)) * Tml)
        F2 = (albedo - 1) * (a1 * taul - 4 * taul - 4) + 4 * albedo
        Tdif = 0.634 * (F1 / F2 - Tml)
        # diffuse horizontal radiation
        EdhKing = Eext * np.cos(sza) * Tdif

        # global radiation
        EghKing = EbnKing * np.cos(sza) + EdhKing

        # Quality control
        lower = 0
        EbnKing[EbnKing < lower] = 0
        EdhKing[EdhKing < lower] = 0
        EghKing[EghKing < lower] = 0
        return [EbnKing, EdhKing, EghKing]