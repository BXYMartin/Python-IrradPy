### 70-Bird 1981

###References:
# Bird, R. E., & Hulstrom, R. L. (1981). Simplified clear sky model for direct and diffuse insolation on horizontal surfaces (No. SERI/TR-642-761). Solar Energy Research Inst., Golden, CO (USA).

###Inputs:
#  Esc=1353     [Wm-2]             (Solar constant)
#  sza          [radians]          (zenith_angle)
#  press        [mb]               (local barometric)
#  albedo       [double]           (surface/ground albedo)
#  ang_alpha    [dimensionless]    (Angstrom_exponent, also known as alpha)
#  ang_beta     [dimensionless]    (Angstrom turbidity coefficient)
#  ozone        [atm.cm]           (total columnar amount of ozone)
#  wv           [atm.cm]           (total columnar amount of water vapour)

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

class ClearSkyBird:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def Bird(self, sza, wv, albedo, ozone, ang_alpha, ang_beta):
        # Extraterrestrial irradiance
        Esc = 1353
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Air Mass
        am = 1 / (cos(sza) + 0.15 * power((pi / 2 - sza) / pi * 180 + 3.885, -1.25))

        ama = am * self.press / 1013.25

        # transmittaance of Rayleigh scattering
        TR = exp(-0.0903 * power(ama, 0.84) * (1 + ama - power(ama, 1.01)))

        # transmittaance of Ozone absorptance
        XO = ozone * am
        TO = 1 - 0.1611 * XO * power(1 + 139.48 * XO, -0.3035) - 0.002715 * XO * 1/(1 + 0.044 * XO + 0.0003 * XO * XO)

        # transmittaance of absorptance by uniformly mixed gases(CO2,O2)
        TUM = exp(-0.0127 * power(ama, 0.26))

        # transmittaance of water vapor absorptance
        XW = wv * am
        TW = 1 - 2.4959 * XW * 1/(power(1 + 79.034 * XW, 0.6828) + 6.385 * XW)

        # transmittance of aerosol absorptance and scattering
        broadaod = ang_beta * (0.2758 * power(0.38, -ang_alpha) + 0.35 * power(0.5, -ang_alpha))
        TA = exp((-power(broadaod, 0.873)) * (1 + broadaod - power(broadaod, 0.7088)) * power(am, 0.9108))

        # direct beam irradiance
        Ebnbird = Eext * 0.9662 * TA * TW * TUM * TO * TR

        # transmittance of aerosol absorptance
        K1 = 0.1  # as suggested by author
        TAA = 1 - K1 * (1 - am + power(am, 1.06)) * (1 - TA)

        # transmittance of aerosol scattering
        TAS = TA / TAA

        BA = 0.84  # as suggested by author
        Eas = Eext * cos(sza) * 0.79 * TO * TUM * TW * TAA * (0.5 * (1 - TR) + BA * (1 - TAS)) / (1 - am + power(am, 1.02))

        rs = 0.0685 + (1 - BA) * (1 - TAS)  # sky albedo
        rs[rs < 0] = 0
        rs[rs > 1] = 1
        rg = albedo  # ground albedo

        # global horizontal irradiance
        Eghbird = (Ebnbird * cos(sza) + Eas) / (1 - rg * rs)
        # diffuse horizontal irradiance
        Edhbird = Eghbird - Ebnbird * cos(sza)

        # Quality control
        lower = 0
        Ebnbird[Ebnbird < lower] = 0
        Edhbird[Edhbird < lower] = 0
        Eghbird[Eghbird < lower] = 0
        return [Ebnbird, Edhbird, Eghbird]
