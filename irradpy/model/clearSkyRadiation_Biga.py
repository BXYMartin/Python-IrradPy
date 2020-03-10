### 05-Biga 1979

###References:
#Schulze, R. E. (1976). A physically based method of estimating solar radiation from suncards. Agricultural Meteorology, 16(1), 85-101.

###Inputs:
#  sza  [radians]  (zenith_angle)

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Codes:
import numpy as np

class ClearSkyBiga:
    def __init__(self):
        pass

    def Biga(self, sza):
        #direct normal irradiance
        EbnBiga=926*np.power((np.cos(sza)),0.29)
        #diffuse horizontal irradiance
        EdhBiga=131*np.power((np.cos(sza)), 0.6)
        #global horizontal irradiance
        EghBiga=1057*np.power((np.cos(sza)), 1.17)

        ###Quality control
        lower=0
        EbnBiga[EbnBiga<lower]=0
        EdhBiga[EdhBiga<lower]=0
        EghBiga[EghBiga<lower]=0
        return [EbnBiga, EdhBiga, EghBiga]

