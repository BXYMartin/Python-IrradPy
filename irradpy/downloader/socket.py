import os
import sys
import tempfile
import argparse
import datetime
import multiprocessing
from typing import List
from typing import Optional
from typing import Union
from pathlib import Path
from .download import SocketManager


def parse_args():
    desc = "Downloader Setup for GESDISC System"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--uid', type=str, required=True, help='Username for GESDISC authentication.')
    parser.add_argument('--password', type=str, required=True, help='Password for GESDISC authentication.')
    parser.add_argument('--collection_names', type=list, default=['rad', 'slv', 'aer', 'asm'], help='Select from ["rad", "slv", "aer", "asm"], predefined in downloader.variables.var_list')
    parser.add_argument('--merge_timelapse', type=str, default='monthly', help='Select from [none, daily, monthly, yearly], option to merge original downloaded files into yearly files.')
    parser.add_argument('--download_dir', type=str, default=os.path.join(os.getcwd(), "MERRA2_data"), help='Set the download path for all files, default value is ' + os.path.join(os.getcwd(), "MERRA2_data") + '.')

    parser.add_argument('--initial_year', type=int, default=(datetime.date.today() + datetime.timedelta(-60)).year, help='Select from [1980, This Year], default to the year of now.')
    parser.add_argument('--initial_month', type=int, default=(datetime.date.today() + datetime.timedelta(-60)).month, help='Select from [1, 12], default to the month of now.')
    parser.add_argument('--initial_day', type=int, default=(datetime.date.today() + datetime.timedelta(-60)).day, help='Select from [1, Total days of the Month Selected], default to yesterday.')
    parser.add_argument('--final_year', type=int, default=(datetime.date.today() + datetime.timedelta(-60)).year, help='Select from [initial_year, This Year], default to the year of now.')
    parser.add_argument('--final_month', type=int, default=(datetime.date.today() + datetime.timedelta(-60)).month, help='Select from [1, 12], default to the month of now.')
    parser.add_argument('--final_day', type=int, default=(datetime.date.today() + datetime.timedelta(-60)).day, help='Select from [1, Total days of the Month Selected], default to yesterday.')

    parser.add_argument('--bottom_left_lat', type=float, default=-90, help='Select from [-90, +90], default to -90. This is the latitude of the left bottom corner of the interest data region (which is a rectangle).')
    parser.add_argument('--bottom_left_lon', type=float, default=-180, help='Select from [-180, +180], default to -180. This is the longitude of the left bottom corner of the interest data region (which is a rectangle).')
    parser.add_argument('--top_right_lat', type=float, default=90, help='Select from [-90, +90], default to 90. This is the latitude of the top right corner of the interest data region (which is a rectangle).')
    parser.add_argument('--top_right_lon', type=float, default=180, help='Select from [-180, +180], default to 180. This is the longitude of the top right corner of the interest data region (which is a rectangle).')
    parser.add_argument('--thread_num', type=int, default=5, help='Specify how many files to be downloaded simutaneously, recommend assign no greater than the number of threads in your CPU.')
    return check_args(parser.parse_args())

def check_args(args):
    # TODO: Add essential checks for input args
    return args


def run(
    collection_names: Optional[List[str]] = ['rad', 'slv', 'aer', 'asm'],
    initial_year: Optional[int] = (datetime.date.today() + datetime.timedelta(-60)).year,
    final_year: Optional[int] = (datetime.date.today() + datetime.timedelta(-60)).year,
    initial_month: Optional[int] = (datetime.date.today() + datetime.timedelta(-60)).month,
    final_month: Optional[int] = (datetime.date.today() + datetime.timedelta(-60)).month,
    initial_day: Optional[int] = (datetime.date.today() + datetime.timedelta(-60)).day,
    final_day: Optional[int] = (datetime.date.today() + datetime.timedelta(-60)).day,
    lat_1: Optional[float] = -90,
    lon_1: Optional[float] = -180,
    lat_2: Optional[float] = 90,
    lon_2: Optional[float] = 180,
    merra2_var_dicts: Optional[List[dict]] = None,
    output_dir: Optional[Union[str, Path]] = os.path.join(os.getcwd(), "MERRA2_data"),
    auth: dict = None,
    merge_timelapse: str = 'monthly',
    thread_num: Optional[int] = 5,
    ):
    """MERRA2 daily download and merge function for the Clear Sky Model.

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
    thread_num : Optional[int]
        Number of Files to be downloaded simutanously.

    Notes
    ---------
    Leave final_* fields empty to download all data available from the given initial date till yesterday.

    """

    if auth is None:
        print('You must provide GESDISC authentication information using parameter auth={"uid": "USERNAME", "password": "PASSWORD"} to proceed, aborting...')
        return

    # Call the main function
    socket = SocketManager()
    socket.daily_download_and_convert(
        collection_names, merra2_var_dicts=merra2_var_dicts,
        initial_year=initial_year, initial_month=initial_month, initial_day=initial_day,
        final_year=final_year, final_month=final_month, final_day=final_day,
        output_dir=output_dir,
        auth=auth,
        merge_timelapse=merge_timelapse,
        lat_1=lat_1, lon_1=lon_1,
        lat_2=lat_2, lon_2=lon_2,
        thread_num=thread_num,
        )


def main():
    # Parse Arguments from Command Line
    args = parse_args()

    # Check If Arguments are Valid
    if args is None:
        exit()

    socket = SocketManager()

    socket.daily_download_and_convert(
        args.collection_names, merra2_var_dicts=None,
        initial_year=args.initial_year, initial_month=args.initial_month, initial_day=args.initial_day,
        final_year=args.final_year, final_month=args.final_month, final_day=args.final_day,
        output_dir=args.download_dir,
        auth={'uid': args.uid, 'password': args.password},
        merge_timelapse=args.merge_timelapse,
        lat_1=args.bottom_left_lat, lon_1=args.bottom_left_lon,
        lat_2=args.top_right_lat, lon_2=args.top_right_lon,
        thread_num=args.thread_num)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
