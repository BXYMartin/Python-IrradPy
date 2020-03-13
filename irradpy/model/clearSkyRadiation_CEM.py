### 54-CEM 1978

###References:
# Atwater, M. A., & Ball, J. T. (1978). A numerical solar radiation model based on standard meteorological observations. Solar Energy, 21(3), 163-170.
# Badescu, V., Gueymard, C. A., Cheval, S., Oprea, C., Baciu, M., Dumitrescu, A., ... & Rada, C. (2013). Accuracy analysis for fifty-four clear-sky solar radiation models using routine hourly global irradiance measurements in Romania. Renewable Energy, 55, 85-103.

###Inputs:
#  Esc=1353         [Wm-2]              (Solar constant)
#  sza              [radians]           (zenith_angle)
#  press            [mb]                (local barometric)
#  albedo           [double]            (surface/ground albedo)
#  Broadband_AOD    [dimensionless]     (broadband aerosol optical depth)
#  wv               [atm.cm]            (total columnar amount of water vapour)

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

class ClearSkyCEM:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def CEM(self, sza, wv, albedo, broadbandaod):
        # Extraterrestrial irradiance
        Esc = 1353
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        am = 35 / power(1224 * power(cos(sza), 2) + 1, 0.5)
        amp = am * self.press / 1013.25
        p = self.press / 1013.25 * 101.325
        X1 = power(am * (949 * p * 1e-5 + 0.051), 0.5)
        Trb = 1.041 - 0.16 * X1
        Trg = 1.021 - 0.0824 * X1
        Tg = 1
        To = 1
        absw = 0.077 * power(am * wv, 0.3)
        Trw = 1 - absw
        Tra = exp(-amp * broadbandaod)

        # direct normal irradiance
        EbnCEM = Eext * Tra * (Trb * Tg - absw)
        # global horizontal irradiance
        EghCEM = Eext * cos(sza) * Tra * (Trg * Tg - absw) / (1 - albedo * 0.0685)
        # diffuse horizontal irradiance
        EdhCEM = EghCEM - EbnCEM * cos(sza)

        # Quality control
        lower = 0
        EbnCEM[EbnCEM < lower] = 0
        EdhCEM[EdhCEM < lower] = 0
        EghCEM[EghCEM < lower] = 0
        return [EbnCEM, EdhCEM, EghCEM]
