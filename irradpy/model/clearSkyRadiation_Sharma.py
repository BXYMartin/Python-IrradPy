### 07-Sharma 1965

###References:
#Sharma, M. R., & Pal, R. S. (1965). Interrelationships between total, direct, and diffuse solar radiation in the tropics. Solar Energy, 9(4), 183-192.
#Badescu, V., Gueymard, C. A., Cheval, S., Oprea, C., Baciu, M., Dumitrescu, A., ... & Rada, C. (2013). Accuracy analysis for fifty-four clear-sky solar radiation models using routine hourly global irradiance measurements in Romania. Renewable Energy, 55, 85-103.

###Inputs:
#  Esc=1366.1   [Wm-2]     (Solar constant)
#  sza          [radians]  (zenith_angle)

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from .solarGeometry import time2yearth

class ClearSkySharma:
    def __init__(self, time):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)

    def Sharma(self, sza):
        # Extraterrestrial irradiance
        Esc=1366.1
        totaldayofyear=366-np.ceil(self.yearth/4-np.trunc(self.yearth/4))
        B=(self.dayth-1)*2*np.pi/totaldayofyear
        Eext=Esc*(1.00011+0.034221*np.cos(B)+0.00128*np.sin(B)+0.000719*np.cos(2*B)+0.000077*np.sin(2*B))

        # Direct normal irradiance
        EbnSharma=1.842*(Eext/2)*np.cos(sza)/(0.3135+np.cos(sza))
        # Global horizontal irradiance
        EghSharma=4.5*(Eext/(2*60))+1.071*EbnSharma*np.cos(sza)
        # Diffuse horizontal irradiance
        EdhSharma=EghSharma-EbnSharma*np.cos(sza)

        # Quality control
        lower=0
        EbnSharma[EbnSharma<lower]=0
        EdhSharma[EdhSharma<lower]=0
        EghSharma[EghSharma<lower]=0
        return [EbnSharma, EdhSharma, EghSharma]

