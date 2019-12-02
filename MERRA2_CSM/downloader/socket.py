import os
import sys
import tempfile
from . import download


def run():
    # var_names you want to download, links defined in variables.py
    var_names = ['rad', 'slv', 'aer']
    # whether to delete the temporary download directory (along with the original data)
    delete_temp_dir = False
    # define your desired download directory
    download_dir = os.path.join(os.getcwd(), "MERRA2_data")
    # define interest region
    left_bottom_coord = [-11, -22]
    right_top_coord = [11, 22]
    # define time period
    initial_year = 2015
    initial_month = 11
    initial_day = 1
    # add your username and password
    GESDISC_AUTH = {
        'uid': 'USERNAME',
        'password': 'PASSWORD',
    }
    # call the main function
    download.daily_download_and_convert(
        var_names, merra2_var_dicts=None,
        initial_year=initial_year, initial_month=initial_month, initial_day=initial_day,
        output_dir=download_dir,
        auth=GESDISC_AUTH,
        delete_temp_dir=delete_temp_dir,
        lat_1=left_bottom_coord[0], lon_1=left_bottom_coord[1],
        lat_2=right_top_coord[0], lon_2=right_top_coord[1])


if __name__ == "__main__":
    run()
