### 41-46 Ineichen & Perez 2002

###References:
# Ineichen, P., & Perez, R. (2002). A new airmass independent formulation for the Linke turbidity coefficient. Solar Energy, 73(3), 151-157.

###Inputs:
#  Esc=1367   [Wm-2]      (Solar constant)
#  sza        [radians]   (zenith_angle)
#  altitude   [m]         (location's altitude)
#  TL2        [double]    (Linke Turbidity at air mass = 2)

###Outputs:
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from .solarGeometry import time2dayth, time2yearth

class ClearSkyIneichenPerez:
    def __init__(self, time, elev):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.elev = elev

    def IneichenPerez(self, sza, TL2):
        # Extraterrestrial irradiance
        Esc = 1367
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Air mass corrected for elevation
        AM = 1 / (np.cos(sza) + 0.50572 * (np.power(6.07995 + (np.pi / 2 - sza) * 180 / np.pi, -1.6364)))

        # coefficients based on altitude
        fh1 = np.exp(-self.elev / 8000)

        fh2 = np.exp(-self.elev / 1250)
        cg1 = (5.09e-5) * (self.elev) + 0.868
        cg2 = (3.92e-5) * (self.elev) + 0.0387

        # global horizontal irradiance & QC
        # Eghip = cg1*Eext*cos(sza)*exp(-cg2*AM*(fh1+fh2*(TL2-1)))

        # Eghip_name = c('Eghip_R', 'Eghip_D', 'Eghip_I', 'Eghip_Gu', 'Eghip_M', 'Eghip_Gr')
        Eghip = [0] * len(TL2)
        for i in range(len(TL2)):
            Eghip_temp = (cg1 * Eext * np.cos(sza) * np.exp(-cg2 * AM * (fh1 + fh2 * (TL2[i] - 1))))
            # Quality control
            lower = 0
            Eghip_temp[Eghip_temp < lower] = 0
            Eghip[i] = Eghip_temp
        return Eghip