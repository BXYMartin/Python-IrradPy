### 53-Perrin 1975

###References:
# de Brichambaut, C. P. (1975). Estimation des Ressources Energétiques en France. Cahiers de l’AFEDES, (1).
# Badescu, V., Gueymard, C. A., Cheval, S., Oprea, C., Baciu, M., Dumitrescu, A., ... & Rada, C. (2013). Accuracy analysis for fifty-four clear-sky solar radiation models using routine hourly global irradiance measurements in Romania. Renewable Energy, 55, 85-103.

###Inputs:
#  Esc=1366.1   [Wm-2]             (Solar constant)
#  sza          [radians]          (zenith_angle)
#  press        [mb]               (local barometric)
#  ang_beta     [dimensionless]    (Angstrom turbidity coefficient)
#  wv           [atm.cm]           (total columnar amount of water vapour)
#  ozone        [atm.cm]           (total columnar amount of ozone)

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

class ClearSkyPerrin:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def Perrin(self, sza, wv, ozone, ang_beta):
        # Extraterrestrial irradiance
        Esc = 1367
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # air mass
        am = 1 / (cos(sza) + 0.15 * power((pi / 2 - sza) / pi * 180 + 3.885, -1.253))

        ama = am * self.press / 1013.25

        Trr = exp(-0.031411 - 0.064331 * ama)

        ako3 = am * ozone
        abso3 = 0.015 + 0.024 * ako3
        Tro = 1 - abso3

        akw = am * wv


        xw = np.zeros(len(wv))  # create a zero vector
        for i in range(len(akw)):
            if akw[i] > 0:
                xw[i] = log(akw[i])
        # xw[akw>0]=log(akw[akw>0])
        xw2 = xw * xw
        absw = 0.1 + 0.03 * xw + 0.002 * xw2
        Trw = 1 - absw

        xwg = np.zeros(len(wv))  # create a zero vector
        akwg = ama * wv
        for i in range(len(akwg)):
            if akwg[i] > 0:
                xwg[i] = log(akwg[i])
        # xwg[akwg>0]=log(akwg[akwg>0])
        absg = 0.013 - 0.0015 * xwg
        Trg = 1 - absg

        Tra = exp(-1.4327 * am * ang_beta)

        # direct normal irradiance
        EbnPerrin = Eext * Trr * Tra * (1 - abso3 - absw - absg)

        tCDA = 1 / (9.4 + 0.9 * ama)
        TL = -(log(EbnPerrin / Eext)) / (tCDA * ama)
        # global horizontal irradiance
        EghPerrin = (1270 - 56 * TL) * power(cos(sza), (TL + 36) / 33)

        # diffuse horizontal irradiance
        EdhPerrin = EghPerrin - EbnPerrin * cos(sza)

        # Strange limit in Badescu
        for i in range(len(EdhPerrin)):
            if EdhPerrin < 0:
                EghPerrin[i] = EbnPerrin[i] * (cos(sza))[i]
        # EghPerrin[EdhPerrin<0]=EbnPerrin[EdhPerrin<0]*(cos(sza))[EdhPerrin<0]

        # Quality control
        lower = 0
        EbnPerrin[EbnPerrin < lower] = 0
        EdhPerrin[EdhPerrin < lower] = 0
        EghPerrin[EghPerrin < lower] = 0
        return [EbnPerrin, EdhPerrin, EghPerrin]
