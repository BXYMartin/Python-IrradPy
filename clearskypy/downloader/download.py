import datetime
import _thread
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
from multiprocessing.pool import MaybeEncodingError
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


    def reconstruct_filename(self, name, params):
        return '{name}?{params}'.format(name=name, params=params)


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
                'MERRA2_{stream}.{abbrv}.{date}.nc4.{ext}'
                .format(stream=merra_stream,
                        abbrv=merra2_collection["collection"],
                        date=date_string, ext=file_extension)
            )


    def download_merra2_nc(self, date, merra2_collection, output_directory, params, auth):
        final_ds = xr.Dataset()

        # build url
        url = os.path.join(self.build_remote_url(merra2_collection, date),
                            self.build_remote_filename(merra2_collection, date, params))

        file_path = os.path.join(output_directory, DownloadManager.get_filename(url))
        if os.path.exists(file_path):
            logging.info("- Detected Duplicated File from Date " + str(date) + ", Deleting Existing File Before Downloading...")
            os.remove(file_path)
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
        while retry and limit < 1:
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
            except MaybeEncodingError as e:
                logging.error(log + ': Error in Serialize Results')
            except Exception as e:
                logging.error(log + ': ' + str(e))

        if retry:
            logging.critical("* File from Date " + str(date) + " Failed Download")
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


    def iter_months(self, first: datetime.date, last: datetime.date):
        ym_start= 12*first.year + first.month - 1
        ym_end= 12*last.year + last.month - 1
        for ym in range( ym_start, ym_end + 1 ):
            y, m = divmod( ym, 12 )
            ny, nm = divmod( ym + 1, 12  )
            for sub in self.iter_days(datetime.date(y, m+1, 1), datetime.date(ny, nm+1, 1) + datetime.timedelta(-1)):
                if sub not in self.iter_days(first, last):
                    logging.error("Missing File From Date {} To Merge Month {}!".format(sub, "{:0>4d}-{:0>2d}".format(y, m+1)))
            yield "{:0>4d}-{:0>2d}".format(y, m+1)


    def iter_years(self, first: datetime.date, last: datetime.date):
        for y in range( first.year, last.year + 1 ):
            for sub in self.iter_months(datetime.date(y, 1, 1), datetime.date(y, 12, 31)):
                if sub not in self.iter_months(first, last):
                    logging.error("Missing File From Date {} To Merge Year {}!".format(sub, "{:0>4d}".format(y)))
            yield "{:0>4d}".format(y)



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
        merge: str = "monthly",
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
        merge: str
        """
        if not isinstance(output_directory, Path):
            log_file = Path(output_directory)

        log_file = os.path.join(log_file.parent, 'index.npy')
        if os.path.exists(log_file):
            log = np.load(log_file).tolist()
        else:
            log = []
        for i, n in enumerate(log):
            if n.endswith('False'):
                log[i] = n.replace('False', merge)
            if n.endswith('True'):
                log[i] = n.replace('True', merge)
        logging.info("---- Begin Analysing Directory ----")
        for name in os.listdir(output_directory):
            if name.endswith('.nc4.nc') and merra2_collection["collection"] in name and self.reconstruct_filename(name, params) + str(merge) not in log:
                # Compatibility Check For Jamie
                intact = False
                try:
                    lat = xr.open_dataset(os.path.join(output_directory, name)).lat
                    lon = xr.open_dataset(os.path.join(output_directory, name)).lon
                    for value in lat:
                        if value != 0:
                            intact = True
                            break
                    for value in lon:
                        if value != 0:
                            intact = True
                            break
                except Exception:
                    intact = False
                if intact:
                    log.append(self.reconstruct_filename(name, params) + str(merge))
                    logging.info("- Found previous intact file " + self.reconstruct_filename(name, params))
                    np.save(log_file, np.array(log))
                else:
                    logging.error("* Found previous corrupted file " + self.reconstruct_filename(name, params) + ", Scheduled for redownload")
        logging.info("----  End Analysing Directory  ----")

        dates = []
        temp_log = []
        for date in self.iter_days(datetime.date(initial_year, initial_month, initial_day), datetime.date(final_year, final_month, final_day)):
            if self.build_remote_filename(merra2_collection, date, params) + str(merge) in temp_log or self.build_remote_filename(merra2_collection, date, params) + str(merge) in log:
                logging.info("Skipping existing file " + self.build_remote_filename(merra2_collection, date, params) + " from " + merra2_collection["esdt_dir"])
                continue
            else:
                temp_log.append(self.build_remote_filename(merra2_collection, date, params) + str(merge))
                logging.info("Preparing new file " + self.build_remote_filename(merra2_collection, date, params) + " from " + merra2_collection["esdt_dir"])
            dates.append(date)

        if len(dates) > 0:
            logging.info("----  Begin  Download  ----")
            time_start = None
            for start in range(0, len(dates), thread_num):
                end = min(start+thread_num, len(dates))
                if time_start is not None:
                    logging.info("~ %d Files Downloaded In %3.2f Seconds, %d Files Left, Expected %3.2f Minutes Remaining..." % (thread_num, time.time() - time_start, len(dates) - start, (len(dates) - start)/thread_num*(time.time() - time_start)/60))
                time_start = time.time()
                pool = multiprocessing.Pool(thread_num)
                rel = pool.map_async(
                        partial(self.download_merra2_nc,
                            merra2_collection=merra2_collection,
                            output_directory=output_directory,
                            params=params,
                            auth=auth,
                            ), dates[start:end]
                        ).get(0.5 * _thread.TIMEOUT_MAX)
                pool.close()
                pool.join()

                for i, success in enumerate(rel):
                    if success:
                        # Check integrity
                        name = self.build_remote_filename(merra2_collection, dates[start:end][i], None)
                        intact = False
                        try:
                            lat = xr.open_dataset(os.path.join(output_directory, name)).lat
                            lon = xr.open_dataset(os.path.join(output_directory, name)).lon
                            for value in lat:
                                if value != 0:
                                    intact = True
                                    break
                            for value in lon:
                                if value != 0:
                                    intact = True
                                    break
                        except Exception:
                            intact = False
                        if intact:
                            logging.info("% New File from Date " + str(dates[start:end][i]) + " Confirmed")
                            log.append(self.build_remote_filename(merra2_collection, dates[start:end][i], params) + str(merge))
                        else:
                            logging.critical("% New File from Date " + str(dates[start:end][i]) + " Integrity Check Failed")
                    else:
                        logging.critical("% New File from Date " + str(dates[start:end][i]) + " Failed")
                np.save(log_file, np.array(log))
            logging.info("---- Download Finished ----")


    def merge_variables_perday(
        self,
        path_data: Union[str, Path],
        collection_names: List[str],
        final_year: int,
        final_month: int,
        final_day: int,
        date: str,
    ):
        if not isinstance(path_data, Path):
            path_data = Path(path_data)

        log_file = os.path.join(path_data.parent, 'index.npy')
        if os.path.exists(log_file):
            log = np.load(log_file).tolist()
        else:
            log = []
        delete_set = []
        time_start = time.time()
        search_str = "*{0}.nc4.nc".format(str(date).replace('-', ''))
        nc_files = [str(f) for f in path_data.rglob(search_str)]
        nc_files.sort()
        if len(nc_files) == 0:
            logging.info("* Skipping Data In {0}".format(date))
            return delete_set
        logging.info("* Processing Data In {0}...".format(date))

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
            try:
                final_ds = xr.merge([final_ds, remote_ds])
            except ValueError:
                logging.error("Corrupted File {0} Detected, Aborting and Redownloading...".format(os.path.split(name)[1]))
                for line in reversed(log):
                    if line.startswith(os.path.split(name)[1]):
                        log.remove(line)
                        logging.info("Removed Logs For {0}".format(line))
                np.save(log_file, np.array(log))
                raise RuntimeError

            remote_ds.close()

        if len(collections) != len(collection_names):
            logging.error("{0} Collection(s) Required, {1} Collection(s) Collected for {2}, Please Redownload Again!".format(",".join(collection_names), ",".join(collections), date))
            raise RuntimeError("Partially Downloaded Collection On Date {0}!".format(date))
        collections.sort()
        # save final dataset to netCDF
        file_name_str = "{0}_merra2_reanalysis_{1}.nc".format('-'.join(collections), date)
        filename = os.path.join(path_data, file_name_str)

        encoding = {v: {'zlib': True, 'complevel': 4} for v in final_ds.data_vars}
        logging.info("- Saving Data For {0}".format(date))
        final_ds.to_netcdf(filename, encoding=encoding)
        final_ds.close()
        logging.info("# Logging Redundant Files...")
        for name in nc_files:
            delete_set.append(name)

        logging.info("- Finished Logging Redundant Files...")

        logging.info("* File From Date {} Finished Daily Merge in {:.2f} seconds, {} Left, Estimated {:.2f} Minutes Remaining...".format(date, time.time() - time_start, (datetime.date(final_year, final_month, final_day) - date).days, (datetime.date(final_year, final_month, final_day) - date).days * (time.time() - time_start)/60))

        return delete_set

    def merge_variables_permonth(
        self,
        path_data: Union[str, Path],
        collection_names: List[str],
        final_year: int,
        final_month: int,
        final_day: int,
        date: str,
    ):
        if not isinstance(path_data, Path):
            path_data = Path(path_data)
        time_start = time.time()
        delete_set = []
        search_str = "*{0}-*.nc".format(date)
        nc_files = [str(f) for f in path_data.rglob(search_str)]
        nc_files.sort()
        if len(nc_files) == 0:
            logging.info("* Skipping Data In {0}".format(date))
            return delete_set

        logging.info("* Processing Data In {0}".format(date))

        final_ds = xr.open_dataset(nc_files[0])

        collections = os.path.split(nc_files[0])[1].split('_')[0]
        # a connection/file for each repository
        for name in nc_files[1:]:
            logging.info("% Merging Data For {0}".format(os.path.split(name)[1]))
            var = os.path.split(name)[1].split('_')[0]
            if collections is None or len(collections) > len(var):
                collections = var
            remote_ds = xr.open_dataset(name)
            # subset to desired variables and merge
            final_ds = xr.concat([final_ds, remote_ds], dim="time")
            remote_ds.close()

        # save final dataset to netCDF
        file_name_str = "{0}_merra2_reanalysis_{1}.nc".format(collections, date)
        filename = os.path.join(path_data, file_name_str)

        encoding = {v: {'zlib': True, 'complevel': 4} for v in final_ds.data_vars}
        logging.info("- Saving Data For {0}".format(date))
        final_ds.to_netcdf(filename, encoding=encoding)
        final_ds.close()
        logging.info("# Logging Redundant Files...")
        for name in nc_files:
            delete_set.append(name)

        logging.info("- Finished Logging Redundant Files...")

        remaining_month = (int(final_year) - int(date.split('-')[0])) * 12 + int(final_month) - int(date.split('-')[1])
        logging.info("* File From Date {} Finished Monthly Merge in {:.2f} seconds, {} Left, Estimated {:.2f} Minutes Remaining...".format(date, time.time() - time_start, remaining_month, remaining_month * (time.time() - time_start)/60))
        return delete_set

    def merge_variables_peryear(
        self,
        path_data: Union[str, Path],
        collection_names: List[str],
        final_year: int,
        final_month: int,
        final_day: int,
        date: str,
    ):
        if not isinstance(path_data, Path):
            path_data = Path(path_data)
        time_start = time.time()
        delete_set = []
        search_str = "*{0}-*.nc".format(date)
        nc_files = [str(f) for f in path_data.rglob(search_str)]
        nc_files.sort()
        if len(nc_files) == 0:
            logging.info("* Skipping Data In {0}".format(date))
            return delete_set

        logging.info("* Processing Data In {0}".format(date))

        final_ds = xr.open_dataset(nc_files[0])

        collections = os.path.split(nc_files[0])[1].split('_')[0]
        # a connection/file for each repository
        for name in nc_files[1:]:
            logging.info("% Merging Data For {0}".format(os.path.split(name)[1]))
            var = os.path.split(name)[1].split('_')[0]
            if collections is None or len(collections) > len(var):
                collections = var
            remote_ds = xr.open_dataset(name)
            # subset to desired variables and merge
            final_ds = xr.concat([final_ds, remote_ds], dim="time")
            remote_ds.close()

        # save final dataset to netCDF
        file_name_str = "{0}_merra2_reanalysis_{1}.nc".format(collections, date)
        filename = os.path.join(path_data, file_name_str)

        encoding = {v: {'zlib': True, 'complevel': 4} for v in final_ds.data_vars}
        logging.info("- Saving Data For {0}".format(date))
        final_ds.to_netcdf(filename, encoding=encoding)
        final_ds.close()
        logging.info("# Logging Redundant Files...")
        for name in nc_files:
            delete_set.append(name)

        logging.info("- Finished Logging Redundant Files...")

        remaining_year = int(final_year) - int(date)
        logging.info("* File From Date {} Finished Yearly Merge in {:.2f} seconds, {} Left, Estimated {:.2f} Minutes Remaining...".format(date, time.time() - time_start, remaining_year, remaining_year * (time.time() - time_start)/60))
        return delete_set

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
        merge_timelapse: str = 'monthly',
        merge: bool = True,
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
        merge_timelapse : str
            Define the timelapse of the merge
            Select from ['none', 'daily', 'monthly', 'yearly']
        thread_num : Optional[int]
            Number of Files to be downloaded simutanously.

        Notes
        ---------
        Leave final_* fields empty to download all data available from the given initial date till today.

        """
        if lat_1 > lat_2 or lon_1 > lon_2:
            raise RuntimeError("Illegal data area selected!")
        if merge_timelapse not in ['none', 'daily', 'monthly', 'yearly']:
            raise RuntimeError("Illegal merge timelapse given, select from ['none', 'daily', 'monthly', 'yearly']!")
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
                    merge=merge_timelapse,
                )
            merge_collection_names = []
            for i, collection_name in enumerate(collection_names):
                if not merra2_var_dicts:
                    merra2_var_dict = var_list[collection_name]
                else:
                    merra2_var_dict = merra2_var_dicts[i]
                if not merra2_var_dict["collection"].startswith("const"):
                    merge_collection_names.append(collection_name)

            try:
                if merge_timelapse == 'daily' or merge_timelapse == 'monthly' or merge_timelapse == 'yearly':
                    logging.info("---- Begin Merging In Daily Variables ----")
                    for date in self.iter_days(datetime.date(initial_year, initial_month, initial_day), datetime.date(final_year, final_month, final_day)):
                        delete_set = self.merge_variables_perday(
                            temp_dir_download,
                            merge_collection_names,
                            final_year,
                            final_month,
                            final_day,
                            date,
                        )
                        logging.info("# Deleting Daily Redundant Files...")
                        for name in delete_set:
                            while True:
                                try:
                                    os.remove(name)
                                    break
                                except OSError as err:
                                    logging.error("OSError: {0} {1}, Retrying...".format(os.path.split(name)[1], err))
                                    time.sleep(20)
                        logging.info("# Finished Deleting Daily Redundant Files...")
                    logging.info("---- Finish Merging In Daily Variables ----")


                if merge_timelapse == 'monthly' or merge_timelapse == 'yearly':
                    logging.info("---- Begin Merging In Monthly Variables ----")

                    for date in self.iter_months(datetime.date(initial_year, initial_month, initial_day), datetime.date(final_year, final_month, final_day)):
                        delete_set = self.merge_variables_permonth(
                            temp_dir_download,
                            merge_collection_names,
                            final_year,
                            final_month,
                            final_day,
                            date,
                        )
                        logging.info("# Deleting Merged Daily Redundant Files...")
                        for name in delete_set:
                            while True:
                                try:
                                    os.remove(name)
                                    break
                                except OSError as err:
                                    logging.error("OSError: {0} {1}, Retrying...".format(os.path.split(name)[1], err))
                                    time.sleep(20)
                        logging.info("# Finished Deleting Merged Daily Redundant Files...")
                    logging.info("---- Finish Merging In Monthly Variables ----")


                if merge_timelapse == 'yearly':
                    logging.info("---- Begin Merging In Yearly Variables ----")

                    for date in self.iter_years(datetime.date(initial_year, initial_month, initial_day), datetime.date(final_year, final_month, final_day)):
                        delete_set = self.merge_variables_peryear(
                            temp_dir_download,
                            merge_collection_names,
                            final_year,
                            final_month,
                            final_day,
                            date,
                        )
                        logging.info("# Deleting Merged Monthly Redundant Files...")
                        for name in delete_set:
                            while True:
                                try:
                                    os.remove(name)
                                    break
                                except OSError as err:
                                    logging.error("OSError: {0} {1}, Retrying...".format(os.path.split(name)[1], err))
                                    time.sleep(20)
                        logging.info("# Finished Deleting Merged Monthly Redundant Files...")
                    logging.info("---- Finish Merging In Yearly Variables ----")
            except RuntimeError:
                self.global_retry = True

            if self.global_retry:
                logging.error("Requested Data Partially Downloaded, Retry Downloading...(CTRL+C TO ABORT)")
