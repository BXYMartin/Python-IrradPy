### 57-PSIM 1993

###References:
# Gueymard, C. (1993). Mathermatically integrable parameterization of clear-sky beam and global irradiances and its use in daily irradiation applications. Solar Energy, 50(5), 385-397.
# Badescu, V., Gueymard, C. A., Cheval, S., Oprea, C., Baciu, M., Dumitrescu, A., ... & Rada, C. (2013). Accuracy analysis for fifty-four clear-sky solar radiation models using routine hourly global irradiance measurements in Romania. Renewable Energy, 55, 85-103.

###Inputs:
#  Esc=1373   [Wm-2]             (Solar constant)
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

class ClearSkyPSIM:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def PSIM(self, sza, wv, albedo, ang_beta):
        # Extraterrestrial irradiance
        Esc = 1373
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Air Mass for Atwater
        ATM = self.press / 1013.25
        Fbgw = exp(0.155 * (1 - power(wv, 0.24)))
        F2PB = 1 + (0.1594 - 0.226 * ang_beta) * (1 - ATM)
        F2PG = 1 + (0.0752 - 0.107 * ang_beta) * (1 - ATM)
        ROS = 0.061 + 0.072 * power(ang_beta, 0.5)
        F3RO = (1 - 0.2 * ROS) / (1 - albedo * ROS)
        S = cos(sza)
        S[S < 0.0285] = 0.0285
            
        S2 = S * S
        S3 = S2 * S
        S4 = S2 * S2
        S5 = S3 * S2
        X = log(1 + 10 * ang_beta)
        X2 = X * X
        X3 = X2 * X
        A0 = exp(-1.62364 - 6.8727 * X)
        A1 = 2.94298 + 5.23504 * X - 18.23861 * X2 + 11.1652 * X3
        A2 = -8.12158 - 15.8 * X + 69.2345 * X2 - 45.1637 * X3
        A3 = 12.5571 + 25.44 * X - 123.3933 * X2 + 83.1014 * X3
        A4 = -9.8044 - 20.3172 * X + 103.9906 * X2 - 71.3091 * X3
        A5 = 3.00487 + 6.3176 * X - 33.3891 * X2 + 23.1547 * X3
        # limit of ang_beta>=0.175

        for i in range(len(X)):
            if ang_beta[i] >= 0.175:
                A0[i] = 0
                A1[i] = 4.41547 - 5.09266 * X[i] + 1.471865 * X2[i]
                A2[i] = -18.45187 + 38.3584 * X[i] - 22.7449 * X2[i] + 4.3189 * X3[i]
                A3[i] = 31.2506 - 74.53835 * X[i] + 48.355 * X2[i] - 9.8657 * X3[i]
                A4[i] = -25.18762 + 64.3575 * X[i] - 43.6586 * X2[i] + 9.23151 * X3[i]
                A5[i] = 7.64179 - 20.41687 * X[i] + 14.20502 * X2[i] - 3.06053 * X3[i]

        # direct normal radiation
        EbnPSIM = Eext * Fbgw * F2PB * (A0 + A1 * S + A2 * S2 + A3 * S3 + A4 * S4 + A5 * S5)

        # global horizontal irradiance
        g0 = 0.006
        g1 = 0.387021 - 0.386246 * X + 0.09234 * X2
        g2 = 1.35369 + 1.533 * X - 1.07736 * X2 + 0.23728 * X3
        g3 = -1.59816 - 1.903774 * X + 1.631134 * X2 - 0.3877 * X3
        g4 = 0.66864 + 0.80172 * X - 0.75795 * X2 + 0.18895 * X3
        EghPSIM = Eext * Fbgw * F2PG * (g0 + g1 * S + g2 * S2 + g3 * S3 + g4 * S4) * F3RO

        # diffuse horizontal radiation
        EdhPSIM = EghPSIM - EbnPSIM * cos(sza)
        EdhPSIM[EdhPSIM < 0] = 0


        # Quality control
        lower = 0
        EbnPSIM[EbnPSIM < lower] = 0
        EdhPSIM[EdhPSIM < lower] = 0
        EghPSIM[EghPSIM < lower] = 0
        return [EbnPSIM, EdhPSIM, EghPSIM]
