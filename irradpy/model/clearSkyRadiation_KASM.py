### 15-KASM  1983

###References:
# Kasten, F. (1984). Parametrisierung der Globalstahlung durch Bedeckungsgrad und Trubungsfaktor. Annalen der Meteorologie Neue, 20, 49-50.
# Badescu, V. (1997). Verification of some very simple clear and cloudy sky models to evaluate global solar irradiance. Solar Energy, 61(4), 251-264.
# Badescu, V., Gueymard, C. A., Cheval, S., Oprea, C., Baciu, M., Dumitrescu, A., ... & Rada, C. (2013). Accuracy analysis for fifty-four clear-sky solar radiation models using routine hourly global irradiance measurements in Romania. Renewable Energy, 55, 85-103.

###Inputs:
#  Esc=1367   [Wm-2]      (Solar constant)
#  sza        [radians]   (zenith_angle)
#  press      [mb]        (local barometric)
#  wv         [atm.cm]    (total columnar amount of water vapour)

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from .solarGeometry import time2dayth, time2yearth

class ClearSkyAtwaterBall1:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def AtwaterBall1(self, sza, wv):
        # Extraterrestrial irradiance
        Esc = 1367
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (
                    1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(
                2 * B))

        # Air Mass
        amk = 1 / (np.cos(sza) + 0.15 * (np.power(3.885 + (np.pi / 2 - sza) * 180 / np.pi, -1.253)))
        am = amk * self.press / 1013.25
        am2 = am * am
        am3 = am2 * am
        am4 = am3 * am
        am5 = am4 * am

        w1 = 10 * wv
        TrR = 0.9768 - 0.0874 * am + 0.010607552 * am2 - 0.000846205 * am3 + 3.57246e-5 * am4 - 6.0176e-7 * am5

        x = amk * 3.5
        aov = 0.002118 * x / (1 + 0.0042 * x + 0.00000323 * x * x)
        aou = 0.1082 * x / np.power((1 + 13.86 * x), 0.805) + 0.00658 * x / (1 + np.power(10.36 * x, 3))
        TroP = 1 - aov - aou

        wp = w1 * am
        aw = 0.29 * wp / (np.power(1 + 14.15 * wp, 0.635) + 0.5925 * wp)
        Tra = np.power(0.9, am)

        # Direct normal irradiance
        EbnKASM = Eext * (TrR * TroP - aw) * Tra

        # Diffuse horizontal irradiance
        EdhKASM = Eext * np.cos(sza) * (
                    TroP * (1 - TrR) * 0.5 + (TroP * TrR - aw) * (1 - Tra) * 0.75 * (0.93 - 0.21 * np.log(am)))

        # Global horizontal irradiance
        EghKASM = EbnKASM * np.cos(sza) + EdhKASM

        # Quality control
        lower = 0
        EbnKASM[EbnKASM < lower] = 0
        EdhKASM[EdhKASM < lower] = 0
        EghKASM[EghKASM < lower] = 0
        return [EbnKASM, EdhKASM, EghKASM]