### 06-ASHRAE 1985

###References:
#Handbook, A. F. (1985). American society of heating, refrigerating and air-conditioning engineers. Inc.: Atlanta, GA, USA.
#El Mghouchi, Y., Ajzoul, T., Taoukil, D., & El Bouardi, A. (2016). The most suitable prediction model of the solar intensity, on horizontal plane, at various weather conditions in a specified location in Morocco. Renewable and Sustainable Energy Reviews, 54, 84-98.

###Inputs:
#  sza  [radians]  (zenith_angle)

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Month is the month number ranging from 1 to 12.

###Codes:
import numpy as np
from .solarGeometry import time2month

class ClearSkyASHRAE:
    def __init__(self, time):
        self.month = time2month(time)

    def ASHRAE(self, sza):
        if type(sza) is np.ndarray and type(self.month) is np.ndarray:
            if len(sza) != len(self.month):
                raise RuntimeError("Solar Zenith Angle array should be the same length as the time array!")
        else:
            raise RuntimeError("Input should be np.ndarray!")
        # Coeff of A,B,C from Jan,Feb,....,Dec
        A=[1230,1215,1186,1136,1104,1088,1085,1107,1152,1193,1221,1234]
        B=[0.142,0.144,0.156,0.180,0.196,0.205,0.207,0.201,0.177,0.160,0.149,0.142]
        C=[0.058,0.060,0.071,0.097,0.121,0.134,0.136,0.122,0.092,0.073,0.063,0.057]
        # Direct normal irradiance
        # EbnASHRAE=A*exp(-B/sinalpha)
        length = len(sza)
        EbnASHRAE=np.zeros(length)
        for i in range(length):
            EbnASHRAE[i] = A[self.month[i]]*np.exp(-1*B[self.month[i]]/np.cos(sza[i]))

        # Diffuse horizontal irradiance
        # EdhASHRAE=C*EbnASHRAE
        EdhASHRAE=np.zeros(length)
        for i in range(length):
            EdhASHRAE[i] = C[self.month[i]]*EbnASHRAE[i]

        # Global horizontal irradiance
        EghASHRAE=EbnASHRAE*np.cos(sza)+EdhASHRAE

        # Quality control
        lower=0
        EbnASHRAE[EbnASHRAE<lower]=0
        EdhASHRAE[EdhASHRAE<lower]=0
        EghASHRAE[EghASHRAE<lower]=0
        return [EbnASHRAE, EdhASHRAE, EghASHRAE]
