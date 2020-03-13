### 66-Paulescu & Schlett 2003

###References:
# Paulescu, M., & Schlett, Z. (2003). A simplified but accurate spectral solar irradiance model. Theoretical and applied climatology, 75(3-4), 203-212.

###Inputs:
#  Esc=1369     [Wm-2]             (Solar constant)
#  sza          [radians]          (zenith_angle)
#  altitude     [m]                (location's altitude)
#  press        [mb]               (local barometric)
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

class ClearSkyPaulescuSchlett:
    def __init__(self, time, press, elev):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press
        self.elev = elev

    def PaulescuSchlett(self, sza, wv, ozone, ang_beta):
        # Extraterrestrial irradiance
        Esc = 1369
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # air mass
        am = (1 - self.elev * 10e-4) / (cos(sza) + 0.50572 * power((pi / 2 - sza) / pi * 180 + 6.07995, -1.6364))

        # ozone
        To3 = exp(-am * ozone * (0.0184 - 0.0004 * am * ozone + 0.022 * power(am * ozone, -0.66)))

        # wv
        emw = am * wv
        Twv = exp(-emw * (-0.002 + 1.67e-5 * emw + 0.094 * power(emw, -0.693)))

        # trace gas absorption
        Tg = exp(-am * (-5.4e-5 - 3.8e-6 * am + 0.0099 * power(am, -0.62)))

        # Rayleigh scattering
        emp = am * self.press / 1013.25
        Tr = exp(-emp * (0.709 + 0.0013 * emp - 0.5856 * power(emp, 0.058)))

        # aerosol extinction
        emb = am * ang_beta
        Ta = exp(-emb * (1.053 - 0.083 * emb + 0.3345 * power(emb, -0.668)))
        Ta[Ta > 1] = 1

        # direct normal radiation

        EbnPaulescu = Eext * Tr * Ta * Twv * To3 * Tg

        # diffuse horizontal radiation
        gama = 0.432
        EdhPaulescu = gama * Eext * cos(sza) * (1 - Tr * Ta) * Twv * To3 * Tg

        # global radiation
        EghPaulescu = EbnPaulescu * cos(sza) + EdhPaulescu


        # Quality control
        lower = 0
        EbnPaulescu[EbnPaulescu < lower] = 0
        EdhPaulescu[EdhPaulescu < lower] = 0
        EghPaulescu[EghPaulescu < lower] = 0
        return [EbnPaulescu, EdhPaulescu, EghPaulescu]
