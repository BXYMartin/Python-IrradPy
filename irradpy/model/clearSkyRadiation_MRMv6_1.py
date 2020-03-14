### 68-MRMv6.1 2017

###References:
# Kambezidis, H. D., & Psiloglou, B. E. (2008). The meteorological radiation model (MRM): advancements and applications. In Modeling solar radiation at the earth’s surface (pp. 357-392). Springer, Berlin, Heidelberg.
# Kambezidis, H. D., Psiloglou, B. E., Karagiannis, D., Dumka, U. C., & Kaskaoutis, D. G. (2016). Recent improvements of the Meteorological Radiation Model for solar irradiance estimates under all-sky conditions. Renewable Energy, 93, 142-158.
# Kambezidis, H. D., Psiloglou, B. E., Karagiannis, D., Dumka, U. C., & Kaskaoutis, D. G. (2017). Meteorological Radiation Model (MRM v6. 1): Improvements in diffuse radiation estimates and a new approach for implementation of cloud products. Renewable and Sustainable Energy Reviews, 74, 616-637.
# author's fortran code

###Inputs:
#  Esc=1360.8     [Wm-2]             (Solar constant)
#  sza            [radians]          (zenith_angle)
#  press          [mb]               (local barometric)
#  albedo         [double]           (surface/ground albedo)
#  AOD_550        [dimensionless]    (aerosol optical depth at 700 nm)
#  ozone          [atm.cm]           (total columnar amount of ozone)
#  wv             [atm.cm]           (total columnar amount of water vapour)
#  'AEROSOL-TABLE.txt'   provided by author

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from numpy import sin, cos, log, log10, power, pi, exp, sqrt
from .solarGeometry import time2dayth, time2yearth

