import datetime
from pydap.client import open_url
from pydap.cas.urs import setup_session
from .process import DownloadManager
import xarray as xr
import config
import utils
import shutil
import multiprocessing
from functools import partial
import subprocess
import logging
import sys
import os
import errno
import time
import tempfile
import netCDF4
import numpy as np
import numpy.ma as ma
import urllib.error
from calendar import monthrange
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union
from .variables import var_list

class SocketManager:
    deff4 = netCDF4.default_fillvals["f4"]

    global_retry = True
    # The arrays contain the coordinates of the grid used by the API.
    # The values are from 0 to 360 and 0 to 575
    lat_coords = np.arange(0, 361, dtype=int)
    lon_coords = np.arange(0, 576, dtype=int)

    def generate_url_params(self, parameter, time_para, lat_para, lon_para):
        """Creates a string containing all the parameters in query form"""
        parameter = map(lambda x: x + time_para, parameter)
        parameter = map(lambda x: x + lat_para, parameter)
        parameter = map(lambda x: x + lon_para, parameter)
        addition = []
        addition.append('time')
        addition.append('lat' + lat_para)
        addition.append('lon' + lon_para)
        return ','.join(parameter) + ',' + ','.join(addition)

    def translate_lat_to_geos5_native(self, latitude):
        """
        The source for this formula is in the MERRA2
        Variable Details - File specifications for GEOS pdf file.
        The Grid in the documentation has points from 1 to 361 and 1 to 576.
        The MERRA-2 Portal uses 0 to 360 and 0 to 575.
        latitude: float Needs +/- instead of N/S
        """
        return ((latitude + 90) / 0.5)

    def translate_lon_to_geos5_native(self, longitude):
        """See function above"""
        return ((longitude + 180) / 0.625)

    def find_closest_coordinate(self, calc_coord, coord_array):
        """
        Since the resolution of the grid is 0.5 x 0.625, the 'real world'
        coordinates will not be matched 100% correctly. This function matches
        the coordinates as close as possible.
        """
        # np.argmin() finds the smallest value in an array and returns its
        # index. np.abs() returns the absolute value of each item of an array.
        # To summarize, the function finds the difference closest to 0 and returns
        # its index.
        index = np.abs(coord_array-calc_coord).argmin()
        return coord_array[index]

    # function to build the database url
    def build_remote_url(self, merra2_collection, date):
        if merra2_collection["collection"].startswith("const"):
            return (
                ('https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2_MONTHLY/'
                 '{db_name}/1980/')
                 .format(db_name=merra2_collection["esdt_dir"])
            )
        else:
            return (
                ('https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2/'
                 '{db_name}/{date:%Y}/{date:%m}/')
                 .format(db_name=merra2_collection["esdt_dir"],
                         date=date)
            )

    # function to build the database file name
    def build_remote_filename(self, merra2_collection, date, params):
        merra_stream = "400"
        file_extension = "nc"
        date_string = '{date:%Y%m%d}'.format(date=date)
        if date.year < 1992:
            merra_stream = "100"
        elif date.year < 2001:
            merra_stream = "200"
        elif date.year < 2011:
            merra_stream = "300"

        if merra2_collection["collection"].startswith("const"):
            merra_stream = "101"
            date_string = "00000000"
            file_extension = "nc4"

        if params is not None:
            return (
                'MERRA2_{stream}.{abbrv}.{date}.nc4.{ext}?{params}'
                .format(stream=merra_stream,
                        abbrv=merra2_collection["collection"],
                        date=date_string, params=params, ext=file_extension)
            )
        else:
            return (
                'MERRA2_{stream}.{abbrv}.{date}.nc4'
                .format(stream=merra_stream,
                        abbrv=merra2_collection["collection"],
                        date=date_string, params=params)
            )


    def download_merra2_nc(self, date, merra2_collection, output_directory, params, auth):
        final_ds = xr.Dataset()

        # build url
        url = os.path.join(self.build_remote_url(merra2_collection, date),
                            self.build_remote_filename(merra2_collection, date, params))

        # The DownloadManager class is defined in the opendap_download module.
        download_manager = DownloadManager()
        download_manager.set_username_and_password(auth['uid'], auth['password'])
        download_manager.download_path = output_directory
        download_manager.download_url = url

        # If you want to see the download progress, check the download folder you
        # specified
        start_time = time.time()
        logging.info("* File from Date " + str(date) + " Begin to Download")
        retry = True
        limit = 0
        passwd = False
        while retry and limit < 5:
            limit = limit + 1
            log = "{url} # {limit} Time Retry #".format(url=url, limit=limit)
            try:
                download_manager.start_download()
                retry = False
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    logging.error(log + ': Requested URL is not available.')
                elif e.code == 401:
                    logging.error(log + ': Username and or Password are not correct!')
                    passwd = True
                else:
                    logging.error(log + ': ' + str(e))
            except IOError as e:
                logging.error(log + ': IO Error in Device!')
            except IndexError as e:
                logging.error(log + ': Unknown Download URL!')
            except TypeError as e:
                logging.error(log + ': File Chunk Type Mismatch')

        if retry:
            logging.critical("* File from Date " + str(date) + " Failed Download")
            file_path = os.path.join(download_manager.download_path, download_manager.get_filename(url))
            if not passwd:
                self.global_retry = True
            if os.path.exists(file_path):
                os.remove(file_path)
            return False
        else:
            logging.info("* File from Date " + str(date) + " Finished Download With %3.2f Seconds" % (time.time() - start_time))
            return True


    def iter_days(self, first: datetime.date, last: datetime.date):
        """Yields first, first+1day, ..., last-1day, last"""
        current = first
        while current <= last:
            yield current
            current += datetime.timedelta(1)

    # run the function
    def subdaily_universal_download(
        self,
        merra2_collection: str,
        initial_year: int,
        final_year: int,
        initial_month: int = 1,
        final_month: int = 12,
        initial_day: int = 1,
        final_day: Optional[int] = None,
        params: Optional[str] = None,
        auth: dict = None,
        output_directory: Union[str, Path] = None,
        thread_num: int = 5,
    ):
        """
        MERRA2 universal download.

        Parameters
        ----------
        merra2_collection : str
        initial_year : int
        final_year : int
        initial_month : int
        final_month : int
        initial_day : int
        final_day : Optional[int]
        params : Optional[str]
        auth : dict,
        output_directory : Union[str, Path]
        thread_num : int

        """
        if not isinstance(output_directory, Path):
            log_file = Path(output_directory)

        log_file = os.path.join(log_file.parent, 'index.npy')
        if os.path.exists(log_file):
            log = np.load(log_file).tolist()
        else:
            log = []

        dates = []
        for date in self.iter_days(datetime.date(initial_year, initial_month, initial_day), datetime.date(final_year, final_month, final_day)):
            if self.build_remote_filename(merra2_collection, date, params) in log:
                logging.info("Skipping existing file " + self.build_remote_filename(merra2_collection, date, params) + " from " + merra2_collection["esdt_dir"])
                continue
            else:
                logging.info("Preparing new file " + self.build_remote_filename(merra2_collection, date, params) + " from " + merra2_collection["esdt_dir"])
                log.append(self.build_remote_filename(merra2_collection, date, params))
            dates.append(date)

        if len(dates) > 0:
            logging.info("----  Begin  Download  ----")
            pool = multiprocessing.Pool(thread_num)
            rel = pool.map(
                    partial(self.download_merra2_nc,
                        merra2_collection=merra2_collection,
                        output_directory=output_directory,
                        params=params,
                        auth=auth,
                        ), dates
                    )

            for i, success in enumerate(rel):
                if success:
                    logging.info("% New File from Date " + str(dates[i]) + " Confirmed")
                else:
                    logging.critical("% New File from Date " + str(dates[i]) + " Failed")
                    log.remove(self.build_remote_filename(merra2_collection, dates[i], params))
            logging.info("---- Download Finished ----")
        np.save(log_file, np.array(log))


    def merge_variables(
        self,
        path_data: Union[str, Path],
        collection_names: List[str],
        initial_year: int,
        final_year: int,
        initial_month: int,
        final_month: int,
        initial_day: int,
        final_day: int,

    ):
        if not isinstance(path_data, Path):
            path_data = Path(path_data)

        logging.info("---- Begin Merging In Variables ----")
        for date in self.iter_days(datetime.date(initial_year, initial_month, initial_day), datetime.date(final_year, final_month, final_day)):
            search_str = "*{0}.nc4.nc".format(str(date).replace('-', ''))
            nc_files = [str(f) for f in path_data.rglob(search_str)]
            nc_files.sort()
            if len(nc_files) == 0:
                logging.info("* Skipping Data In {0}".format(date))
                continue

            logging.info("* Processing Data In {0}".format(date))

            final_ds = xr.Dataset()

            collections = []
            # a connection/file for each repository
            for name in nc_files:
                logging.info("% Merging Data For {0}".format(os.path.split(name)[1]))
                var = os.path.split(name)[1].split('_')[3]
                if var not in collections:
                    collections.append(var)
                remote_ds = xr.open_dataset(name)
                # subset to desired variables and merge
                final_ds = xr.merge([final_ds, remote_ds])

            collections.sort()
            # save final dataset to netCDF
            file_name_str = "{0}_merra2_reanalysis_{1}.nc".format('-'.join(collections), date)
            filename = os.path.join(path_data, file_name_str)

            encoding = {v: {'zlib': True, 'complevel': 4} for v in final_ds.data_vars}
            logging.info("- Saving Data For {0}".format(date))
            final_ds.to_netcdf(filename, encoding=encoding)
            logging.info("# Deleting Redundant Files...")
            for name in nc_files:
                try:
                    os.remove(name)
                except OSError as err:
                    logging.error("OSError: {0} {1}".format(os.path.split(name)[1], err))

            logging.info("- Finished Deleting Redundant Files...")

        logging.info("---- Finish Merging In Variables ----")



    def daily_netcdf(
        self,
        path_data: Union[str, Path],
        output_file: Union[str, Path],
        collection_name: str,
        initial_year: int,
        final_year: int,
        merra2_var_dict: Optional[dict] = None,
    ):
        """MERRA2 daily NetCDF.

        Parameters
        ----------
        path_data : Union[str, Path]
        output_file : Union[str, Path]
        collection_name : str
        initial_year : int
        final_year : int
        merra2_var_dict : Optional[dict]
            Dictionary containing the following keys:
            esdt_dir, collection, var_name, standard_name,
            see the Bosilovich paper for details.

        """
        if not isinstance(path_data, Path):
            path_data = Path(path_data)

        log_file = os.path.join(path_data, 'index.npy')
        if os.path.exists(log_file):
            log = np.load(log_file).tolist()
        else:
            log = []

        if not merra2_var_dict:
            merra2_var_dict = var_list[collection_name]

        logging.info("---- Begin Merging In Time ----")
        if merra2_var_dict["collection"].startswith("const"):
            search_str = "*{0}*.nc4".format(merra2_var_dict["collection"])
            nc_files = [str(f) for f in path_data.rglob(search_str)]
            for f in nc_files:
                shutil.copy(f, path_data.parent)
            return

        logging.info("* Searching For Files To Merge...")
        search_str = "*{0}*.nc4*".format(merra2_var_dict["collection"])
        nc_files = [str(f) for f in path_data.rglob(search_str)]
        nc_files = list(filter(lambda a: a not in log, nc_files))
        for name in nc_files:
            log.append(name)
        if os.path.exists(output_file) and len(os.listdir(path_data)) != 0:
            shutil.copy(output_file, path_data)
            filepath, filename = os.path.split(output_file)
            nc_files.append(os.path.join(path_data, filename))
        nc_files.sort()
        logging.info("- Find Files [{0}] To Merge...".format(','.join([os.path.split(name)[1] for name in nc_files])))

        logging.info("* Processing Headers...")
        relevant_files = []
        divided_files = []
        nt_division = [0]
        nt = 0
        nmb = 0
        for nc_file in nc_files:
            try:
                yyyy = int(nc_file.split(".")[-2][0:4])
            except ValueError:
                try:
                    yyyy = int(nc_file.split(".")[-2][-4:])
                except ValueError:
                    yyyy = int(nc_file.split(".")[-3][0:4])
            if (yyyy >= initial_year) and (yyyy <= final_year):
                relevant_files.append(nc_file)
                nc = netCDF4.Dataset(nc_file, "r")
                divided_files.append(nc_file)
                nt += len(nc.dimensions["time"])
                nc.close()

        if len(relevant_files) == 0:
            logging.info(str(merra2_var_dict["var_name"]) + " data files have been downloaded and merged for " + collection_name + ".")
            return
        nc_reference = netCDF4.Dataset(relevant_files[0], "r")

        if isinstance(merra2_var_dict["var_name"], list):
            var_ref = {}
            for name in merra2_var_dict["var_name"]:
                var_ref[name] = nc_reference.variables[name]
        else:
            var_ref = nc_reference.variables[merra2_var_dict["var_name"]]
        nc_file = output_file
        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        nc1 = netCDF4.Dataset(nc_file, "w", format="NETCDF4_CLASSIC")
        nc1.Conventions = "CF-1.7"
        nc1.title = (
            "Modern-Era Retrospective analysis for Research and " "Applications, Version 2"
        )
        if (len(divided_files) == 1) and (len(divided_files[0]) == 1):
            try:
                nc1.history = (
                    "{0}\n{1}: " "Reformat to CF-1.7 & " "Extract variable."
                ).format(nc_reference.History, now)
            except AttributeError:
                nc1.history = (
                    "{0}: " "Reformat to CF-1.7 & " "Extract variable."
                ).format(now)

        else:
            try:
                nc1.history = (
                    "{0}\n{1}: "
                    "Reformat to CF-1.7 & "
                    "Extract variable & "
                    "Merge in time."
                ).format(nc_reference.History, now)
            except AttributeError:
                nc1.history = (
                    "{0}: "
                    "Reformat to CF-1.7 & "
                    "Extract variable & "
                    "Merge in time."
                ).format(now)
        try:
            nc1.institution = nc_reference.Institution
            nc1.references = nc_reference.References
        except AttributeError:
            pass
        nc1.source = "Reanalysis"

        attr_overwrite = ["conventions", "title", "institution", "source", "references"]
        ordered_attr = {}
        for attr in nc_reference.ncattrs():
            if attr == "History":
                continue
            if attr.lower() in attr_overwrite:
                ordered_attr["original_file_" + attr] = getattr(nc_reference, attr)
            else:
                ordered_attr[attr] = getattr(nc_reference, attr)
        for attr in sorted(ordered_attr.keys(), key=lambda v: v.lower()):
            setattr(nc1, attr, ordered_attr[attr])

        # Create netCDF dimensions
        nc1.createDimension("time", nt)
        # nc1.createDimension('ts', 6)
        # nc1.createDimension('level', k)
        nc1.createDimension("lat", len(nc_reference.dimensions["lat"]))
        nc1.createDimension("lon", len(nc_reference.dimensions["lon"]))

        time = nc1.createVariable("time", "i4", ("time",), zlib=True)
        time.axis = "T"
        time.units = "hours since 1980-01-01 00:00:00"
        time.long_name = "time"
        time.standard_name = "time"
        time.calendar = "gregorian"

        # level = nc1.createVariable('level','f4',('level',),zlib=True)
        # level.axis = 'Z'
        # level.units = 'Pa'
        # level.positive = 'up'
        # level.long_name = 'air_pressure'
        # level.standard_name = 'air_pressure'

        lat = nc1.createVariable("lat", "f4", ("lat",), zlib=True)
        lat.axis = "Y"
        lat.units = "degrees_north"
        lat.long_name = "latitude"
        lat.standard_name = "latitude"
        lat[:] = nc_reference.variables["lat"][:]

        lon = nc1.createVariable("lon", "f4", ("lon",), zlib=True)
        lon.axis = "X"
        lon.units = "degrees_east"
        lon.long_name = "longitude"
        lon.standard_name = "longitude"
        lon[:] = nc_reference.variables["lon"][:]

        least_digit = merra2_var_dict.get("least_significant_digit", None)

        if isinstance(merra2_var_dict["var_name"], list):
            var1 = {}
            for name in merra2_var_dict["var_name"]:
                var1[name] = nc1.createVariable(
                    name,
                    "f4",
                    ("time", "lat", "lon"),
                    zlib=True,
                    fill_value=self.deff4,
                    least_significant_digit=least_digit,
                )
                var1[name].units = var_ref[name].units
                var1[name].long_name = var_ref[name].long_name
                var1[name].standard_name = merra2_var_dict["standard_name"]
        else:
            var1 = nc1.createVariable(
                merra2_var_dict["var_name"],
                "f4",
                ("time", "lat", "lon"),
                zlib=True,
                fill_value=self.deff4,
                least_significant_digit=least_digit,
            )
            var1.units = var_ref.units
            var1.long_name = var_ref.long_name
            var1.standard_name = merra2_var_dict["standard_name"]

        nc_reference.close()

        logging.info("- Finished Creating Headers...")
        if isinstance(merra2_var_dict["var_name"], list):
            t = {}
            for name in merra2_var_dict["var_name"]:
                t[name] = 0
        else:
            t = 0
        for i, nc_file in enumerate(divided_files):
            logging.debug(nc_file)

            logging.info("% Merging Data {0}/{1}".format(i+1, len(divided_files)))
            nc = netCDF4.Dataset(nc_file, "r")
            if isinstance(merra2_var_dict["var_name"], list):
                ncvar = {}
                for name in merra2_var_dict["var_name"]:
                    ncvar[name] = nc.variables[name]
            else:
                ncvar = nc.variables[merra2_var_dict["var_name"]]
            nctime = nc.variables["time"]
            ncdatetime = netCDF4.num2date(nctime[:], nctime.units)
            nctime_1980 = np.round(netCDF4.date2num(ncdatetime, time.units))
            if isinstance(merra2_var_dict["var_name"], list):
                for name in merra2_var_dict["var_name"]:
                    var1[name][t[name] : t[name] + ncvar[name].shape[0], :, :] = ncvar[name][:, :, :]
                    time[t[name] : t[name] + ncvar[name].shape[0]] = nctime_1980[:]
                    t[name] += ncvar[name].shape[0]
            else:
                var1[t : t + ncvar.shape[0], :, :] = ncvar[:, :, :]
                time[t : t + ncvar.shape[0]] = nctime_1980[:]
                t += ncvar.shape[0]
            nc.close()

        logging.info("% Saving Data")
        nc1.close()

        np.save(log_file, np.array(log))
        logging.info("---- Finish Merging In Time ----")


    def daily_download_and_convert(
        self,
        collection_names: List[str],
        initial_year: int,
        final_year: Optional[int] = datetime.datetime.now().year,
        initial_month: int = 1,
        final_month: Optional[int] = datetime.datetime.now().month,
        initial_day: int = 1,
        final_day: Optional[int] = datetime.datetime.now().day,
        lat_1: Optional[float] = -90,
        lon_1: Optional[float] = -180,
        lat_2: Optional[float] = 90,
        lon_2: Optional[float] = 180,
        merra2_var_dicts: Optional[List[dict]] = None,
        output_dir: Union[str, Path] = None,
        auth: dict = None,
        delete_temp_dir: bool = True,
        thread_num: Optional[int] = 5,
    ):
        """MERRA2 daily download and conversion.

        Parameters
        ----------
        collection_names : List[str]
            Variable short names, must be defined in variables.py
            if merra2_var_dict is not provided. If more than one variable,
            they are assumed to have the same original files and those will only
            be downloaded once.
        initial_year : int
            Initial year for the data to be downloaded.
            Select from [1980, Now]
        final_year : int
            Final year for the data to be downloaded.
            Select from [1980, Now]
        initial_month : int
            Initial month for the data to be downloaded.
            Select from [1, 12]
        final_month : int
            Final month for the data to be downloaded.
            Select from [1, 12]
        initial_day : int
            Initial day for the data to be downloaded.
            Select from [1, 12]
        final_day : Optional[int]
            Final day for the data to be downloaded.
        lat_1 : Optional[float]
            Define the latitude of the left bottom corner of the rectangle region of interest.
            Select a value from [-90, +90]
        lon_1 : Optional[float]
            Define the longitude of the left bottom corner of the rectangle region of interest.
            Select a value from [-180, +180]
        lat_2 : Optional[float]
            Define the latitude of the right top corner of the rectangle region of interest.
            Select a value from [-90, +90]
        lon_2 : Optional[float]
            Define the longitude of the right top corner of the rectangle region of interest.
            Select a value from [-180, +180]
        merra2_var_dicts : Optional[List[dict]]
            Dictionary containing the following keys:
            esdt_dir, collection, var_name, standard_name,
            see the Bosilovich paper for details. Same order as collection_names.
        output_dir : Union[str, Path]
        auth : dict
            Dictionary contains login information.
            {"uid": "USERNAME", "password": "PASSWORD"}
        delete_temp_dir : bool
        thread_num : Optional[int]
            Number of Files to be downloaded simutanously.

        Notes
        ---------
        Leave final_* fields empty to download all data available from the given initial date till today.

        """
        if lat_1 > lat_2 or lon_1 > lon_2:
            raise RuntimeError("Illegal data area selected!")
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
        while self.global_retry:
            self.global_retry = False
            logging.info("Downloading data from {0}-{1}-{2} to {3}-{4}-{5}..."
                    .format(initial_year, initial_month, initial_day, final_year, final_month, final_day))
            if isinstance(output_dir, Path):
                output_dir = Path(output_dir)
            if output_dir is None:
                output_dir = Path.cwd()
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)

            # temp_dir_download = tempfile.mkdtemp(dir=output_dir)
            temp_dir_name = "{0}-{1}-{2}~{3}-{4}-{5} {6} [{7},{8}]~[{9},{10}]".format(initial_year, initial_month, initial_day, final_year, final_month, final_day,
                        '-'.join(collection_names), lat_1, lon_1, lat_2, lon_2)
            temp_dir_download = os.path.join(output_dir, temp_dir_name)
            try:
                os.mkdir(temp_dir_download)
            except OSError as err:
                if err.errno != errno.EEXIST:
                    raise err
                else:
                    logging.info("Request Already Exist in Download Directory, Adding More Files...")

            for i, collection_name in enumerate(collection_names):
                if not merra2_var_dicts:
                    merra2_var_dict = var_list[collection_name]
                else:
                    merra2_var_dict = merra2_var_dicts[i]
                # Download subdaily files
                # Translate the coordinates that define your area to grid coordinates.
                lat_coord_1 = self.translate_lat_to_geos5_native(lat_1)
                lon_coord_1 = self.translate_lon_to_geos5_native(lon_1)
                lat_coord_2 = self.translate_lat_to_geos5_native(lat_2)
                lon_coord_2 = self.translate_lon_to_geos5_native(lon_2)

                # Find the closest coordinate in the grid.
                lat_co_1_closest = self.find_closest_coordinate(lat_coord_1, self.lat_coords)
                lon_co_1_closest = self.find_closest_coordinate(lon_coord_1, self.lon_coords)
                lat_co_2_closest = self.find_closest_coordinate(lat_coord_2, self.lat_coords)
                lon_co_2_closest = self.find_closest_coordinate(lon_coord_2, self.lon_coords)

                requested_lat = '[{lat_1}:{lat_2}]'.format(
                        lat_1=lat_co_1_closest, lat_2=lat_co_2_closest
                    )
                requested_lon = '[{lon_1}:{lon_2}]'.format(
                        lon_1=lon_co_1_closest, lon_2=lon_co_2_closest
                    )

                if isinstance(merra2_var_dict['var_name'], list):
                    requested_params = merra2_var_dict['var_name']
                else:
                    requested_params = [merra2_var_dict['var_name']]

                if merra2_var_dict["collection"].startswith("const"):
                    requested_time = '[0:0]'
                else:
                    requested_time = '[0:23]'
                parameter = self.generate_url_params(requested_params, requested_time,
                                                        requested_lat, requested_lon)

                self.subdaily_universal_download(
                    merra2_var_dict,
                    initial_year,
                    final_year,
                    initial_month=initial_month,
                    final_month=final_month,
                    initial_day=initial_day,
                    final_day=final_day,
                    output_directory=temp_dir_download,
                    auth=auth,
                    params=parameter,
                    thread_num=thread_num,
                )
                # Name the output file
                if initial_year == final_year:
                    file_name_str = "{0}_{1}_merra2_reanalysis_{2}.nc"
                    out_file_name = file_name_str.format(collection_name, merra2_var_dict["esdt_dir"], str(initial_year))
                else:
                    file_name_str = "{0}_{1}_merra2_reanalysis_{2}-{3}.nc"
                    out_file_name = file_name_str.format(
                        collection_name, merra2_var_dict["esdt_dir"], str(initial_year), str(final_year)
                    )
                out_file = Path(output_dir).joinpath(out_file_name)
                # Extract variable
                self.daily_netcdf(
                    temp_dir_download,
                    out_file,
                    collection_name,
                    initial_year,
                    final_year,
                    merra2_var_dict
                )
            if delete_temp_dir:
                shutil.rmtree(temp_dir_download)
            else:
                self.merge_variables(
                        temp_dir_download,
                        collection_names,
                        initial_year,
                        final_year,
                        initial_month,
                        final_month,
                        initial_day,
                        final_day,
                )
            if self.global_retry:
                logging.error("Requested Data Partially Downloaded, Retry Downloading...(CTRL+C TO ABORT)")
