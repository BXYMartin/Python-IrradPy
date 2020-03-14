### 56-RSC 1985

###References:
# Carroll, J. J. (1985). Global transmissivity and diffuse fraction of solar radiation for clear and cloudy skies as measured and as predicted by bulk transmissivity models. Solar Energy, 35(2), 105-118.
# Badescu, V., Gueymard, C. A., Cheval, S., Oprea, C., Baciu, M., Dumitrescu, A., ... & Rada, C. (2013). Accuracy analysis for fifty-four clear-sky solar radiation models using routine hourly global irradiance measurements in Romania. Renewable Energy, 55, 85-103.

###Inputs:
#  Esc=1371   [Wm-2]             (Solar constant)
#  sza        [radians]          (zenith_angle)
#  press      [mb]               (local barometric)
#  albedo     [double]           (surface/ground albedo)
#  ang_beta   [dimensionless]    (Angstrom turbidity coefficient)
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

class ClearSkyRSC:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def RSC(self, sza, wv, albedo, ang_beta):
        # Extraterrestrial irradiance
        Esc = 1371
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Air Mass for Atwater
        am = 1 / (cos(sza) + 0.15 * power((pi / 2 - sza) / pi * 180 + 3.885, -1.253))  # relative air mass
        ama = am * self.press / 1013.25

        # Rayleigh Transmittance
        gamma = 0.054 - 0.0088 * ama + (1.08E-3) * power(ama, 2) - (5.1E-5) * power(ama, 3)
        TR = power(10, (-ama * gamma))

        Ta = power(10, (-0.02 * ama))

        Tp = power(10, (-0.666 * ang_beta * ama))

        # water vapour Transmittance
        Tw = power(10, (-ama * (0.04 * power(wv, 0.1) + 0.01 * wv)))

        # direct normal irradiance
        EbnRSC = Eext * Ta * Tw * Tp * TR
        Eb = EbnRSC * cos(sza)  # direct horizontal irradiance

        # diffuse horizontal irradiance
        Ew = Eext * cos(sza) * Ta * Tw  # from Badescu
        Ef = (0.5 + 0.3 * ang_beta) * power(cos(sza), 1 / 3) * (Ew - Eb)
        f3 = (0.98 + 0.1 * albedo + 0.36 * ang_beta * (albedo - 0.25)) * (Eb + Ef) - (Eb + Ef)
        EdhRSC = Ef + f3

        # global horizontal irradiance
        EghRSC = EbnRSC * cos(sza) + EdhRSC

        # Quality control
        lower = 0
        EbnRSC[EbnRSC < lower] = 0
        EdhRSC[EdhRSC < lower] = 0
        EghRSC[EghRSC < lower] = 0
        return [EbnRSC, EdhRSC, EghRSC]
