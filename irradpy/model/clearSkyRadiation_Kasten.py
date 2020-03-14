### 17-22 Kasten 1984

###References:
# Ineichen, P., & Perez, R. (2002). A new airmass independent formulation for the Linke turbidity coefficient. Solar Energy, 73(3), 151-157.

###Inputs:
#  Esc=1367.13   [Wm-2]      (Solar constant)
#  sza           [radians]   (zenith_angle)
#  altitude      [m]         (location's altitude)
#  TL2           [double]    (Linke Turbidity at air mass = 2)

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from .solarGeometry import time2dayth, time2yearth

class ClearSkyKasten:
    def __init__(self, time, elev):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.elev = elev

    def Kasten(self, sza, TL2):
        # Extraterrestrial irradiance
        Esc = 1367.13
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Air mass corrected for elevation
        AM = 1 / (np.cos(sza) + 0.50572 * (np.power(6.07995 + (np.pi / 2 - sza) * 180 / np.pi, -1.6364)))

        # coefficients based on altitude
        fh1 = np.exp(-1 * self.elev / 8000)

        fh2 = np.exp(-1 * self.elev / 1250)

        # global horizontal irradiance & QC
        # Eghkasten = 0.84*Eext*cos(sza)*exp(-0.027*AM*(fh1+fh2*(TL2-1)))
        Eghkasten = [0] * len(TL2)
        for i in range(len(TL2)):
            temp = (0.84 * Eext * np.cos(sza) * np.exp(-0.027 * AM * (fh1+fh2 * (TL2[i]-1))))
            # Quality control
            lower = 0
            temp[temp < lower] = 0
            Eghkasten[i] = temp


        # Eghkasten_name = c('Eghkasten_R', 'Eghkasten_D', 'Eghkasten_I', 'Eghkasten_Gu', 'Eghkasten_M', 'Eghkasten_Gr')
        return Eghkasten
