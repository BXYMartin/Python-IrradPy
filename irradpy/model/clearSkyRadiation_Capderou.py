### 16-Capderou 1987

###References:
# Capderou, M. (1987). Theoretical and experimental models solar atlas of Algeria (in French) Tome 1 and 2. Algeria: University Publications Office.
# Marif, Y., Chiba, Y., Belhadj, M. M., Zerrouki, M., & Benhammou, M. (2018). A clear sky irradiation assessment using a modified Algerian solar atlas model in Adrar city. Energy Reports, 4, 84-90.

###Inputs:
#  Esc=1367   [Wm-2]      (Solar constant)
#  sza        [radians]   (zenith_angle)
#  latitude   [double]    (location's latitude，-90~90)
#  altitude   [m]         (location's altitude)
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

class ClearSkyCapderou:
    def __init__(self, lat, time, press, elev):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press
        self.lat = lat
        self.elev = elev

    def Capderou(self, sza):
        # Extraterrestrial irradiance
        Esc = 1367
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (
                    1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(
                2 * B))

        # Air Mass
        mA = self.press / 1013.25 * 1 / (np.cos(sza) + 0.15 * (np.power(3.885 + (np.pi / 2 - sza) * 180 / np.pi, -1.253)))
        mAc = 1 / (np.cos(sza) + 0.15 * (np.power(3.885 + (np.pi / 2 - sza) * 180 / np.pi, -1.253)))

        Ahe = np.sin(360 / 365 * (self.dayth - 121))
        # Atmospheric turbidity caused by water vapor absorption
        T0 = 2.4 - 0.9 * np.sin(self.elev) + 0.1 * Ahe * (2 + np.sin(self.elev)) - 0.2 * self.elev / 1000 - (
                    1.22 + 0.14 * Ahe) * (1 - np.cos(sza))
        # Atmospheric turbidity corresponding to the molecular diffusion
        T1 = np.power(0.89, (self.elev / 1000))
        # Atmospheric turbidity relative to the aerosol diffusion coupled with a slight absorption
        T2 = (0.9 + 0.4 * Ahe) * np.power(0.63, (self.elev / 1000))
        # Atmospheric Linke turbidity factor
        Tlc = T0 + T1 + T2

        delta_rk = 1 / (9.4 + 0.9 * mA)
        # Direct normal irradiance
        EbnCapderou = Eext * np.exp(-Tlc * mAc * delta_rk)

        # Diffuse horizontal irradiance
        a = 1.1
        b = np.log(T1 + T2) - 2.8 + 1.02 * np.power((1 - np.cos(sza)), 2)
        EdhCapderou = Eext * np.exp(-1 + 1.06 * np.log(np.cos(sza)) + a - np.sqrt(a*a+b*b))
        # Global horizontal irradiance
        EghCapderou = EbnCapderou * np.cos(sza) + EdhCapderou

        # Quality control
        lower = 0
        EbnCapderou[EbnCapderou < lower] = 0
        EdhCapderou[EdhCapderou < lower] = 0
        EghCapderou[EghCapderou < lower] = 0
        return [EbnCapderou, EdhCapderou, EghCapderou]
