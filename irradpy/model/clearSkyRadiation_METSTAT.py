### 64-METSTAT 1998

###References:
# Maxwell, E. L. (1998). METSTAT—The solar radiation model used in the production of the National Solar Radiation Data Base (NSRDB). Solar Energy, 62(4), 263-279.
# Badescu, V., Gueymard, C. A., Cheval, S., Oprea, C., Baciu, M., Dumitrescu, A., ... & Rada, C. (2013). Accuracy analysis for fifty-four clear-sky solar radiation models using routine hourly global irradiance measurements in Romania. Renewable Energy, 55, 85-103.

###Inputs:
#  Esc=1367         [Wm-2]             (Solar constant)
#  sza              [radians]          (zenith_angle)
#  press            [mb]               (local barometric)
#  albedo           [double]           (surface/ground albedo)
#  Broadband_AOD    [dimensionless]    (broadband aerosol optical depth)
#  ozone            [atm.cm]           (total columnar amount of ozone)
#  wv               [atm.cm]           (total columnar amount of water vapour)

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

class ClearSkyMETSTAT:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def METSTAT(self, sza, wv, albedo, ozone, broadbandaod):
        # Extraterrestrial irradiance
        Esc = 1367
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        am = 1 / (cos(sza) + 0.15 * power((pi / 2 - sza) / pi * 180 + 3.885, -1.253))
        ama = am * self.press / 1013.25

        # water vapour transmittance
        xw = wv * am
        Tw = 1 - 1.668 * xw / (4.042 * xw + power(1 + 54.6 * xw, 0.637))

        # Rayleigh scattering transmittance
        TR = exp(-0.0903 * power(ama, 0.84) * (1 + ama - power(ama, 1.01)))

        # ozone absorption transmittance
        XO = ozone * am
        To = 1 - 0.1611 * XO * power(1 + 139.48 * XO, -0.3035) - 0.002715 * XO * 1/(1 + 0.044 * XO + 0.0003 * XO * XO)

        # transmittance from absorption by uniformly mixed gases
        Tum = exp(-0.0127 * power(ama, 0.26))

        # total aerosol transmittance
        TA = exp(-broadbandaod * am)

        # direct normal irradiance
        Kn = 0.9751 * TR * To * Tum * Tw * TA
        EbnMetstat = Eext * Kn

        omega = 0.9  # Badescu
        Ba = 0.84  # Badescu
        Taa = 1 - (1 - omega) * (1 - am + power(am, 1.06)) * (1 - TA)
        Tas = TA / Taa
        Tabs = To * Tum * Taa
        Tsr = 0.5 * (1 - TR) * Tabs
        Tsa = Ba * (1 - TA) * Tabs
        Fam = 0.38 + 0.925 * exp(-0.851 * am)
        rhos = 0.0685 + (1 - Ba) * (1 - Tas)
        Ts0 = (Tsr + Tsa) * Fam
        Tsg = (Kn + Ts0) * (albedo - 0.2) * rhos
        Td = Ts0 + Tsg
        XKt = Kn + Td

        # diffuse horizontal irradiance
        EdhMetstat = Td * Eext * cos(sza)

        # global horizontal irradiance
        EghMetstat = XKt * Eext * cos(sza)

        # Quality control
        lower = 0
        EbnMetstat[EbnMetstat < lower] = 0
        EdhMetstat[EdhMetstat < lower] = 0
        EghMetstat[EghMetstat < lower] = 0
        return [EbnMetstat, EdhMetstat, EghMetstat]
