### 51-Simplified Soils 2008

###References:
# Ineichen, P. (2008). A broadband simplified version of the Solis clear sky model. Solar Energy, 82(8), 758-762.

###Inputs:
#  Esc=1367   [Wm-2]              (Solar constant)
#  sza        [radians]           (zenith_angle)
#  press      [mb]                (local barometric)
#  AOD_700    [dimensionless]     (aerosol optical depth at 700 nm)
#  wv         [atm.cm]            (total columnar amount of water vapour)

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

class ClearSkySimplifiedSoils:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def SimplifiedSoils(self, sza, wv, aod700):
        # Extraterrestrial irradiance
        Esc = 1367
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Ineichen 2008 limit aod700 between 0~0.45
        aod700[aod700 > 0.45] = 0.45

        # Modified solar constant(Eext)
        Eext0 = 1.08 * power(wv, 0.0051)
        Eext1 = 0.97 * power(wv, 0.032)
        Eext2 = 0.12 * power(wv, 0.56)
        Eexte = Eext * (Eext2 * aod700 * aod700 + Eext1 * aod700 + Eext0 + 0.071 * log(self.press / 1013.25))

        # direct total optical depth
        tb1 = 1.82 + 0.056 * log(wv) + 0.0071 * power(log(wv), 2)
        tb0 = 0.33 + 0.045 * log(wv) + 0.0096 * power(log(wv), 2)
        tbp = 0.0089 * wv + 0.13
        tb = tb1 * aod700 + tb0 + tbp * log(self.press / 1013.25)
        b1 = 0.00925 * aod700 * aod700 + 0.0148 * aod700 - 0.0172
        b0 = -0.7565 * aod700 * aod700 + 0.5057 * aod700 + 0.4557
        b = b1 * log(wv) + b0

        # diffuse total optical depth
        # for aod700<0.05
        td4 = 86 * wv - 13800
        td3 = -3.11 * wv + 79.4
        td2 = -0.23 * wv + 74.8
        td1 = 0.092 * wv - 8.86
        td0 = 0.0042 * wv + 3.12
        tdp = -0.83 * power(1 + aod700, -17.2)
        # for aod700>=0.05
        for i in range(len(wv)):
            if aod700[i] >= 0.05:
                td4[i] = -0.21 * wv[i] + 11.6
                td3[i] = 0.27 * wv[i] - 20.7
                td2[i] = -0.134 * wv[i] + 15.5
                td1[i] = 0.0554 * wv[i] - 5.71
                td0[i] = 0.0057 * wv[i] + 2.94
                tdp[i] = -0.71 * power(1 + aod700[i], -15)
        td = td4 * power(aod700, 4) + td3 * power(aod700, 3) + td2 * power(aod700, 2) + td1 * aod700 + td0 + tdp * log(self.press / 1013.25)
        dp = 1 / (18 + 152 * aod700)
        d = -0.337 * power(aod700, 2) + 0.63 * aod700 + 0.116 + dp * log(self.press / 1013.25)

        # global total optical depth
        tg1 = 1.24 + 0.047 * log(wv) + 0.0061 * power(log(wv), 2)
        tg0 = 0.27 + 0.043 * log(wv) + 0.0090 * power(log(wv), 2)
        tgp = 0.0079 * wv + 0.1
        tg = tg1 * aod700 + tg0 + tgp * log(self.press / 1013.25)
        g = -0.0147 * log(wv) - 0.3079 * power(aod700, 2) + 0.2846 * aod700 + 0.3798

        # direct normal radiation
        Ebnsolis = Eexte * exp(-tb / (power(cos(sza), b)))

        # diffuse horizontal radiation
        Edhsolis = Eexte * exp(-td / (power(cos(sza), d)))

        # global horizontal irradiance
        Eghsolis = Eexte * exp(-tg / (power(cos(sza), g))) * cos(sza)

        # Quality control
        lower = 0
        Ebnsolis[Ebnsolis < lower] = 0
        Edhsolis[Edhsolis < lower] = 0
        Eghsolis[Eghsolis < lower] = 0
        return [Ebnsolis, Edhsolis, Eghsolis]
