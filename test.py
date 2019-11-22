import fnmatch
import glob
import os
import shutil
import sys
import tempfile
import download


def test_daily_download_convert():
    # var_names you want to download, links defined in variables.py
    var_names = ['rad', 'slv', 'aer']
    # whether to delete the temporary download directory (along with the original data)
    delete_temp_dir = False
    # define your desired download directory
    download_dir = os.path.join(os.getcwd(), "MERRA2_data")
    # add your username and password
    GESDISC_AUTH = {
        'uid': 'USERNAME',
        'password': 'PASSWORD',
    }
    # call the main function
    download.daily_download_and_convert(
        var_names, merra2_var_dicts=None, initial_year=2015,
        final_year=2015, initial_month=1, final_month=1, initial_day=1,
        final_day=1, output_dir=download_dir,
        auth=GESDISC_AUTH,
        delete_temp_dir=delete_temp_dir,
        lat_1=-11, lon_1=-22, lat_2=22, lon_2=33)


if __name__ == "__main__":
    test_daily_download_convert()
