### 11-Kumar 1997

###References:
# Gueymard, C. A. (2012). Clear-sky irradiance predictions for solar resource mapping and large-scale applications: Improved validation methodology and detailed performance analysis of 18 broadband radiative models. Solar Energy, 86(8), 2145-2169.

###Inputs:
#  Esc=1353   [Wm-2]      (Solar constant)
#  sza        [radians]   (zenith_angle)
#  press      [mb]        (local barometric)

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from .solarGeometry import time2dayth, time2yearth

class ClearSkyKumar:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def Kumar(self, sza):
        # Extraterrestrial irradiance
        Esc = 1353
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear

        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Absolute air mass
        mk = (np.power(1229 + np.power(614 * cos(sza), 2), 0.5) - 614 * np.cos(sza)) * self.press / 1013.25

        # Direct beam irradiance
        Ebnkumar = Eext * 0.56 * (np.exp(-0.65 * mk) + np.exp(-0.095 * mk))
        # Diffuse horizontal irradiance
        Edhkumar = (0.2710 * Eext - 0.294 * Ebnkumar) * np.cos(sza)

        # Global horizontal irradiance
        Eghkumar = Ebnkumar * np.cos(sza) + Edhkumar

        # Quality control
        lower = 0
        Ebnkumar[Ebnkumar < lower] = 0
        Edhkumar[Edhkumar < lower] = 0
        Eghkumar[Eghkumar < lower] = 0
        return [Ebnkumar, Edhkumar, Eghkumar]
