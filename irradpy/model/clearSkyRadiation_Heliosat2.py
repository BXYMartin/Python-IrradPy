### 35-40 Heliosat-2 2002

###References:
# Lefevre, M., Albuisson, M., & Wald, L. (2002). Joint report on interpolation scheme ‘meteosat’and database ‘climatology’i (meteosat). SoDa Deliverable D3-8 and D5-1-4. Internal document.

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
from scipy import interpolate
from .solarGeometry import time2dayth, time2yearth

class ClearSkyHeliosat2:
    def __init__(self, time, elev):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.elev = elev

    def Heliosat2(self, sza, TL2):
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
        am = 1 / np.power(np.sin(alphatrue) + 0.50572 * (alphatrue / np.pi * 180 + 6.07995), -1.6364)
        # corr_rot is the correction of the integral Rayleigh optical thickness due to the elevation of the site
        corr_rot1 = 1
        corr_rot075 = 1.248174 - 0.011997 * am + 0.00037 * am * am
        corr_rot05 = 1.68219 - 0.03059 * am + 0.00089 * am * am

        # piecewise linear interpolation
        ntotal = len(corr_rot05)
        corr_rot = corr_rot05  # define the length of corr_rot
        x = [0.5, 0.75, 1]
        y = [corr_rot05[i], corr_rot075[i], 1]
        pchup0 = np.exp(-self.elev / 8434.5)  # all sites satisfy p/p0>=0.5
        for i in range(ntotal):
            if not np.isnan(corr_rot05[i]) and not np.isnan(corr_rot075[i]):
                f = interpolate.interp1d(x, y, kind='cubic')
                corr_rot[i] = f(pchup0)

        # Rayleigh Optical Thickness (rot)

        rot = (1 / corr_rot) * 1 / (6.625928 + 1.92969 * am - 0.170073 * am * am + 0.011517 * np.power(am, 3) - 0.000285 * np.power(am, 4))
        for i in range(len(rot)):
            if am[i] > 20:
                rot[i] = 1 / (10.4 + 0.718 * am[i] * np.exp(-self.elev / 8434.5))

        L00 = alpha  # define the length of L00 to be the same as the length of alpha
        for i in range(len(alpha)):
            if alpha[i] > np.pi / 6:
                L00[i] = -1.7349e-2
            elif alpha[i] > np.pi / 12:
                L00[i] = -8.2193e-3
            else:
                L00[i] = -1.1656e-3


        L01 = alpha  # define the length
        for i in range(len(alpha)):
            if alpha[i] > np.pi / 6:
                L01[i] = -5.8985e-3
            elif alpha[i] > np.pi / 12:
                L01[i] = 4.5643e-4
            else:
                L01[i] = 1.8408e-4

        L02 = alpha  # define the length
        for i in range(len(alpha)):
            if alpha[i] > np.pi / 6:
                L02[i] = 6.8868e-4
            elif alpha[i] > np.pi / 12:
                L02[i] = 6.7916e-5
            else:
                L02[i] = -4.8754e-7

        L10 = alpha  # define the length
        for i in range(len(alpha)):
            if alpha[i] > np.pi / 6:
                L10[i] = 1.0258
            elif alpha[i] > np.pi / 12:
                L10[i] = 8.9233e-1
            else:
                L10[i] = 7.4095e-1

        L11 = alpha  # define the length
        for i in range(len(alpha)):
            if alpha[i] > np.pi / 6:
                L11[i] = -1.2196e-1
            elif alpha[i] > np.pi / 12:
                L11[i] = -1.9991e-1
            else:
                L11[i] = -2.2427e-1

        L12 = alpha  # define the length
        for i in range(len(alpha)):
            if alpha[i] > np.pi / 6:
                L12[i] = 1.9299e-3
            elif alpha[i] > np.pi / 12:
                L12[i] = 9.9741e-3
            else:
                L12[i] = 1.5314e-2

        L20 = alpha  # define the length
        for i in range(len(alpha)):
            if alpha[i] > np.pi / 6:
                L20[i] = -7.2178e-3
            elif alpha[i] > np.pi / 12:
                L20[i] = 2.5428e-1
            else:
                L20[i] = 3.4959e-1

        L21 = alpha  # define the length
        for i in range(len(alpha)):
            if alpha[i] > np.pi / 6:
                L21[i] = 1.3086e-1
            elif alpha[i] > np.pi / 12:
                L21[i] = 2.6140e-1
            else:
                L21[i] = 7.2313e-1

        L22 = alpha  # define the length
        for i in range(len(alpha)):
            if alpha[i] > np.pi / 6:
                L22[i] = -2.8405e-3
            elif alpha[i] > np.pi / 12:
                L22[i] = -1.7020e-2
            else:
                L22[i] = -1.2305e-1

        L23 = alpha  # define the length
        for i in range(len(alpha)):
            if alpha[i] > np.pi / 6:
                L23[i] = 0
            elif alpha[i] > np.pi / 12:
                L23[i] = 0
            else:
                L23[i] = 5.9194e-3


        # Trb=exp(-0.8662*TL2*exp(altitude/8434.5)*rot)

        # c0=L00+L01*TL2*pchup0+L02*(TL2*pchup0)^2
        # c1=L10+L11*TL2*pchup0+L12*(TL2*pchup0)^2
        # c2=L20+L21*TL2*pchup0+L22*(TL2*pchup0)^2+L23*(TL2*pchup0)^3
        # Fb=c0+c1*sin(alpha)+c2*(sin(alpha))^2

        # direct horizontal irradiance
        # Eb=Eext*pmax(Trb*Fb,0)

        # the diffuse transmission function at zenith
        # Trd=(-1.5843e-2)+(3.0543e-2)*TL2*pchup0+(3.797e-4)*(pchup0*TL2)^2
        # the diffuse angular function
        # a0 = (2.6463e-1)-(6.1581e-2)*TL2*pchup0+(3.1408e-3)*(pchup0*TL2)^2
        # a1 = 2.0402+(1.8945e-2)*TL2*pchup0-(1.1161e-2)*(pchup0*TL2)^2
        # a2 = -1.3025+(3.9231e-2)*TL2*pchup0+(8.5079e-3)*(pchup0*TL2)^2
        # a0[which((a0*Trd<(2e-3))==T)] = (2e-3)/Trd[which((a0*Trd<(2E-3))==T)]
        # FD = a0+a1*sin(alpha)+a2*(sin(alpha))^2
        # diffuse horizontal irradiance
        # Ed = Eext*pmax(Trd*FD,0)
        # global horizontal irradiance
        # Eghheliosat2=Eb+Ed

        # EghHeliosat2_name = c('EghHeliosat2_R', 'EghHeliosat2_D', 'EghHeliosat2_I', 'EghHeliosat2_Gu', 'EghHeliosat2_M',
        #                       'EghHeliosat2_Gr')
        # EbnHeliosat2_name = c('EbnHeliosat2_R', 'EbnHeliosat2_D', 'EbnHeliosat2_I', 'EbnHeliosat2_Gu', 'EbnHeliosat2_M',
        #                       'EbnHeliosat2_Gr')
        # EdhHeliosat2_name = c('EdhHeliosat2_R', 'EdhHeliosat2_D', 'EdhHeliosat2_I', 'EdhHeliosat2_Gu', 'EdhHeliosat2_M',
        #                       'EdhHeliosat2_Gr')
        EghHeliosat2 = [0] * len(TL2)
        EdhHeliosat2 = [0] * len(TL2)
        EbnHeliosat2 = [0] * len(TL2)


        for i in range(len(TL2)):
            # Quality control
            lower = 0
            # direct beam irradiance
            Trb=np.exp(-0.8662 * TL2[i] * np.exp(self.elev / 8434.5) * rot)
            c0=L00+L01 * TL2[i] * pchup0+L02 * np.power(TL2[i] * pchup0, 2)
            c1=L10+L11 * TL2[i] * pchup0+L12 * np.power(TL2[i] * pchup0, 2)
            c2=L20+L21 * TL2[i] * pchup0+L22 * np.power(TL2[i] * pchup0, 2)+L23 * np.power(TL2[i] * pchup0, 3)
            Fb=c0+c1 * np.sin(alpha)+c2 * np.power(np.sin(alpha), 2)
            M1 = Trb * Fb
            M1[M1 < 0] = 0
            EbnHeliosat2_temp = Eext * M1 / np.sin(alpha)
            EbnHeliosat2_temp[EbnHeliosat2_temp < lower] = 0
            EbnHeliosat2[i] = EbnHeliosat2_temp

            # diffuse horizontal irradiance
            TRD = (-1.5843e-2)+(3.0543e-2) * TL2[i]+(3.797e-4) * np.power(TL2[i], 2)
            a01 = (2.6463e-1)-(6.1581e-2) * TL2[i]+(3.1408e-3) * np.power(TL2[i], 2)
            a11 = 2.0402+(1.8945e-2) * TL2[i]-(1.1161e-2) * np.power(TL2[i], 2)
            a21 = -1.3025+(3.9231e-2) * TL2[i]+(8.5079e-3) * np.power(TL2[i], 2)

            for j in range(len(a01)):
                if a01[j] * TRD < 2e-3:
                    a01[j] = (2e-3) / TRD[j]
            FD = a01+a11 * np.sin(alpha)+a21 * np.power(np.sin(alpha), 2)
            M2 = TRD * FD
            M2[M2 < 0] = 0
            EdhHeliosat2_temp = Eext * M2
            EdhHeliosat2_temp[EdhHeliosat2_temp < lower] = 0
            EdhHeliosat2[i] = EdhHeliosat2_temp

            # global horizontal irradiance
            EghHeliosat2_temp = EbnHeliosat2_temp * np.cos(sza)+EdhHeliosat2_temp
            EghHeliosat2_temp[EghHeliosat2_temp < lower] = 0
            EghHeliosat2[i] = EghHeliosat2_temp
        return [EghHeliosat2, EdhHeliosat2, EbnHeliosat2]
