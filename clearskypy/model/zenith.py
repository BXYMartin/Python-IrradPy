import numpy as np
import datetime

def latlon2solarzenith(lat, lon, datearray):
    """

    :param lat: np.ndarray of lat vector (n,1)
    :param lon: np.ndarray of lon vector (n,1)
    :param datearray: np.ndarray of np.datetim64 which can get from dataset ; vector (m,1)
    :return: zenith of (n,m)
    """
    dayth = []
    hourth = []
    datearray = np.array(datearray, dtype='datetime64[s]').reshape([datearray.size, 1])
    lat = lat.reshape([lat.size, 1])
    lon = lon.reshape([lon.size, 1])
    for date in datearray:
        datetuple = date[0].astype(datetime.datetime).timetuple()
        dayth.append(datetuple.tm_yday)
        hourth.append(datetuple.tm_hour + datetuple.tm_min / 60)
    dayth = np.array(dayth).reshape(datearray.shape).T
    hourth = np.array(hourth).reshape(datearray.shape).T

    Bd = (360 / 365.242) * (dayth - 1)
    Br = np.deg2rad(Bd)

    eott = (0.258 * np.cos(Br) - 7.416 * np.sin(Br) - 3.648 * np.cos(2 * Br) - 9.228 * np.sin(2 * Br))

    usn = 12 - lon / 15 - 1. * (eott / 60)

    ha_d = (hourth - usn) * 15
    ha_d[ha_d >= 180] = -1. * (360 - ha_d[ha_d >= 180])
    ha_d[ha_d <= -180] = 360 + ha_d[ha_d <= -180]
    ha_r = np.deg2rad(ha_d)

    phid_i = (2 * np.pi / 365) * (dayth + (hourth / 24) - 1)

    decl_r = 0.006918 - 0.399912 * np.cos(phid_i) + 0.070257 * np.sin(phid_i) - 0.006758 * np.cos(
        2. * phid_i) + 0.000907 * np.sin(2. * phid_i) - 0.002697 * np.cos(3. * phid_i) + 0.001480 * np.sin(3. * phid_i)

    tm1 = np.sin(np.deg2rad(lat)) * np.sin(decl_r) + np.cos(np.deg2rad(lat)) * np.cos(decl_r) * np.cos(ha_r)
    zen_r = np.arccos(tm1)
    zen = np.rad2deg(zen_r)

    zen = zen.T

    return zen
