import os
import sys
import tempfile
import argparse
import datetime
from typing import List
from typing import Optional
from typing import Union
from pathlib import Path
from . import download

def parse_args():
    desc = "Downloader Setup for GESDISC System"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--var_names', type=str2list, default=['rad', 'slv', 'aer'], help='Select from ["rad", "slv", "aer"], predefined in downloader.variables.var_list')
    parser.add_argument('--delete_temp', type=str2bool, default=True, help='Select from [True, False], option to delete or save original downloaded files.')
    parser.add_argument('--download_dir', type=str, default=os.path.join(os.getcwd(), "MERRA2_data"), help='Set the download path for all files, default value is ' + os.path.join(os.getcwd(), "MERRA2_data") + '.')

    parser.add_argument('--initial_year', type=int, default=(datetime.date.today() + datetime.timedelta(-1)).year, help='Select from [1980, This Year], default to the year of now.')
    parser.add_argument('--initial_month', type=int, default=(datetime.date.today() + datetime.timedelta(-1)).month, help='Select from [1, 12], default to the month of now.')
    parser.add_argument('--initial_day', type=int, default=(datetime.date.today() + datetime.timedelta(-1)).day, help='Select from [1, Total days of the Month Selected], default to yesterday.')
    parser.add_argument('--final_year', type=int, default=(datetime.date.today() + datetime.timedelta(-1)).year, help='Select from [initial_year, This Year], default to the year of now.')
    parser.add_argument('--final_month', type=int, default=(datetime.date.today() + datetime.timedelta(-1)).month, help='Select from [1, 12], default to the month of now.')
    parser.add_argument('--final_day', type=int, default=(datetime.date.today() + datetime.timedelta(-1)).day, help='Select from [1, Total days of the Month Selected], default to yesterday.')
    parser.add_argument('--uid', type=str, required=True, help='Username for GESDISC authentication.')
    parser.add_argument('--password', type=str, help='Password for GESDISC authentication.')

    parser.add_argument('--bottom_left_lat', type=float, default=-90, help='Select from [-90, +90], default to -90. This is the latitude of the left bottom corner of the interest data region (which is a rectangle).')
    parser.add_argument('--bottom_left_lon', type=float, default=-180, help='Select from [-180, +180], default to -180. This is the longitude of the left bottom corner of the interest data region (which is a rectangle).')
    parser.add_argument('--top_right_lat', type=float, default=90, help='Select from [-90, +90], default to 90. This is the latitude of the top right corner of the interest data region (which is a rectangle).')
    parser.add_argument('--top_right_lon', type=float, default=180, help='Select from [-180, +180], default to 180. This is the longitude of the top right corner of the interest data region (which is a rectangle).')
    return check_args(parser.parse_args())


def run(
    var_names: Optional[List[str]] = ['rad', 'slv', 'aer'],
    initial_year: Optional[int] = (datetime.date.today() + datetime.timedelta(-1)).year,
    final_year: Optional[int] = (datetime.date.today() + datetime.timedelta(-1)).year,
    initial_month: Optional[int] = (datetime.date.today() + datetime.timedelta(-1)).month,
    final_month: Optional[int] = (datetime.date.today() + datetime.timedelta(-1)).month,
    initial_day: Optional[int] = (datetime.date.today() + datetime.timedelta(-1)).day,
    final_day: Optional[int] = (datetime.date.today() + datetime.timedelta(-1)).day,
    lat_1: Optional[float] = -90,
    lon_1: Optional[float] = -180,
    lat_2: Optional[float] = 90,
    lon_2: Optional[float] = 180,
    merra2_var_dicts: Optional[List[dict]] = None,
    output_dir: Optional[Union[str, Path]] = os.path.join(os.getcwd(), "MERRA2_data"),
    auth: dict = None,
    delete_temp_dir: bool = True,
    verbose: bool = True,
    ):
    """MERRA2 daily download and merge function for the Clear Sky Model.

    Parameters
    ----------
    var_names : List[str]
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
        esdt_dir, collection, merra_name, standard_name,
        see the Bosilovich paper for details. Same order as var_names.
    output_dir : Union[str, Path]
    auth : dict
        Dictionary contains login information.
        {"uid": "USERNAME", "password": "PASSWORD"}
    delete_temp_dir : bool
    verbose : bool

    Notes
    ---------
    Leave final_* fields empty to download all data available from the given initial date till yesterday.

    """

    if auth is None:
        print('You must provide GESDISC authentication information using parameter auth={"uid": "USERNAME", "password": "PASSWORD"} to proceed, aborting...')
        return

    # Call the main function
    download.daily_download_and_convert(
        var_names, merra2_var_dicts=None,
        initial_year=initial_year, initial_month=initial_month, initial_day=initial_day,
        final_year=final_year, final_month=final_month, final_day=final_day,
        output_dir=output_dir,
        auth=auth,
        delete_temp_dir=delete_temp_dir,
        lat_1=lat_1, lon_1=lon_1,
        lat_2=lat_2, lon_2=lon_2)


def main():
    # Parse Arguments from Command Line
    args = parse_args()

    # Check If Arguments are Valid
    if args is None:
      exit()

    print("Connecting Database...")

    download.daily_download_and_convert(
        args.var_names, merra2_var_dicts=None,
        initial_year=args.initial_year, initial_month=args.initial_month, initial_day=args.initial_day,
        final_year=args.final_year, final_month=args.final_month, final_day=args.final_day,
        output_dir=args.download_dir,
        auth={'uid': args.uid, 'password': args.password},
        delete_temp_dir=args.delete_temp,
        lat_1=args.bottom_left_lat, lon_1=args.bottom_left_lon,
        lat_2=args.top_right_lat, lon_2=args.top_right_lon)

    print("Download and Merge Complete, merged data file available in " + args.download_dir)



if __name__ == "__main__":
    main()
