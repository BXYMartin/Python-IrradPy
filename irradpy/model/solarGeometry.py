import datetime

import numpy as np


def dayth_hourth(datetime):
    datetuple = datetime.timetuple()
    dayth = datetuple.tm_yday
    hourth = datetuple.tm_hour + datetuple.tm_min / 60

    return dayth, hourth


def latlon2solarzenith(lat, lon, datearray):
    """
    n: station number
    m: date number
    :param lat: np.ndarray of lat vector (n,1)
    :param lon: np.ndarray of lon vector (n,1)
    :param datearray: np.ndarray of np.datetim64 which can get from dataset ; vector (m,n)
    :return: zenith of (n,m)
    """
    time = datearray.astype(datetime.datetime)

    yday = np.vectorize(dayth_hourth)

    dayth, hourth = yday(time)

    dayth = dayth.T
    hourth = hourth.T

    lat = lat.reshape([lat.size, 1])
    lon = lon.reshape([lon.size, 1])

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


def data_eext_builder(datearray):
    datearray = datearray.astype(datetime.datetime)

    yday = np.vectorize(dayth_hourth)

    ndd, hourth = yday(datearray)

    esc = 1366.1
    beta = (2 * np.pi * ndd) / 365
    Eext = esc * (1.00011 + 0.034221 * np.cos(beta) + 0.00128 * np.sin(beta) + 0.000719 * np.cos(
        2 * beta) + 0.000077 * np.sin(
        2 * beta))

    return Eext


def timeseries_builder(timeset,num_station):
    if len(timeset) != 1 and num_station == len(timeset):

        unique_timeset = []

        for time_s in timeset:
            inflag = 0
            for index in range(len(unique_timeset)):
                if (unique_timeset[index] == time_s).all():
                    inflag = 1
            if inflag == 0:
                unique_timeset.append(time_s)

        if len(unique_timeset) == 1:
            print(len(unique_timeset))
            raise Exception(
                'Duplicate time series definitions, enter only one definition if you want to use the same time for all sites')

        timeseries = [timeset[0].values[:, np.newaxis].astype('datetime64[m]')]

        for index in range(len(timeset) - 1):
            new_series = timeset[index + 1].values[:, np.newaxis].astype('datetime64[m]')

            timeseries.append(new_series)

        return timeseries

    elif len(timeset) == 1:
        timeseries = timeset[0].values[:, np.newaxis].astype('datetime64[m]')

        timeseries = np.tile(timeseries, num_station)

        return timeseries.T
    elif len(timeset) > num_station:
        raise Exception(
            'Station number > time definition')