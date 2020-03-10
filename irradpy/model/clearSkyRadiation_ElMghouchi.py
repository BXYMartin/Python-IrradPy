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

class ClearSkyElMghouchi:
    def __init__(self, time):
        self.dayth = time2dayth(time)

    def ElMghouchi(self, sza):
        if type(sza) is np.ndarray and type(self.dayth) is np.ndarray:
            if len(sza) != len(self.dayth):
                raise RuntimeError("Solar Zenith Angle array should be the same length as the time array!")
        else:
            raise RuntimeError("Input should be np.ndarray!")

        #extraterrestrial irradiance
        Esc=1367
        Eext=Esc*(1+0.034*np.cos(self.dayth-2))

        #turbidity atmospheric factor for clear skies
        TFactor=0.796-0.01*np.sin(0.986*(self.dayth+284))

        #direct normal irradiance
        EbnElMghouchi=Eext*TFactor*np.exp(-0.13/np.cos(sza))

        #diffuse horizontal irradiance
        EdhElMghouchi=120*TFactor*np.exp(-1/(0.4511+np.cos(sza)))

        #global horizontal irradiance
        EghElMghouchi=EbnElMghouchi*np.cos(sza)+EdhElMghouchi

        ###Quality control
        lower=0
        EbnElMghouchi[EbnElMghouchi<lower]=0
        EdhElMghouchi[EdhElMghouchi<lower]=0
        EghElMghouchi[EghElMghouchi<lower]=0
        return [EbnElMghouchi, EdhElMghouchi, EghElMghouchi]


