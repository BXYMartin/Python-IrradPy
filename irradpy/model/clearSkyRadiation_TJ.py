### 01-TJ 1957

###References:
#Threlkeld, J. L., & Jordan, R. C. (1957). Direct solar radiation available on clear days. Heat., Piping Air Cond., 29(12).
#Masters, G. M. (2013). Renewable and efficient electric power systems. John Wiley & Sons.

###Inputs:
#  sza  [radians]  (zenith_angle)

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from .solarGeometry import *

class clearSkyTJ:
    def __init__(self, time):
        self.dayth = time2dayth(time)

    def TJ(self, sza):
        if type(sza) is np.ndarray and type(self.dayth) is np.ndarray:
            if len(sza) != len(self.dayth):
                raise RuntimeError("Solar Zenith Angle array should be the same length as the time array!")
        else:
            raise RuntimeError("Input should be np.ndarray!")

        # Air Mass
        mA = 1 / np.cos(sza)

        # Coefficients
        A = 1160+75*np.sin(2*np.pi*(self.dayth-275)/365)
        k = 0.174+0.035*np.sin(2*np.pi*(self.dayth-100)/365)
	C = 0.095+0.04*np.sin(2*np.pi*(self.dayth-100)/365)

	# Direct Normal Irradiance
	EbnTJ = A*np.exp(-1*k*mA)

	# Diffuse Horizontal Irradiance
	EdhTJ = C*EbnTJ

	# Global Horizontal Irradiance
	EghTJ = EbnTJ*np.cos(sza)+EdhTJ

        # Quality Control
        lower = 0
        EbnTJ[EbnTJ<lower] = 0
        EdhTJ[EdhTJ<lower] = 0
        EghTJ[EghTJ<lower] = 0
        return EbnTJ, EdhTJ, EghTJ