class ClearSkyMRMv6_1:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def MRMv6_1(self, sza, wv, albedo, ozone, aod550):
        # Extraterrestrial irradiance
        Esc = 1360.8
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # air mass
        m = 1 / (cos(sza) + 0.50572 * power((pi / 2 - sza) / pi * 180 + 6.07995, -1.6364))
        ma = m * self.press / 1013.25

        # broadband transmission function for water vapour
        ##we have wv value, so directly use eq.14.27. if no wv value, use eq.14.20abcd
        Tw = 1 - (3.0140 * m * wv / (power(1 + 119.3 * m * wv, 0.644) + 5.814 * m * wv))

        # broadband transmission function for Rayleigh scattering
        Tr = exp(-(0.1128 * power(ma, 0.8346) * (0.9341 - power(ma, 0.9868) + 0.9391 * ma)))

        # broadband transmission function for absorption by ozone
        ## we have ozone value, so directly use eq.14.27. if no ozone value, use eq.14.9
        To = 1 - (0.2554 * m * ozone / (power(1 + 6107.26 * m * ozone, 0.204) + 0.471 * m * ozone))

        # broadband transmission function for absorption by uniformly gases(CO2,CO,N2O,CH4,02)
        Tco2 = 1 - (0.07210 * ma * 350 / (power(1 + 377.890 * ma * 350, 0.5855) + 3.1709 * ma * 350))
        Tco = 1 - (0.0062 * ma * 0.075 / (power(1 + 243.670 * ma * 0.075, 0.4246) + 1.7222 * ma * 0.075))
        Tn2o = 1 - (0.0326 * ma * 0.28 / (power(1 + 107.413 * ma * 0.28, 0.5501) + 0.9093 * ma * 0.28))
        Tch4 = 1 - (0.0192 * ma * 1.6 / (power(1 + 166.095 * ma * 1.6, 0.4221) + 0.7186 * ma * 1.6))
        To2 = 1 - (0.0003 * ma * 2.095e5 / (power(1 + 476.934 * ma * 2.095e5, 0.4892) + 0.1261 * ma * 2.095e5))
        Tmg = Tco2 * Tco * Tn2o * Tch4 * To2

        # broadband transmission function for aerosol total extinction(scattering and absorption)
        ## JAMIEs MATLAB CODE TO BE CONVERTED AND ADDED HERE.
        # Produces Taa, Taer, Tas.
        with open("AEROSOL-TABLE.txt", "r") as f:
            aerosol_table = f.readlines()
        for i, line in enumerate(aerosol_table):
            aerosol_table[i] = line.split(",")
        aerosol_table = np.array(aerosol_table)
        wavelength = aerosol_table[:, 0]
        ET = aerosol_table[:, 1]
        AODtable = aerosol_table[:, 2:5]
        SSAtable = aerosol_table[:, 6:9]
        k = aod550 - aod550 + 4
        for i in range(len(k)):
            if aod550[i] >= 0.3:
                k[i] = 1
            elif aod550[i] >= 0.2:
                k[i] =  2
            else:
                k[i] = 3
        AODt = aod550 - aod550
        SSA = aod550 - aod550
        for i in range(len(k)):
            AODt[i] = AODtable[391, k[i]]
        RAOD = aod550 / AODt
        sumetl = sum(((ET[1:] + ET[0:-1]) / 2) * (wavelength[1:] - wavelength[0:-1]))
        sumletl = np.zeros(len(aod550))
        sumtletl = np.zeros(len(aod550))
        for t in range(len(aod550)):
            sumletl[t] = sum((exp(-ma[t] * RAOD[t] * AODtable[1:, k[t]]) * ET[1:] + exp(
                -ma[t] * RAOD[t] * AODtable[0:-1, k[t]]) * ET[0:-1]) / 2 * (
                                     wavelength[1:] - wavelength[0:-1]))
            sumtletl[t] = sum((exp(-ma[t] * RAOD[t] * AODtable[1:, k[t]] * SSAtable[1:, k[t]]) * ET[1:] + exp(
                -ma[t] * RAOD[t] * AODtable[0:-1, k[t]] * SSAtable[0:-1, k[t]]) * ET[0:-1]) / 2 * (
                                      wavelength[1:] - wavelength[0:-1]))
        sumletl[0] = sumetl
        sumtletl[0] = sumetl

        Taer = sumletl / sumetl
        Tas = sumtletl / sumetl
        Taa = Taer / Tas

        # direct horizontal/beam irradiance
        Ebh = Eext * cos(sza) * Tw * Tr * To * Tmg * Taer
        EbnMRM61 = Eext * Tw * Tr * To * Tmg * Taer

        # calculation of Diffuse and global radiation from Fortran
        Tc = 1  # Tc=1 means clear
        Ra = 0.0685 + 0.26 * (1 - Taer) + 0.4 * (1 - Tc)
        Rsa = Ra * albedo
        Ebhc = Ebh * Tc

        # Calculation of Mie (aerosol) forward scattering percentage fa
        fa = abs(-8e-5 * power(pi / 2 - sza, 2) + 0.0117 * (pi / 2 - sza) + 0.5)
        HDR3 = Eext * cos(sza) * Tw * To * Tmg * Taa * (sqrt(0.5 * fa) * (1.0 - Tas * Tr))
        HDR3c = (HDR3 * Tc) + (0.32 * (1.0 - Tc) * (Ebh + HDR3))
        HDA3c = (Ebhc + HDR3c) * ((Rsa) / (1.0 - Rsa))

        # Diffuse horizonral irradiance
        EdhMRM61 = HDR3c + HDA3c

        # Global horizonral irradiance
        EghMRM61 = EbnMRM61 * cos(sza) + EdhMRM61

        # Quality control
        lower = 0
        EbnMRM61[EbnMRM61 < lower] = 0
        EdhMRM61[EdhMRM61 < lower] = 0
        EghMRM61[EghMRM61 < lower] = 0
        return [EbnMRM61, EdhMRM61, EghMRM61]
