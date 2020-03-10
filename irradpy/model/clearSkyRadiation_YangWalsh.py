### 09-Yang & Walsh  2014

###References:
#Yang, D., Walsh, W. M., & Jirutitijaroen, P. (2014). Estimation and applications of clear sky global horizontal irradiance at the equator. Journal of Solar Energy Engineering, 136(3), 034505.

###Inputs:
#  Esc=1362   [Wm-2]     (Solar constant)
#  sza        [radians]  (zenith_angle)

###Outputs:
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from .solarGeometry import time2dayth, time2yearth

class ClearSkyYangWalsh:
    def __init__(self, time):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)

    def YangWalsh(self, sza):
        # Extraterrestrial irradiance
        Esc=1362
        totaldayofyear=366-np.ceil(self.yearth/4-np.trunc(self.yearth/4))
        B=(self.dayth-1)*2*np.pi/totaldayofyear
        Eext=Esc*(1.00011+0.034221*np.cos(B)+0.00128*np.sin(B)+0.000719*np.cos(2*B)+0.000077*np.sin(2*B))

        # Global horizontal irradiance
        Eghyangwalsh=0.8298*Eext*np.power(np.cos(sza), 1.3585)*np.exp(-0.00135*(np.pi/2-sza)/np.pi*180)

        # Quality control
        lower=0
        Eghschulze[Eghyangwalsh<lower]=0
        return Eghyangwalsh

