### 02-Schulze 1957

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

class ClearSkySchulze:
    def __init__(self):
        pass

    def Schulze(self, sza):
        # Direct normal irradiance
        Ebnschulze=1127*np.power(0.888, (1/np.cos(sza)))

        # Diffuse horizontal irradiance
        Edhschulze=94.23*np.power(np.cos(sza),0.5)

        # Global horizontal irradiance
        Eghschulze=Ebnschulze*np.cos(sza)+Edhschulze

        # Quality control
        lower=0
        Ebnschulze[Ebnschulze<lower]=0
        Edhschulze[Edhschulze<lower]=0
        Eghschulze[Eghschulze<lower]=0
        return [Ebnschulze, Edhschulze, Eghschulze]


