import fnmatch
import glob
import os
import shutil
import sys
import tempfile
import download


def test_daily_download_convert():
    var_names = ['tasmax']
    delete_temp_dir = True
    download_dir = os.path.join(os.getcwd(), "resources")
    merra2_server = 'https://goldsmr4.gesdisc.eosdis.nasa.gov/data/'

    download.daily_download_and_convert(
        merra2_server, var_names, merra2_var_dicts=None, initial_year=2015,
        final_year=2015, initial_month=1, final_month=1, initial_day=1,
        final_day=1, output_dir=download_dir,
        delete_temp_dir=delete_temp_dir)


if __name__ == "__main__":
    test_daily_download_convert()
