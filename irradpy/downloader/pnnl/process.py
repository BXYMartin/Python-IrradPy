import datetime
import _thread
from pydap.client import open_url
from pydap.cas.urs import setup_session
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
from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed
from calendar import monthrange
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union


class SocketManager:
    def daily_universal_download(
        self,
        merra2_collection: str,
        initial_year: int,
        final_year: int,
        initial_month: int = 1,
        final_month: int = 12,
        params: Optional[str] = None,
        output_directory: Union[str, Path] = None,
        thread_num: int = 5,
        merge: str = "monthly",
    ):
        pass

    def merge(
        self,
        path_data: Union[str, Path],
        date: str,
    ):
        if not isinstance(path_data, Path):
            path_data = Path(path_data)
        delete_set = []
        search_str = "*{0}*.nc".format(date)
        nc_files = [str(f) for f in path_data.rglob(search_str)]
        nc_files.sort()
        if len(nc_files) == 0:
            logging.info("* Skipping Data In {0}".format(date))

        logging.info("* Processing Data In {0}".format(date))

        final_ds = xr.open_dataset(nc_files[0])

        # a connection/file for each repository
        for name in nc_files[1:]:
            logging.info("% Merging Data For {0}".format(os.path.split(name)[1]))
            remote_ds = xr.open_dataset(name)
            # subset to desired variables and merge
            final_ds = xr.concat([final_ds, remote_ds], dim="time")
            remote_ds.close()

        # save final dataset to netCDF
        file_name_str = "pnnl_reanalysis_{0}.nc".format(date)
        filename = os.path.join(path_data, file_name_str)

        encoding = {v: {'zlib': True, 'complevel': 4} for v in final_ds.data_vars}
        logging.info("- Saving Data For {0}".format(date))
        final_ds.to_netcdf(filename, encoding=encoding)
        final_ds.close()
        logging.info("# Logging Redundant Files...")
        for name in nc_files:
            delete_set.append(name)

        logging.info("- Finished Logging Redundant Files...")

        return delete_set

    def convert(
        self,
        data_dir: Union[str, Path] = 'PNNL_data',
        merge_timelapse: str = 'monthly',
    ):
        logging.getLogger().setLevel(logging.INFO)
        # Check Daily
        if merge_timelapse == "daily":
            logging.info("Skipping Merge Phase Because Of Daily Merge Request!")
            return
        # Check Date Range For All Data
        date_list = []
        for name in os.listdir(data_dir):
            if name.startswith('EPIC_SW_PAR_Hourly_'):
                if merge_timelapse == 'monthly' and name[19:25] not in date_list:
                    date_list.append(name[19:25])
        date_list.sort()
        for item in date_list:
            logging.info("Merging " + merge_timelapse + " for date " + item + "...")
            delete_set = self.merge(data_dir, item)
            for name in delete_set:
                while True:
                    try:
                        os.remove(name)
                        break
                    except OSError as err:
                        logging.error("OSError: {0} {1}, Retrying...".format(os.path.split(name)[1], err))
                        time.sleep(20)
            logging.info("# Finished Deleting Redundant Files...")
        logging.info("# Finished All")


