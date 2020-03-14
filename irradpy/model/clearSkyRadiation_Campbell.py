### 12-Campbell 1998

###References:
# Campbell, G. S., & Norman, J. M. (1998). An introduction to environmental biophysics. An introduction to environmental biophysics., (Ed. 2).

###Inputs:
#  Esc=1366.1   [Wm-2]      (Solar constant)
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

class ClearSkyCampbell:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def Campbell(self, sza):
        # Extraterrestrial irradiance
        Esc = 1366.1
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear

        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Air mass
        am = self.press / (1013 * np.cos(sza))

        # Direct normal irradiance
        tau0 = 0.7  # Author stated 0.7 to be typical of clear sky conditions.
        EbnCampbell = Eext * np.power(tau0, am)
        # diffuse horizontal irradiance
        EdhCampbell = 0.3 * Eext * np.cos(sza) * (1 - np.power(tau0, am))
        # global horizontal irradiance
        EghCampbell = EbnCampbell * np.cos(sza) + EdhCampbell

        # Quality control
        lower = 0
        EbnCampbell[EbnCampbell < lower] = 0
        EdhCampbell[EdhCampbell < lower] = 0
        EghCampbell[EghCampbell < lower] = 0
        return [EbnCampbell, EdhCampbell, EghCampbell]
