### 29-34 ESRA 2000

###References:
# Rigollier, C., Bauer, O., & Wald, L. (2000). On the clear sky model of the ESRA—European Solar Radiation Atlas—with respect to the Heliosat method. Solar energy, 68(1), 33-48.

###Inputs:
#  Esc=1367   [Wm-2]      (Solar constant)
#  sza        [radians]   (zenith_angle)
#  altitude   [m]         (location's altitude)
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

class ClearSkyESRA:
    def __init__(self, time, elev):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.elev = elev

    def ESRA(self, sza, TL2):
        # Extraterrestrial irradiance
        Esc = 1367
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Air mass corrected for elevation
        # correct alpha(solar altitude angle, alpha=pi/2-sza) for refraction
        alpha = np.pi / 2 - sza
        alphatrue = alpha + 0.061359 * (0.1594 + 1.123 * alpha + 0.065656 * alpha * alpha) / (
                    1 + 28.9344 * alpha + 277.3971 * alpha * alpha)
        ame = np.exp(-self.elev / 8434.5) / (np.sin(alphatrue) + 0.50572 * np.power(alphatrue / np.pi * 180 + 6.07995, -1.6364))
        # Rayleigh Optical Thickness (rot)

        rot = 1 / (6.6296 + 1.7513 * ame - 0.1202 * np.power(ame, 2) + 0.0065 * np.power(ame, 3) - 0.00013 * np.power(ame, 4))
        for i in range(len(rot)):
            if ame[i] > 20:
                rot[i] = 1 / (10.4 + 0.718 * ame[i])

        # direct beam irradiance
        # Ebnesra = Eext*exp(-0.8662*TL2*ame*rot)

        # the diffuse transmission function at zenith
        # TRD = (-1.5843e-2)+(3.0543e-2)*TL2+(3.797e-4)*TL2^2
        # the diffuse angular function
        # a0 = (2.6463e-1)-(6.1581e-2)*TL2+(3.1408e-3)*TL2^2
        # a1 = 2.0402+(1.8945e-2)*TL2-(1.1161e-2)*TL2^2
        # a2 = -1.3025+(3.9231e-2)*TL2+(8.5079e-3)*TL2^2
        # a0[which((a0*TRD<(2e-3))==T)] = (2e-3)/TRD[which((a0*TRD<(2E-3))==T)]
        # FD = a0+a1*sin(alpha)+a2*(sin(alpha))^2
        # diffuse horizontal irradiance
        # Edesra = Eext*TRD*FD

        # global horizontal irradiance
        # Eghesra= Ebnesra*cos(sza)+Edesra

        # EghEsra_name = c('EghEsra_R', 'EghEsra_D', 'EghEsra_I', 'EghEsra_Gu', 'EghEsra_M', 'EghEsra_Gr')
        # EbnEsra_name = c('EbnEsra_R', 'EbnEsra_D', 'EbnEsra_I', 'EbnEsra_Gu', 'EbnEsra_M', 'EbnEsra_Gr')
        # EdhEsra_name = c('EdhEsra_R', 'EdhEsra_D', 'EdhEsra_I', 'EdhEsra_Gu', 'EdhEsra_M', 'EdhEsra_Gr')
        EghEsra = [0] * len(TL2)
        EdhEsra = [0] * len(TL2)
        EbnEsra = [0] * len(TL2)

        for i in range(len(TL2)):
            # Quality control
            lower = 0

            # direct beam irradiance
            EbnEsra_temp = Eext * np.exp(-0.8662 * TL2[i] * ame * rot)
            EbnEsra_temp[EbnEsra_temp < lower] = 0
            # diffuse horizontal irradiance
            TRD = (-1.5843e-2) + (3.0543e-2) * TL2[i] + (3.797e-4) * np.power(TL2[i], 2)
            a01 = (2.6463e-1) - (6.1581e-2) * TL2[i] + (3.1408e-3) * np.power(TL2[i], 2)
            a11 = 2.0402 + (1.8945e-2) * TL2[i] - (1.1161e-2) * np.power(TL2[i], 2)
            a21 = -1.3025 + (3.9231e-2) * TL2[i] + (8.5079e-3) * np.power(TL2[i], 2)
            for j in range(len(a01)):
                if a01[j] * TRD < 2e-3:
                    a01[j] = (2e-3) / TRD[j]
            FD = a01 + a11 * np.sin(alpha) + a21 * np.power(np.sin(alpha), 2)
            EdhEsra_temp = Eext * TRD * FD
            EdhEsra_temp[EdhEsra_temp < lower] = 0
            # global horizontal irradiance
            EghEsra_temp = EbnEsra_temp * np.cos(sza) + EdhEsra_temp

            EbnEsra[i] = EbnEsra_temp
            EdhEsra[i] = EdhEsra_temp
            EghEsra[i] = EghEsra_temp

        return [EghEsra, EdhEsra, EbnEsra]
