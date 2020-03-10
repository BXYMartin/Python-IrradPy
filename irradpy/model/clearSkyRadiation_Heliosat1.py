### 23-28 Heliosat-1 1996

###References:
# Hammer, A., Heinemann, D., Hoyer, C., Kuhlemann, R., Lorenz, E., Müller, R., & Beyer, H. G. (2003). Solar energy assessment using remote sensing technologies. Remote Sensing of Environment, 86(3), 423-432.
# Gueymard, C. A. (2012). Clear-sky irradiance predictions for solar resource mapping and large-scale applications: Improved validation methodology and detailed performance analysis of 18 broadband radiative models. Solar Energy, 86(8), 2145-2169.

###Inputs:
#  Esc=1367   [Wm-2]      (Solar constant)
#  sza        [radians]   (zenith_angle)
#  press      [mb]        (local barometric)
#  TL2        [double]    (Linke Turbidity at air mass = 2)

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from .solarGeometry import time2dayth, time2yearth

class ClearSkyHeliosat1:
    def __init__(self, time, elev):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.elev = elev

    def Heliosat1(self, sza, TL2):
        # Extraterrestrial irradiance
        Esc = 1367.13
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Air mass corrected for elevation
        AM = 1 / (np.cos(sza) + 0.50572 * (np.power(6.07995 + (np.pi / 2 - sza) * 180 / np.pi, -1.6364)))

        ama = AM * self.press / 1013.25

        # the Rayleigh optical thickness
        theta = 1 / (6.62960 + 1.7513 * ama - 0.1202 * ama * ama + 0.0065 * np.power(ama, 3) - 0.00013 * np.power(ama, 4))
        for i in range(len(theta)):
            if ama[i] > 20:
                theta[i] = 1/(10.4 + 0.718 * ama[i])

        # direct beam irradiance
        # EbnHeliosat1=Eext*exp(-ama*theta*TL2*0.8662)
        # diffuse horizontal irradiance
        # EdhHeliosat1=Eext*(0.0065+(0.0646*TL2-0.045)*cos(sza)-(0.0327*TL2-0.014)*(cos(sza))^2)
        # global horizontal irradiance
        # EghHeliosat1=EbnHeliosat1*cos(sza)+EdhHeliosat1

        # EghHeliosat1_name = c('EghHeliosat1_R', 'EghHeliosat1_D', 'EghHeliosat1_I', 'EghHeliosat1_Gu', 'EghHeliosat1_M',
        #                       'EghHeliosat1_Gr')
        # EbnHeliosat1_name = c('EbnHeliosat1_R', 'EbnHeliosat1_D', 'EbnHeliosat1_I', 'EbnHeliosat1_Gu', 'EbnHeliosat1_M',
        #                       'EbnHeliosat1_Gr')
        # EdhHeliosat1_name = c('EdhHeliosat1_R', 'EdhHeliosat1_D', 'EdhHeliosat1_I', 'EdhHeliosat1_Gu', 'EdhHeliosat1_M',
        #                       'EdhHeliosat1_Gr')
        EghHeliosat1 = [0] * len(TL2)
        EdhHeliosat1 = [0] * len(TL2)
        EbnHeliosat1 = [0] * len(TL2)

        # calculate Ebn,Edh,Egh and quality control
        for i in range(len(TL2)):
            # direct beam irradiance
            EbnHeliosat1_temp = (Eext * np.exp(-1 * ama * theta * TL2[i] * 0.8662))
            EdhHeliosat1_temp = Eext * (0.0065+(0.0646 * TL2[i]-0.045) * np.cos(sza)-(0.0327 * TL2[[i]]-0.014) * np.power(np.cos(sza), 2))
            EghHeliosat1_temp = EbnHeliosat1[i] * np.cos(sza)+EdhHeliosat1[i]

            # Quality control
            lower = 0
            EbnHeliosat1_temp[EbnHeliosat1_temp < lower] = 0
            EdhHeliosat1_temp[EdhHeliosat1_temp < lower] = 0
            EghHeliosat1_temp[EghHeliosat1_temp < lower] = 0
            EbnHeliosat1[i] = EbnHeliosat1_temp
            EdhHeliosat1[i] = EdhHeliosat1_temp
            EghHeliosat1[i] = EghHeliosat1_temp

        return EghHeliosat1, EdhHeliosat1, EbnHeliosat1
