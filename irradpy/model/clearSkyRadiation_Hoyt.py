### 62-Hoyt 1978

###References:
# Iqbal, M. (2012). An introduction to solar radiation. Elsevier.

###Inputs:
#  Esc=1367   [Wm-2]             (Solar constant)
#  sza        [radians]          (zenith_angle)
#  press      [mb]               (local barometric)
#  albedo     [double]           (surface/ground albedo)
#  ang_beta   [dimensionless]    (Angstrom turbidity coefficient)
#  ozone      [atm.cm]           (total columnar amount of ozone)
#  wv         [atm.cm]           (total columnar amount of water vapour)

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from numpy import sin, cos, log, log10, power, pi, exp
from .solarGeometry import time2dayth, time2yearth

class ClearSkyHoyt:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def Hoyt(self, sza, wv, albedo, ozone, ang_beta):
        # Extraterrestrial irradiance
        Esc = 1367
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        am = 1 / (cos(sza) + 0.15 * power(3.885 + (pi / 2 - sza) / pi * 180, -1.253))
        ama = am * self.press / 1013.25

        # absorption ratio for water vapor
        U1 = am * wv * power(self.press / 1013.25, 0.75)
        aw = 0.110 * power(U1 + 6.31e-4, 0.3) - 0.0121

        # absorption ratio for uniformly mixed gases(carbon dioxide + oxygen)
        ag = 0.00235 * power(126 * ama + 0.0129, 0.26) - 7.5e-4 + 7.5e-3 * power(ama, 0.875)

        # absorption ratio for ozone
        U3 = ozone * am
        ao = 0.045 * power(U3 + 8.34e-4, 0.38) - 3.1e-3

        # the transmittance due to Rayleigh scattering
        Tr = 0.615958 + 0.375566 * exp(-0.221185 * ama)

        # the transmittance due to scattering by aerosols
        gAB = -0.914 + 1.909267 * exp(-0.667023 * ang_beta)
        Tas = power(gAB, ama)

        # the transmittance due to absorptance of aerosols
        w0 = 0.95  # recommended by Hoyt
        Aa = (1 - w0) * power(gAB, ama)

        # direct beam irradiance
        Ebnhoyt = Eext * (1 - aw - ag - ao - Aa) * Tr * Tas

        # the diffuse irradiance from the Rayleigh atmosphere
        Idr = Eext * cos(sza) * (1 - aw - ag - ao - Aa) * 0.5 * (1 - Tr)

        # the diffuse irradiance from aerosol scattering
        Ida = Eext * cos(sza) * (1 - aw - ag - ao - Aa) * 0.75 * (1 - Tas)

        # the diffuse irradiance from multiple reflections between ground and cloundless-sky atmosphere
        Q = Ebnhoyt * cos(sza) + Idr + Ida
        Tr1 = 0.615958 + 0.375566 * exp(-0.221185 * 1.66 * self.press / 1013.25)
        Tas1 = power(gAB, 1.66 * self.press / 1013.25)
        U11 = wv * (power(self.press / 1013.25, 0.75)) * (ama + 1.66 * self.press / 1013.25)
        aw1 = 0.110 * power(U11 + (6.31e-4), 0.3) - 0.0121
        ag1 = 0.00235 * power(126 * (ama + 1.66 * self.press / 1013.25) + 0.0129, 0.26) - 7.5e-4 + 7.5e-3 * power(
                    ama + 1.66 * self.press / 1013.25, 0.875)
        U33 = ozone * (ama + 1.66 * self.press / 1013.25)
        ao1 = 0.045 * power(U33 + 8.34e-4, 0.38) - 3.1e-3
        Aa1 = (1 - w0) * power(gAB, ama + 1.66 * self.press / 1013.25)
        Idm = albedo * Q * (1 - aw1 - ag1 - ao1 - Aa1) * (0.5 * (1 - Tr1) + 0.25 * (1 - Tas1))

        # diffuse horizontal irradiance
        Edhhoyt = Idr + Ida + Idm
        # global horizontal irradiance
        Eghhoyt = Ebnhoyt * cos(sza) + Edhhoyt

        # Quality control
        lower = 0
        Ebnhoyt[Ebnhoyt < lower] = 0
        Edhhoyt[Edhhoyt < lower] = 0
        Eghhoyt[Eghhoyt < lower] = 0
        return [Ebnhoyt, Edhhoyt, Eghhoyt]