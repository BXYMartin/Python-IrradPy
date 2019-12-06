import xarray as xr
import numpy as np
import math
import scipy
import datetime
import sys
import os


def extract_dataset(lats, lons, dataset_path, variables, datevecs, interpolate=True):
    """
    extract variables from dataset

    :param lats: numpy.ndarray
    :param lons: numpy.ndarray
    :param dataset_path: string
    :param variables: list of string
    :param datevecs: list of string
    :param interpolate: bool

    :return var: list of numpy.ndarray


    lons and lats determine a site coordinate together. lons.length==lat.length

    datavecs need to increase monotonically.

    """

    lons_unique, lons_index = np.unique(lons, return_inverse=True)
    lats_unique, lats_index = np.unique(lats, return_inverse=True)

    try:
        dataset = xr.open_dataset(dataset_path).sel(lat=lats_unique, lon=lons_unique, method='nearest')[
            variables]  # ectract nearest stations point for given lats and lons

    except:
        print('The data set does not contain the specified variable')
        return -1

    if dataset['time'].size > 1:
        if interpolate:
            dataset_interpolation = dataset.interp(time=datevecs)  # use datevecs to interpolate
        else:
            try:
                dataset_interpolation = dataset.sel(time=datevecs)
            except:
                print('can not find data match specified time coordinate, exit with code -2. Maybe you want to '
                      'interpolate.')
                return -2

    else:
        dataset_interpolation = dataset

    var = []
    for index_variables in variables:
        if interpolate:
            station_data = np.empty([len(datevecs), len(lats)], dtype=float)
            for index_station in range(len(lons)):
                station_data[:, index_station] = np.array([dataset_interpolation[index_variables].sel(
                    lat=lats[index_station], lon=lons[index_station], method='nearest').data]).T[:, 0]

        else:
            station_data = np.empty([len(lons_unique), 1], dtype=float)  # for phis
            for index_station in range(len(lons)):
                station_data[index_station, :] = np.array([dataset_interpolation[index_variables].sel(
                    lat=lats[index_station], lon=lons[index_station], method='nearest').data])[:, 0]
        var.append(station_data)

    return var


def extract_dataset_list(lats, lons, dataset_path_list, variables, datevecs, interpolate=True):
    """
    extract variables from dataset

    :param lats: numpy.ndarray
    :param lons: numpy.ndarray
    :param dataset_path_list: list of string
    :param variables: list of string
    :param datevecs: list of string
    :param interpolate: bool

    :return var: list of numpy.ndarray

    lons and lats determine a site coordinate together. lons.length==lat.length

    datavecs need to increase monotonically.

    """
    '''
    var_list = []
    for dataset_path in dataset_path_list:
        var = extract_dataset(lats, lons, dataset_path, variables, datevecs, interpolate)
        var_list.append(var)
    return var_list
    '''
    halfhour = datetime.timedelta(minutes=30)
    var_list = []
    for index_dataset in range(len(dataset_path_list)):
        dataset = xr.open_dataset(dataset_path_list[index_dataset])
        dataset_starttime = datetime.datetime.strptime(np.datetime_as_string(dataset['time'][0]),
                                                       '%Y-%m-%dT%H:%M:%S.000000000')
        dataset_endtime = datetime.datetime.strptime(np.datetime_as_string(dataset['time'][-1]),
                                                     '%Y-%m-%dT%H:%M:%S.000000000')
        datevecs_for_dataset = []

        if index_dataset == 0:
            for index_datevec in range(len(datevecs)):
                if datetime.datetime.strptime(datevecs[index_datevec],
                                              '%Y-%m-%dT%H:%M:%S') <= dataset_endtime + halfhour:
                    datevecs_for_dataset.append(datevecs[index_datevec])

        elif index_dataset == len(dataset_path_list) - 1:
            for index_datevec in range(len(datevecs)):
                if datetime.datetime.strptime(datevecs[index_datevec],
                                              '%Y-%m-%dT%H:%M:%S') > dataset_starttime + halfhour:
                    datevecs_for_dataset.append(datevecs[index_datevec])

        else:
            for index_datevec in range(len(datevecs)):
                if dataset_starttime - halfhour < datetime.datetime.strptime(datevecs[index_datevec],
                                                                             '%Y-%m-%dT%H:%M:%S') <= dataset_endtime + halfhour:
                    datevecs_for_dataset.append(datevecs[index_datevec])

        var_list.append(
            extract_dataset(lats, lons, dataset_path_list[index_dataset], variables, datevecs_for_dataset, interpolate))
    var = var_list[0]
    for index_varlist in range(len(var_list) - 1):
        for index_variable in range(len(variables)):
            var[index_variable] = np.vstack((var[index_variable], var_list[index_varlist + 1][index_variable]))

    return var

