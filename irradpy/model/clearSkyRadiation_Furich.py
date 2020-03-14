### 13-Fu and Rich 1999 (Release v9.2 2008)

###References:
# Gueymard, C. A. (2012). Clear-sky irradiance predictions for solar resource mapping and large-scale applications: Improved validation methodology and detailed performance analysis of 18 broadband radiative models. Solar Energy, 86(8), 2145-2169.

###Inputs:
#  Esc=1367   [Wm-2]      (Solar constant)
#  sza        [radians]   (zenith_angle)
#  altitude   [m]         (location's altitude)

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from .solarGeometry import time2dayth, time2yearth

class ClearSkyFurich:
    def __init__(self, time, elev):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.elev = elev

    def Furich(self, sza):
        # Extraterrestrial irradiance
        Esc = 1367
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Air mass corrected for elevation
        mf = np.exp(-0.000118 * self.elev - 1.638e-9 * np.power(self.elev, 2)) / np.cos(sza)
        # a bulk atmospheric transmittance
        Tb = 0.5  # recommended value in Gueymard 2012

        # Direct beam irradiance
        Ebnfurich = Eext * np.power(Tb, mf)

        # Diffuse fraction of global normal irradiance
        P = 0.3  # recommended value in Gueymard 2012

        # Diffuse horizontal irradiance
        Edhfurich = Ebnfurich * (P / (1 - P)) * np.cos(sza)

        # Global horizontal irradiance
        Eghfurich = Ebnfurich * np.cos(sza) + Edhfurich

        # Quality control
        lower = 0
        Ebnfurich[Ebnfurich < lower] = 0
        Edhfurich[Edhfurich < lower] = 0
        Eghfurich[Eghfurich < lower] = 0
        return [Ebnfurich, Edhfurich, Eghfurich]
